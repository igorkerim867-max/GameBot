from __future__ import annotations

import random

import discord

from games.bunker.player import BunkerPlayer
from games.bunker.cards import (
    generate_character,
    get_random_catastrophe,
)
from games.room_manager import room_manager


class BunkerGame:

    MIN_PLAYERS = 4
    MAX_PLAYERS = 16
    MAX_ROUNDS = 5
    VOTING_SCHEDULE = {
        4:  {1: 0, 2: 0, 3: 0, 4: 1, 5: 1},
        5:  {1: 0, 2: 0, 3: 1, 4: 1, 5: 1},
        6:  {1: 0, 2: 0, 3: 1, 4: 1, 5: 1},
        7:  {1: 0, 2: 1, 3: 1, 4: 1, 5: 1},
        8:  {1: 0, 2: 1, 3: 1, 4: 1, 5: 1},
        9:  {1: 0, 2: 1, 3: 1, 4: 1, 5: 2},
        10: {1: 0, 2: 1, 3: 1, 4: 1, 5: 2},
        11: {1: 0, 2: 1, 3: 1, 4: 2, 5: 2},
        12: {1: 0, 2: 1, 3: 1, 4: 2, 5: 2},
        13: {1: 0, 2: 1, 3: 2, 4: 2, 5: 2},
        14: {1: 0, 2: 1, 3: 2, 4: 2, 5: 2},
        15: {1: 0, 2: 2, 3: 2, 4: 2, 5: 2},
        16: {1: 0, 2: 2, 3: 2, 4: 2, 5: 2},
    }

    BUNKER_PLACES = {
        4: 2,
        5: 2,
        6: 3,
        7: 3,
        8: 4,
        9: 4,
        10: 5,
        11: 5,
        12: 6,
        13: 6,
        14: 7,
        15: 7,
        16: 8,
    }

    CARD_NAMES = {
        "superpower": "💪 Суперсила",
        "phobia": "😱 Фобия",
        "character": "🧠 Характер",
        "hobby": "🎯 Хобби",
        "baggage": "🎒 Багаж",
        "fact": "📋 Факты",
    }

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
        self.phase = "waiting"

        self.bunker_places = 0

        self.catastrophe = get_random_catastrophe()

        self.game_channel = None
        self.game_message = None

        self.votes: dict[int, int] = {}

    # ==========================================================
    # ИГРОКИ
    # ==========================================================

    @property
    def active_players(self):
        """
        Игроки, которых ещё можно изгнать.
        Они продолжают раскрывать карты.
        """
        return [
            player
            for player in self.players
            if not player.exiled
        ]

    @property
    def voting_players(self):
        """
        Все игроки голосуют, включая изгнанных.
        """
        return self.players

    def get_player(self, user_id: int):

        for player in self.players:

            if player.user_id == user_id:
                return player

        return None

    # ==========================================================
    # ЗАПУСК
    # ==========================================================

    async def start(self):

        player_count = len(self.players)

        if not (
            self.MIN_PLAYERS
            <= player_count
            <= self.MAX_PLAYERS
        ):
            raise ValueError(
                "Для Бункера необходимо от 4 до 16 игроков."
            )

        self.bunker_places = self.BUNKER_PLACES[
            player_count
        ]

        self.started = True
        self.finished = False
        self.round = 1
        self.phase = "reveal"

        print(
            f"========== BUNKER START: "
            f"{player_count} PLAYERS =========="
        )

        # Раздаём карты
        self.give_characteristics()

        # Отправляем карты игрокам в ЛС
        await self.send_characteristics()

        # Сначала показываем катастрофу
        await self.send_catastrophe()

        # Затем создаём игровое сообщение
        await self.create_game_message()

        print("========== BUNKER READY ==========")

    # ==========================================================
    # КАТАСТРОФА
    # ==========================================================

    async def send_catastrophe(self):

        if self.game_channel is None:
            return

        embed = discord.Embed(
            title="☢️ КАТАСТРОФА",
            description=self.catastrophe["description"],
            color=discord.Color.red(),
        )

        embed.add_field(
            name="🏚️ Мест в Бункере",
            value=f"**{self.bunker_places}**",
            inline=True,
        )

        embed.add_field(
            name="👥 Игроков",
            value=f"**{len(self.players)}**",
            inline=True,
        )

        embed.add_field(
            name="🎯 Цель игры",
            value=(
                "Доказать свою полезность для выживания "
                "и попасть в число тех, кто останется "
                "в Бункере."
            ),
            inline=False,
        )

        await self.game_channel.send(
            embed=embed
        )

    # ==========================================================
    # КАРТЫ
    # ==========================================================

    def give_characteristics(self):

        for player in self.players:

            data = generate_character()

            player.superpower = data["superpower"]
            player.phobia = data["phobia"]
            player.character = data["character"]
            player.hobby = data["hobby"]
            player.baggage = data["baggage"]
            player.fact = data["fact"]

            player.special_condition = data.get(
                "special_condition"
            )

            player.revealed = []
            player.voted = False
            player.exiled = False

    async def send_characteristics(self):

        for player in self.players:

            try:

                user = await self.bot.fetch_user(
                    player.user_id
                )

                await user.send(
                    embed=self.build_private_card(player)
                )

            except discord.Forbidden:

                print(
                    f"[BUNKER] Не удалось отправить ЛС "
                    f"{player.user_id}"
                )

            except Exception as error:

                print(
                    f"[BUNKER] Ошибка отправки ЛС "
                    f"{player.user_id}: {error}"
                )

    def build_private_card(self, player):

        embed = discord.Embed(
            title="🏚️ Бункер — ваша карточка",
            description=(
                "Это ваши личные характеристики.\n"
                "Не показывайте их другим игрокам."
            ),
            color=discord.Color.dark_gold(),
        )

        embed.add_field(
            name="💪 Суперсила",
            value=player.superpower,
            inline=False,
        )

        embed.add_field(
            name="😱 Фобия",
            value=player.phobia,
            inline=False,
        )

        embed.add_field(
            name="🧠 Характер",
            value=player.character,
            inline=False,
        )

        embed.add_field(
            name="🎯 Хобби",
            value=player.hobby,
            inline=False,
        )

        embed.add_field(
            name="🎒 Багаж",
            value=player.baggage,
            inline=False,
        )

        embed.add_field(
            name="📋 Факты",
            value=player.fact,
            inline=False,
        )

        if player.special_condition:

            embed.add_field(
                name="⭐ Особое условие",
                value=player.special_condition,
                inline=False,
            )

        return embed

    # ==========================================================
    # ИГРОВОЕ СООБЩЕНИЕ
    # ==========================================================

    async def create_game_message(self):

        if self.game_channel is None:
            return

        self.game_message = await self.game_channel.send(
            embed=self.build_game_embed(),
            view=BunkerRevealView(self),
        )

    def build_game_embed(self):

        embed = discord.Embed(
            title="🏚️ БУНКЕР",
            color=discord.Color.dark_gold(),
        )

        if self.phase == "reveal":

            description = (
                f"### 🔓 Раунд {self.round}/{self.MAX_ROUNDS}\n\n"
                "Каждый игрок, который ещё не изгнан, "
                "должен раскрыть **одну карту**.\n\n"
                "После раскрытия всех карт начнётся голосование."
            )

        elif self.phase == "voting":

            description = (
                f"### 🗳 Голосование — раунд "
                f"{self.round}/{self.MAX_ROUNDS}\n\n"
                "Все игроки должны проголосовать."
            )

        else:

            description = "Игра завершена."

        embed.description = description

        players_text = []

        for number, player in enumerate(
            self.players,
            start=1,
        ):

            if player.exiled:
                status = "❌ Изгнан"
            else:
                status = "🟢 В игре"

            revealed_count = len(
                player.revealed
            )

            players_text.append(
                f"**{number}.** <@{player.user_id}> "
                f"— {status} "
                f"• карт открыто: **{revealed_count}**"
            )

        embed.add_field(
            name=(
                f"👥 Игроки "
                f"({len(self.active_players)}/{len(self.players)})"
            ),
            value="\n".join(players_text),
            inline=False,
        )

        embed.add_field(
            name="🏚️ Бункер",
            value=(
                f"Мест: **{self.bunker_places}**\n"
                f"Игроков останется: **{self.bunker_places}**"
            ),
            inline=False,
        )

        return embed

    async def update_game_message(self):

        if self.game_message is None:
            return

        await self.game_message.edit(
            embed=self.build_game_embed(),
            view=self.get_current_view(),
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

    async def reveal_card(
        self,
        user_id: int,
        card_type: str,
    ):

        player = self.get_player(user_id)

        if player is None:
            return False, "Вы не участвуете в игре."

        if player.exiled:
            return (
                False,
                "❌ Вы уже изгнаны и больше не раскрываете карты.",
            )

        if card_type not in self.CARD_NAMES:
            return False, "❌ Неизвестная карта."

        if card_type in player.revealed:
            return (
                False,
                "❌ Эта карта уже была раскрыта.",
            )

        if len(player.revealed) >= self.round:
            return (
                False,
                "❌ В этом раунде вы уже раскрыли карту.",
            )

        value = getattr(
            player,
            card_type,
            None,
        )

        if value is None:
            return False, "❌ Карта не найдена."

        player.reveal(card_type)

        await self.game_channel.send(
            f"🔓 <@{user_id}> раскрывает "
            f"**{self.CARD_NAMES[card_type]}**:\n"
            f"> {value}"
        )

        if self.all_active_players_revealed():

            await self.start_voting_phase()

        else:

            await self.update_game_message()

        return True, "Карта раскрыта."

    def all_active_players_revealed(self):

        for player in self.active_players:

            if len(player.revealed) < self.round:
                return False

        return True

    # ==========================================================
    # ГОЛОСОВАНИЕ
    # ==========================================================

    async def start_voting_phase(self):

        player_count = len(self.players)

        votes_count = self.VOTING_SCHEDULE[
            player_count
        ][self.round]

        # ==========================================
        # В ЭТОМ РАУНДЕ ГОЛОСОВАНИЯ НЕТ
        # ==========================================

        if votes_count == 0:

            await self.game_channel.send(
                embed=discord.Embed(
                    title=f"🏁 Раунд {self.round} завершён",
                    description=(
                    f"Все игроки раскрыли карты.\n\n"
                    f"🗳️ В этом раунде голосования нет."
                    ),
                    color=discord.Color.orange(),
                )
            )

            # Если это был последний раунд
            if self.round >= self.MAX_ROUNDS:

                await self.finish_game()
                return

            # Переходим к следующему раунду
            self.round += 1

            await self.game_channel.send(
                embed=discord.Embed(
                    title=f"🔄 Раунд {self.round}",
                    description=(
                    f"Начинается раунд "
                    f"**{self.round}/{self.MAX_ROUNDS}**."
                    ),
                    color=discord.Color.blue(),
                )
            )

            await self.start_reveal_phase()

            return

        # ==========================================
        # В ЭТОМ РАУНДЕ ЕСТЬ ГОЛОСОВАНИЕ
        # ==========================================

        self.phase = "voting"
        self.votes = {}

        self.current_vote_number = 1
        self.votes_required = votes_count

        for player in self.players:
            player.voted = False

        await self.game_channel.send(
            embed=discord.Embed(
                title="🗳️ Голосование",
                description=(
                f"Голосование "
                f"**{self.current_vote_number}/"
                f"{self.votes_required}**\n\n"
                "Все игроки, включая изгнанных, "
                "участвуют в голосовании."
                ),
                color=discord.Color.red(),
            )
        )

        await self.update_game_message()

    async def vote(
        self,
        voter_id: int,
        target_id: int,
    ):

        voter = self.get_player(voter_id)
        target = self.get_player(target_id)

        if voter is None:
            return False, "Вы не участвуете в игре."

        if target is None:
            return False, "Игрок не найден."

        # Изгнанные тоже голосуют.
        if voter.voted:
            return False, "❌ Вы уже проголосовали."

        if target.exiled:
            return False, "❌ Этот игрок уже изгнан."

        if voter_id == target_id:
            return False, "❌ Нельзя голосовать за себя."

        self.votes[voter_id] = target_id
        voter.voted = True

        await self.game_channel.send(
            f"🗳 <@{voter_id}> проголосовал."
        )

        if self.all_players_voted():

            await self.finish_voting()

        else:

            await self.update_game_message()

        return True, "Голос принят."

    def all_players_voted(self):

        return all(
            player.voted
            for player in self.voting_players
        )

    async def finish_voting(self):

        if not self.votes:
            return

        counts = {}

        for target_id in self.votes.values():

            counts[target_id] = (
                counts.get(target_id, 0) + 1
            )

        max_votes = max(
            counts.values()
        )

        candidates = [
            player_id
            for player_id, votes in counts.items()
            if votes == max_votes
        ]

        eliminated_id = random.choice(
            candidates
        )

        eliminated = self.get_player(
            eliminated_id
        )

        eliminated.exile()

        await self.game_channel.send(
            f"❌ **<@{eliminated_id}> изгнан!**\n\n"
            f"Получено голосов: **{max_votes}**"
        )

        # Последний раунд
        if self.current_vote_number < self.votes_required:

            self.current_vote_number += 1
            self.votes = {}

            for player in self.players:
               player.voted = False

            await self.game_channel.send(
        f"🗳️ **Второе голосование "
        f"{self.current_vote_number}/{self.votes_required}**"
            )

            await self.update_game_message()
            return


        if self.round >= self.MAX_ROUNDS:

            await self.finish_game()
            return


        self.round += 1



        await self.game_channel.send(
            f"🔄 **Начинается раунд "
            f"{self.round}/{self.MAX_ROUNDS}.**"
        )

        await self.start_reveal_phase()

    # ==========================================================
    # НОВЫЙ РАУНД
    # ==========================================================

    async def start_reveal_phase(self):

        self.phase = "reveal"

        for player in self.players:

            player.voted = False

        await self.update_game_message()

    # ==========================================================
    # ЗАВЕРШЕНИЕ
    # ==========================================================

    async def finish_game(self):

        self.finished = True
        self.started = False
        self.phase = "finished"

        winners = self.active_players

        # Если каким-то образом осталось больше мест,
        # выбираем только нужное количество.
        if len(winners) > self.bunker_places:

            winners = winners[
                :self.bunker_places
            ]

        winner_text = "\n".join(
            f"🏆 <@{player.user_id}>"
            for player in winners
        )

        embed = discord.Embed(
            title="🏆 БУНКЕР ЗАВЕРШЁН!",
            description=(
                f"После {self.MAX_ROUNDS} раундов "
                "определены люди, которые попадают "
                "в Бункер.\n\n"
                f"### 🏚️ Выжившие:\n"
                f"{winner_text}"
            ),
            color=discord.Color.gold(),
        )

        embed.add_field(
            name="☢️ Катастрофа",
            value=self.catastrophe["description"],
            inline=False,
        )

        embed.add_field(
            name="🏚️ Мест в Бункере",
            value=str(self.bunker_places),
            inline=True,
        )

        await self.game_channel.send(
            embed=embed
        )

        room_manager.delete_room(
            self.room.owner_id
        )


# ==============================================================
# VIEW — РАСКРЫТИЕ
# ==============================================================

class BunkerRevealView(discord.ui.View):

    def __init__(self, game):

        super().__init__(
            timeout=None
        )

        self.game = game

    @discord.ui.button(
        label="🔓 Раскрыть карту",
        style=discord.ButtonStyle.primary,
    )
    async def reveal(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):

        player = self.game.get_player(
            interaction.user.id
        )

        if player is None:

            await interaction.response.send_message(
                "❌ Вы не участвуете в игре.",
                ephemeral=True,
            )
            return

        if player.exiled:

            await interaction.response.send_message(
                "❌ Вы уже изгнаны.",
                ephemeral=True,
            )
            return

        if len(player.revealed) >= self.game.round:

            await interaction.response.send_message(
                "❌ В этом раунде вы уже раскрыли карту.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "Выберите карту, которую хотите раскрыть:",
            view=BunkerRevealSelectView(
                self.game
            ),
            ephemeral=True,
        )


# ==============================================================
# SELECT — РАСКРЫТИЕ КАРТЫ
# ==============================================================

class BunkerRevealSelectView(discord.ui.View):

    def __init__(self, game):

        super().__init__(
            timeout=60
        )

        self.add_item(
            BunkerCharacteristicSelect(game)
        )


class BunkerCharacteristicSelect(
    discord.ui.Select
):

    def __init__(self, game):

        self.game = game

        options = [
            discord.SelectOption(
                label="Суперсила",
                emoji="💪",
                value="superpower",
            ),
            discord.SelectOption(
                label="Фобия",
                emoji="😱",
                value="phobia",
            ),
            discord.SelectOption(
                label="Характер",
                emoji="🧠",
                value="character",
            ),
            discord.SelectOption(
                label="Хобби",
                emoji="🎯",
                value="hobby",
            ),
            discord.SelectOption(
                label="Багаж",
                emoji="🎒",
                value="baggage",
            ),
            discord.SelectOption(
                label="Факты",
                emoji="📋",
                value="fact",
            ),
        ]

        super().__init__(
            placeholder="Выберите карту",
            options=options,
        )

    async def callback(
        self,
        interaction: discord.Interaction,
    ):

        success, message = (
            await self.game.reveal_card(
                interaction.user.id,
                self.values[0],
            )
        )

        await interaction.response.send_message(
            (
                "✅ " + message
                if success
                else message
            ),
            ephemeral=True,
        )


# ==============================================================
# VIEW — ГОЛОСОВАНИЕ
# ==============================================================

class BunkerVoteView(
    discord.ui.View
):

    def __init__(self, game):

        super().__init__(
            timeout=None
        )

        self.add_item(
            BunkerVoteSelect(game)
        )


class BunkerVoteSelect(
    discord.ui.Select
):

    def __init__(self, game):

        self.game = game

        options = []

        for index, player in enumerate(
            game.active_players,
            start=1,
        ):

            options.append(
                discord.SelectOption(
                    label=f"Игрок {index}",
                    description="Проголосовать за исключение",
                    value=str(
                        player.user_id
                    ),
                )
            )

        super().__init__(
            placeholder="Выберите игрока",
            options=options[:25],
        )

    async def callback(
        self,
        interaction: discord.Interaction,
    ):

        target_id = int(
            self.values[0]
        )

        success, message = (
            await self.game.vote(
                interaction.user.id,
                target_id,
            )
        )

        await interaction.response.send_message(
            (
                "✅ " + message
                if success
                else message
            ),
            ephemeral=True,
        )