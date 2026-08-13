from __future__ import annotations

import discord

from games.bunker.player import BunkerPlayer
from games.bunker.cards import generate_character
from games.room_manager import room_manager


class BunkerGame:

    MAX_PLAYERS = 6
    WINNERS = 3

    def __init__(self, bot: discord.Client, room):
        self.bot = bot
        self.room = room

        self.players = [
            BunkerPlayer(user_id)
            for user_id in room.players
        ]

        self.started = False
        self.finished = False

        self.round = 0

        self.game_channel = None
        self.game_message = None

        self.phase = "waiting"

        self.votes: dict[int, int] = {}

    @property
    def alive_players(self):
        return [
            player
            for player in self.players
            if player.alive
        ]

    def get_player(self, user_id: int):
        for player in self.players:
            if player.user_id == user_id:
                return player

        return None

    # ==========================================================
    # ЗАПУСК
    # ==========================================================

    async def start(self):

        if len(self.players) != self.MAX_PLAYERS:
            raise ValueError(
                "Для Бункера необходимо ровно 6 игроков."
            )

        self.started = True
        self.finished = False
        self.round = 1

        print("========== BUNKER START ==========")

        self.give_characteristics()

        await self.send_characteristics()

        await self.create_game_message()

        await self.start_reveal_phase()

        print("========== BUNKER READY ==========")

    # ==========================================================
    # ХАРАКТЕРИСТИКИ
    # ==========================================================

    def give_characteristics(self):

        for player in self.players:

            data = generate_character()

            player.profession = data["profession"]
            player.health = data["health"]
            player.character = data["character"]
            player.baggage = data["baggage"]
            player.hobby = data["hobby"]
            player.special = data["special"]
            player.additional_info = data["additional_info"]

            player.revealed = []

            player.alive = True
            player.voted = False

    async def send_characteristics(self):

        for player in self.players:

            try:

                user = await self.bot.fetch_user(
                    player.user_id
                )

                await user.send(
                    self.build_private_card(player)
                )

            except discord.Forbidden:

                print(
                    f"[BUNKER] Не удалось отправить ЛС "
                    f"{player.user_id}"
                )

            except Exception as e:

                print(
                    f"[BUNKER] Ошибка отправки ЛС "
                    f"{player.user_id}: {e}"
                )

    def build_private_card(self, player):

        return (
            "🏚️ **Бункер — ваша карточка**\n\n"

            f"💼 **Профессия:** {player.profession}\n"
            f"❤️ **Здоровье:** {player.health}\n"
            f"🧠 **Характер:** {player.character}\n"
            f"🎒 **Багаж:** {player.baggage}\n"
            f"🎯 **Хобби:** {player.hobby}\n"
            f"🧬 **Особенность:** {player.special}\n"
            f"📚 **Дополнительно:** {player.additional_info}\n\n"

            "⚠️ Не показывайте эту информацию другим игрокам."
        )

    # ==========================================================
    # ИГРОВОЕ СООБЩЕНИЕ
    # ==========================================================

    async def create_game_message(self):

        if self.game_channel is None:
            return

        embed = self.build_game_embed()

        self.game_message = await self.game_channel.send(
            embed=embed,
            view=BunkerRevealView(self)
        )

    def build_game_embed(self):

        embed = discord.Embed(
            title="🏚️ БУНКЕР",
            color=discord.Color.dark_gold()
        )

        if self.phase == "reveal":

            description = (
                f"### 🔓 Раунд {self.round}\n\n"
                "Каждый живой игрок должен раскрыть "
                "**одну характеристику**.\n\n"
                "После этого начнётся голосование."
            )

        elif self.phase == "voting":

            description = (
                f"### 🗳 Раунд {self.round}\n\n"
                "Выберите игрока, которого хотите "
                "исключить из Бункера."
            )

        else:

            description = "Игра начинается..."

        embed.description = description

        players_text = []

        for player in self.players:

            if not player.alive:

                status = "❌ ВЫБЫЛ"

            else:

                status = "🟢 Жив"

            mention = f"<@{player.user_id}>"

            revealed_count = len(player.revealed)

            players_text.append(
                f"{mention} — {status} "
                f"• раскрыто: **{revealed_count}**"
            )

        embed.add_field(
            name=f"👥 Игроки ({len(self.alive_players)}/6)",
            value="\n".join(players_text),
            inline=False
        )

        embed.add_field(
            name="🏆 Условие победы",
            value="В Бункере должны остаться **3 игрока**.",
            inline=False
        )

        return embed

    async def update_game_message(self):

        if self.game_message is None:
            return

        await self.game_message.edit(
            embed=self.build_game_embed(),
            view=self.get_current_view()
        )

    def get_current_view(self):

        if self.phase == "reveal":
            return BunkerRevealView(self)

        if self.phase == "voting":
            return BunkerVoteView(self)

        return discord.ui.View()

    # ==========================================================
    # РАСКРЫТИЕ
    # ==========================================================

    async def start_reveal_phase(self):

        self.phase = "reveal"

        for player in self.players:
            player.revealed = []

        await self.update_game_message()

    async def reveal_characteristic(
        self,
        user_id: int,
        characteristic: str
    ):

        player = self.get_player(user_id)

        if player is None:
            return False, "Вы не участвуете в этой игре."

        if not player.alive:
            return False, "❌ Вы уже выбыли."

        if characteristic in player.revealed:
            return False, "❌ Вы уже раскрыли эту характеристику."

        value = getattr(player, characteristic, None)

        if value is None:
            return False, "❌ Такая характеристика не найдена."

        player.revealed.append(characteristic)

        await self.game_channel.send(
            f"🔓 <@{user_id}> раскрыл характеристику "
            f"**{self.characteristic_name(characteristic)}**:\n"
            f"> {value}"
        )

        if self.all_alive_revealed():

            await self.start_voting_phase()

        else:

            await self.update_game_message()

        return True, "Характеристика раскрыта."

    def all_alive_revealed(self):

        for player in self.alive_players:

            if len(player.revealed) == 0:
                return False

        return True

    def characteristic_name(self, key):

        names = {
            "profession": "💼 Профессия",
            "health": "❤️ Здоровье",
            "character": "🧠 Характер",
            "baggage": "🎒 Багаж",
            "hobby": "🎯 Хобби",
            "special": "🧬 Особенность",
            "additional_info": "📚 Дополнительно",
        }

        return names.get(key, key)

    # ==========================================================
    # ГОЛОСОВАНИЕ
    # ==========================================================

    async def start_voting_phase(self):

        self.phase = "voting"
        self.votes = {}

        for player in self.players:
            player.voted = False

        await self.game_channel.send(
            "🗳 **Голосование начинается!**\n\n"
            "Каждый живой игрок должен выбрать одного "
            "игрока для исключения."
        )

        await self.update_game_message()

    async def vote(
        self,
        voter_id: int,
        target_id: int
    ):

        voter = self.get_player(voter_id)
        target = self.get_player(target_id)

        if voter is None or target is None:
            return False, "Игрок не найден."

        if not voter.alive:
            return False, "❌ Вы выбыли."

        if not target.alive:
            return False, "❌ Этот игрок уже выбыл."

        if voter_id == target_id:
            return False, "❌ Нельзя голосовать за себя."

        if voter.voted:
            return False, "❌ Вы уже проголосовали."

        self.votes[voter_id] = target_id
        voter.voted = True

        await self.game_channel.send(
            f"🗳 <@{voter_id}> проголосовал."
        )

        if self.all_alive_voted():

            await self.finish_voting()

        else:

            await self.update_game_message()

        return True, "Голос принят."

    def all_alive_voted(self):

        for player in self.alive_players:

            if not player.voted:
                return False

        return True

    async def finish_voting(self):

        counts = {}

        for target_id in self.votes.values():

            counts[target_id] = counts.get(
                target_id,
                0
            ) + 1

        if not counts:
            return

        max_votes = max(counts.values())

        candidates = [
            player_id
            for player_id, votes in counts.items()
            if votes == max_votes
        ]

        # Если ничья — случайный выбор
        import random

        eliminated_id = random.choice(candidates)

        eliminated = self.get_player(
            eliminated_id
        )

        eliminated.kill()

        await self.game_channel.send(
            f"❌ **<@{eliminated_id}> выбывает из Бункера!**\n\n"
            f"Количество голосов: **{max_votes}**"
        )

        # Проверяем победу
        if len(self.alive_players) <= self.WINNERS:

            await self.finish_game()

            return

        self.round += 1

        await self.game_channel.send(
            f"🔄 Начинается **раунд {self.round}**."
        )

        await self.start_reveal_phase()

    # ==========================================================
    # ЗАВЕРШЕНИЕ
    # ==========================================================

    async def finish_game(self):

        self.finished = True
        self.started = False
        self.phase = "finished"

        winners = self.alive_players

        winner_text = "\n".join(
            f"🏆 <@{player.user_id}>"
            for player in winners
        )

        await self.game_channel.send(
            embed=discord.Embed(
                title="🏆 БУНКЕР ЗАВЕРШЁН!",
                description=(
                    "В Бункере осталось достаточно мест.\n\n"
                    "### Победители:\n"
                    f"{winner_text}"
                ),
                color=discord.Color.gold()
            )
        )

        # Удаляем комнату
        room_manager.delete_room(
            self.room.owner_id
        )


# ==============================================================
# VIEW — РАСКРЫТИЕ
# ==============================================================

class BunkerRevealView(discord.ui.View):

    def __init__(self, game: BunkerGame):

        super().__init__(timeout=None)

        self.game = game

    @discord.ui.button(
        label="🔓 Раскрыть характеристику",
        style=discord.ButtonStyle.primary
    )
    async def reveal(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        player = self.game.get_player(
            interaction.user.id
        )

        if player is None:

            await interaction.response.send_message(
                "❌ Вы не участвуете в этой игре.",
                ephemeral=True
            )

            return

        if not player.alive:

            await interaction.response.send_message(
                "❌ Вы уже выбыли.",
                ephemeral=True
            )

            return

        if len(player.revealed) > 0:

            await interaction.response.send_message(
                "❌ В этом раунде вы уже раскрыли характеристику.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            "Выберите характеристику:",
            view=BunkerRevealSelectView(self.game),
            ephemeral=True
        )


# ==============================================================
# SELECT — ХАРАКТЕРИСТИКА
# ==============================================================

class BunkerRevealSelectView(discord.ui.View):

    def __init__(self, game: BunkerGame):

        super().__init__(timeout=60)

        self.game = game

        self.add_item(
            BunkerCharacteristicSelect(game)
        )


class BunkerCharacteristicSelect(discord.ui.Select):

    def __init__(self, game: BunkerGame):

        self.game = game

        options = [
            discord.SelectOption(
                label="Профессия",
                emoji="💼",
                value="profession"
            ),
            discord.SelectOption(
                label="Здоровье",
                emoji="❤️",
                value="health"
            ),
            discord.SelectOption(
                label="Характер",
                emoji="🧠",
                value="character"
            ),
            discord.SelectOption(
                label="Багаж",
                emoji="🎒",
                value="baggage"
            ),
            discord.SelectOption(
                label="Хобби",
                emoji="🎯",
                value="hobby"
            ),
            discord.SelectOption(
                label="Особенность",
                emoji="🧬",
                value="special"
            ),
            discord.SelectOption(
                label="Дополнительно",
                emoji="📚",
                value="additional_info"
            )
        ]

        super().__init__(
            placeholder="Выберите характеристику",
            options=options
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        success, message = await self.game.reveal_characteristic(
            interaction.user.id,
            self.values[0]
        )

        await interaction.response.send_message(
            "✅ " + message if success else message,
            ephemeral=True
        )


# ==============================================================
# VIEW — ГОЛОСОВАНИЕ
# ==============================================================

class BunkerVoteView(discord.ui.View):

    def __init__(self, game: BunkerGame):

        super().__init__(timeout=None)

        self.game = game

        self.add_item(
            BunkerVoteSelect(game)
        )


class BunkerVoteSelect(discord.ui.Select):

    def __init__(self, game: BunkerGame):

        self.game = game

        options = []

        for player in game.alive_players:

            options.append(
                discord.SelectOption(
                    label=f"Игрок {player.user_id}",
                    value=str(player.user_id)
                )
            )

        super().__init__(
            placeholder="Выберите игрока",
            options=options[:25]
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        target_id = int(self.values[0])

        success, message = await self.game.vote(
            interaction.user.id,
            target_id
        )

        await interaction.response.send_message(
            "✅ " + message if success else message,
            ephemeral=True
        )