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

    # Количество голосований для каждого количества игроков.
    # Значения взяты из таблицы правил.
    VOTING_SCHEDULE = {
        4:  [0, 0, 0, 1, 1],
        5:  [0, 0, 1, 1, 1],
        6:  [0, 0, 1, 1, 1],
        7:  [0, 1, 1, 1, 1],
        8:  [0, 1, 1, 1, 1],
        9:  [0, 1, 1, 1, 2],
        10: [0, 1, 1, 1, 2],
        11: [0, 1, 1, 2, 2],
        12: [0, 1, 1, 2, 2],
        13: [0, 1, 2, 2, 2],
        14: [0, 1, 2, 2, 2],
        15: [0, 2, 2, 2, 2],
        16: [0, 2, 2, 2, 2],
    }

    # Сколько игроков попадает в Бункер.
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
        "profession": "💼 Профессия",
        "health": "❤️ Здоровье",
        "biology": "🧬 Биология",
        "hobby": "🎨 Хобби",
        "baggage": "🎒 Багаж",
        "phobia": "😨 Фобия",
    }

    CARD_EMOJIS = {
        "profession": "💼",
        "health": "❤️",
        "biology": "🧬",
        "hobby": "🎨",
        "baggage": "🎒",
        "phobia": "😨",
    }

    CARD_ORDER = [
        "profession",
        "health",
        "biology",
        "hobby",
        "baggage",
        "phobia",
    ]

    # Простая внутриигровая колода Бункера.
    BUNKER_CARDS = [
        "Запас питьевой воды на 10 лет",
        "Медицинский блок",
        "Генератор электричества",
        "Теплица для выращивания пищи",
        "Оружейная комната",
        "Мастерская с инструментами",
        "Система очистки воды",
        "Склад консервов",
        "Радиостанция",
        "Система вентиляции",
        "Лаборатория",
        "Небольшая библиотека",
        "Запас топлива",
        "Спальные помещения",
        "Система наблюдения",
    ]

    THREAT_CARDS = [
        "Заражение воды",
        "Отказ системы вентиляции",
        "Пожар внутри Бункера",
        "Поломка генератора",
        "Нехватка продовольствия",
        "Радиационная утечка",
        "Обрушение части Бункера",
        "Нападение неизвестных",
        "Эпидемия",
        "Сильное землетрясение",
        "Отказ системы отопления",
        "Повреждение запасов",
        "Выход из строя связи",
        "Затопление нижнего уровня",
        "Критическая нехватка медикаментов",
    ]

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

        self.catastrophe = get_random_catastrophe()

        self.game_channel = None
        self.game_message = None
        self.action_message = None

        # Голосование
        self.votes: dict[int, int] = {}
        self.vote_number = 0
        self.votes_required = 0

        # Исследованные пары Бункер + Угроза
        self.bunker_pairs = []

        # Кто начинал текущий раунд
        self.round_starter_index = 0

    # ==========================================================
    # ОСНОВНЫЕ СВОЙСТВА
    # ==========================================================

    @property
    def player_count(self):
        return len(self.players)

    @property
    def bunker_places(self):
        return self.BUNKER_PLACES[self.player_count]

    @property
    def alive_players(self):
        return [
            player
            for player in self.players
            if player.alive
        ]

    @property
    def exiled_players(self):
        return [
            player
            for player in self.players
            if not player.alive
        ]

    def get_player(self, user_id: int):

        for player in self.players:

            if player.user_id == user_id:
                return player

        return None
    def get_player_name(self, player):

        user = self.bot.get_user(player.user_id)

        if user is not None:
            return user.display_name

        return "Игрок"

    # ==========================================================
    # ЗАПУСК
    # ==========================================================

    async def start(self):

        if not (
            self.MIN_PLAYERS
            <= len(self.players)
            <= self.MAX_PLAYERS
        ):
            raise ValueError(
                f"Для Бункера нужно от "
                f"{self.MIN_PLAYERS} до "
                f"{self.MAX_PLAYERS} игроков."
            )

        self.started = True
        self.finished = False
        self.round = 1
        self.phase = "starting"

        print(
            f"========== BUNKER START: "
            f"{len(self.players)} PLAYERS =========="
        )

        # Генерируем персонажей
        self.give_characteristics()

        # Создаём 5 пар Бункер + Угроза
        self.prepare_bunker_pairs()

        # Отправляем карты игрокам
        await self.send_characteristics()

        # Показываем катастрофу
        await self.send_catastrophe()

        # Создаём основное игровое сообщение
        await self.create_game_message()

        # Начинаем первый раунд
        await self.start_round()

        print("========== BUNKER READY ==========")

    # ==========================================================
    # КАТАСТРОФА
    # ==========================================================

    async def send_catastrophe(self):

        if self.game_channel is None:
            return

        embed = discord.Embed(
            title=self.catastrophe["name"],
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
            value=f"**{self.player_count}**",
            inline=True,
        )

        embed.add_field(
            name="☢️ Что произошло",
            value=(
                "Катастрофа уже произошла. "
                "Игрокам предстоит доказать, "
                "почему именно они должны попасть "
                "в Бункер."
            ),
            inline=False,
        )

        await self.game_channel.send(embed=embed)

    # ==========================================================
    # КАРТЫ ПЕРСОНАЖЕЙ
    # ==========================================================

    def give_characteristics(self):

        for player in self.players:

            data = generate_character()

            player.profession = data["profession"]
            player.health = data["health"]
            player.biology = data["biology"]
            player.hobby = data["hobby"]
            player.baggage = data["baggage"]
            player.phobia = data["phobia"]

            player.revealed = []
            player.alive = True
            player.voted = False
            player.in_bunker = False

    def build_private_card(self, player):

        biology = player.biology

        biology_text = (
            f"🎂 Возраст: **{biology['age']}**\n"
            f"⚧️ Гендер: **{biology['gender']}**\n"
            f"🏳️‍🌈 Ориентация: **{biology['orientation']}**\n"
            f"🧬 Особенности: **{biology['details']}**"
        )

        return (
            "🏚️ **ВАША КАРТОЧКА ПЕРСОНАЖА**\n\n"

            f"💼 **Профессия**\n"
            f"{player.profession}\n\n"

            f"❤️ **Здоровье**\n"
            f"{player.health}\n\n"

            f"🧬 **Биология**\n"
            f"{biology_text}\n\n"

            f"🎨 **Хобби**\n"
            f"{player.hobby}\n\n"

            f"🎒 **Багаж**\n"
            f"{player.baggage}\n\n"

            f"😨 **Фобия**\n"
            f"{player.phobia}\n\n"

            "⚠️ Не показывайте карточку другим игрокам."
        )

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
                    f"[BUNKER] "
                    f"ЛС закрыты у {player.user_id}"
                )

            except Exception as e:

                print(
                    f"[BUNKER] Ошибка ЛС "
                    f"{player.user_id}: {e}"
                )

    # ==========================================================
    # БУНКЕР + УГРОЗЫ
    # ==========================================================

    def prepare_bunker_pairs(self):

        bunker = random.sample(
            self.BUNKER_CARDS,
            5,
        )

        threats = random.sample(
            self.THREAT_CARDS,
            5,
        )

        self.bunker_pairs = list(
            zip(bunker, threats)
        )

    async def investigate_bunker(self):

        if self.round > len(self.bunker_pairs):
            return

        bunker, threat = self.bunker_pairs[
            self.round - 1
        ]

        await self.game_channel.send(
            embed=discord.Embed(
                title=(
                    f"🏚️ Исследование Бункера "
                    f"— Раунд {self.round}"
                ),
                description=(
                    f"🏚️ **Бункер:**\n"
                    f"{bunker}\n\n"
                    f"⚠️ **Угроза:**\n"
                    f"{threat}"
                ),
                color=discord.Color.dark_gold(),
            )
        )

    # ==========================================================
    # РАУНД
    # ==========================================================

    async def start_round(self):

        if self.round > self.MAX_ROUNDS:

            await self.finish_game()
            return

        self.phase = "reveal"

        # В новом раунде игроки ещё не раскрывали карту
        # именно этого раунда.
        for player in self.players:
            player.voted = False

        await self.game_channel.send(
            embed=discord.Embed(
                title=(
                    f"🔄 РАУНД "
                    f"{self.round}/{self.MAX_ROUNDS}"
                ),
                description=(
                    "Сейчас произойдёт исследование "
                    "Бункера, после чего игроки будут "
                    "раскрывать свои карты."
                ),
                color=discord.Color.blue(),
            )
        )

        await self.investigate_bunker()
        await self.update_game_message()
        await self.send_action_message()

    # ==========================================================
    # ИГРОВОЕ СООБЩЕНИЕ
    # ==========================================================

    async def create_game_message(self):

        if self.game_channel is None:
            return

    async def create_game_message(self):

        if self.game_channel is None:
             return

        self.game_message = await self.game_channel.send(
        embed=self.build_game_embed()
        )

    def build_game_embed(self):

        embed = discord.Embed(
            title="🏚️ БУНКЕР",
            color=discord.Color.dark_gold(),
        )

        if self.phase == "reveal":

            description = (
                f"### 🔓 Раунд "
                f"{self.round}/{self.MAX_ROUNDS}\n\n"
                "Каждый активный игрок должен "
                "раскрыть **одну ещё не раскрытую карту**."
            )

            if self.round == 1:

                description += (
                    "\n\n💼 **В первом раунде "
                    "обязательно раскрывается Профессия.**"
                )

        elif self.phase == "voting":

            description = (
                f"### 🗳️ Голосование "
                f"{self.vote_number}/{self.votes_required}\n\n"
                "Все игроки, включая изгнанных, "
                "голосуют за кандидата."
            )

        else:

            description = "Игра завершена."

        embed.description = description

        players_text = []

        for player in self.players:

            if player.alive:
                status = "🟢 В игре"
            else:
                status = "❌ Изгнан"

            players_text.append(
                f"<@{player.user_id}> — {status} "
                f"• раскрыто: **{len(player.revealed)}/6**"
            )

        embed.add_field(
            name=(
                f"👥 Игроки "
                f"({len(self.alive_players)}/"
                f"{self.player_count})"
            ),
            value="\n".join(players_text),
            inline=False,
        )

        embed.add_field(
            name="🏚️ Мест в Бункере",
            value=f"**{self.bunker_places}**",
            inline=True,
        )

        embed.add_field(
            name="☢️ Катастрофа",
            value=self.catastrophe["name"],
            inline=True,
        )

        return embed

    async def update_game_message(self):

        if self.game_message is None:
            return

        await self.game_message.edit(
            embed=self.build_game_embed(),
            view=self.get_current_view(),
        )
    async def send_action_message(self):

        # Убираем кнопку с предыдущего сообщения
        if self.action_message is not None:

            try:
                await self.action_message.edit(
                view=discord.ui.View()
                )
            except Exception:
                pass

        # Кнопка раскрытия карты
        if self.phase == "reveal":

            embed = discord.Embed(
                title=f"🔓 Раунд {self.round}/{self.MAX_ROUNDS}",
                description=(
                "Выберите карту, которую хотите раскрыть.\n\n"
                "⚠️ Уже раскрытые карты больше "
                "не доступны для выбора."
                ),
                color=discord.Color.blue()
            )

            self.action_message = await self.game_channel.send(
                embed=embed,
                view=BunkerRevealView(self)
            )

        # Кнопка голосования
        elif self.phase == "voting":

            embed = discord.Embed(
                title=(
                f"🗳️ Голосование "
                f"{self.vote_number}/{self.votes_required}"
            ),
            description=(
                "Выберите игрока, которого хотите "
                "изгнать из Бункера."
            ),
            color=discord.Color.red()
        )

        self.action_message = await self.game_channel.send(
            embed=embed,
            view=BunkerVoteView(self)
        )

    def get_current_view(self):

        if self.phase == "reveal":

            return BunkerRevealView(self)

        if self.phase == "voting":

            return BunkerVoteView(self)

        return discord.ui.View()

    # ==========================================================
    # ДОСТУПНЫЕ КАРТЫ
    # ==========================================================

    def available_cards_for_player(self, player):

        cards = []

        for card in self.CARD_ORDER:

            if card in player.revealed:
                continue

            # В первом раунде только Профессия
            if self.round == 1:
                if card != "profession":
                    continue

            cards.append(card)

        return cards

    # ==========================================================
    # РАСКРЫТИЕ КАРТЫ
    # ==========================================================

    async def reveal_characteristic(
        self,
        user_id: int,
        characteristic: str,
    ):

        player = self.get_player(user_id)

        if player is None:
            return False, "❌ Вы не участвуете в игре."

        if not player.alive:
            return False, "❌ Вы уже изгнаны."

        if self.phase != "reveal":
            return False, "❌ Сейчас нельзя раскрывать карты."

        available = self.available_cards_for_player(
            player
        )

        if characteristic not in available:

            if characteristic in player.revealed:

                return False, (
                    "❌ Эта карта уже была раскрыта."
                )

            return False, (
                "❌ Эту карту сейчас нельзя раскрыть."
            )

        value = getattr(
            player,
            characteristic,
            None,
        )

        if value is None:

            return False, (
                "❌ Данные карты не найдены."
            )

        player.reveal(characteristic)

        value_text = self.format_card_value(
            characteristic,
            value,
        )

        await self.game_channel.send(
            embed=discord.Embed(
                title=(
                    f"🔓 <@{user_id}> раскрывает "
                    f"{self.CARD_NAMES[characteristic]}"
                ),
                description=value_text,
                color=discord.Color.green(),
            )
        )

        # Проверяем, раскрыли ли все активные игроки
        if self.all_active_players_revealed():

            await self.finish_reveal_phase()

        else:

            await self.update_game_message()

        return True, "Карта раскрыта."

    def format_card_value(
        self,
        characteristic,
        value,
    ):

        if characteristic == "biology":

            return (
                f"🎂 Возраст: **{value['age']}**\n"
                f"⚧️ Гендер: **{value['gender']}**\n"
                f"🏳️‍🌈 Ориентация: "
                f"**{value['orientation']}**\n"
                f"🧬 Особенности: "
                f"**{value['details']}**"
            )

        return str(value)

    def all_active_players_revealed(self):

        for player in self.alive_players:

            # В каждом раунде каждый активный игрок
            # должен раскрыть ещё одну карту.
            if len(player.revealed) < self.round:

                return False

        return True

    async def finish_reveal_phase(self):

        votes_for_round = self.VOTING_SCHEDULE[
            self.player_count
        ][self.round - 1]

        print(
        f"[BUNKER] Round {self.round}: "
        f"voting required = {votes_for_round}"
        )

        # В этом раунде голосования НЕТ
        if votes_for_round == 0:

            self.phase = "round_end"

            await self.game_channel.send(
                embed=discord.Embed(
                    title=f"🏁 Раунд {self.round} завершён",
                    description=(
                    "Все игроки раскрыли свои карты.\n\n"
                    "🗳️ **Голосования в этом раунде нет.**"
                    ),
                    color=discord.Color.orange()
                )
            )

            await self.next_round()
            return

        # В этом раунде голосование есть
        self.votes_required = votes_for_round
        self.vote_number = 1

        await self.start_voting_phase()

    # ==========================================================
    # СЛЕДУЮЩИЙ РАУНД
    # ==========================================================

    async def next_round(self):

        self.round += 1

        if self.round > self.MAX_ROUNDS:

            await self.finish_game()
            return

        await self.game_channel.send(
            embed=discord.Embed(
                title=(
                    f"➡️ Начинается раунд "
                    f"{self.round}/{self.MAX_ROUNDS}"
                ),
                color=discord.Color.blue(),
            )
        )

        await self.start_round()

    # ==========================================================
    # ГОЛОСОВАНИЕ
    # ==========================================================

    async def start_voting_phase(self):

        self.phase = "voting"
        self.votes = {}

        # ВАЖНО:
        # голосуют ВСЕ игроки, включая изгнанных.
        for player in self.players:
            player.voted = False

        await self.game_channel.send(
            embed=discord.Embed(
                title=(
                    f"🗳️ ГОЛОСОВАНИЕ "
                    f"{self.vote_number}/"
                    f"{self.votes_required}"
                ),
                description=(
                    "Все игроки, включая изгнанных, "
                    "могут проголосовать.\n\n"
                    "Выберите игрока, которого хотите "
                    "изгнать из Бункера."
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

        if voter is None or target is None:

            return False, "❌ Игрок не найден."

        # В оригинальных правилах изгнанные продолжают
        # голосовать.
        if voter.voted:

            return False, (
                "❌ Вы уже проголосовали."
            )

        # Нельзя голосовать за уже изгнанного.
        if not target.alive:

            return False, (
                "❌ Этот игрок уже изгнан."
            )

        # За себя голосовать нельзя.
        if voter_id == target_id:

            return False, (
                "❌ Нельзя голосовать за себя."
            )

        self.votes[voter_id] = target_id
        voter.voted = True

        await self.game_channel.send(
            f"🗳️ <@{voter_id}> проголосовал."
        )

        if self.all_players_voted():

            await self.finish_voting()

        else:

            await self.update_game_message()

        return True, "Голос принят."

    def all_players_voted(self):

        for player in self.players:

            if not player.voted:
                return False

        return True

    async def finish_voting(self):

        if not self.votes:
            return

        counts = {}

        for target_id in self.votes.values():

            counts[target_id] = (
                counts.get(target_id, 0) + 1
            )

        max_votes = max(counts.values())

        candidates = [
            player_id
            for player_id, votes in counts.items()
            if votes == max_votes
        ]

        # Ничья — повторное голосование.
        if len(candidates) > 1:

            await self.game_channel.send(
                embed=discord.Embed(
                    title="⚖️ Ничья",
                    description=(
                        "Несколько игроков набрали "
                        "одинаковое количество голосов.\n\n"
                        "Проводится повторное голосование."
                    ),
                    color=discord.Color.orange(),
                )
            )

            self.votes = {}

            for player in self.players:
                player.voted = False

            # Временно ограничиваем выбор кандидатами.
            self.tie_candidates = candidates

            await self.update_game_message()
            return

        eliminated_id = candidates[0]

        eliminated = self.get_player(
            eliminated_id
        )

        await self.eliminate_player(eliminated)

        # Если это было последнее голосование раунда
        if self.vote_number >= self.votes_required:

            await self.next_round()
            return

        # Иначе второе голосование
        self.vote_number += 1
        self.votes = {}

        for player in self.players:
            player.voted = False

        await self.start_voting_phase()

    async def eliminate_player(self, player):

        player.kill()

        # Изгнанный сразу раскрывает ВСЕ карты.
        for card in self.CARD_ORDER:

            if card not in player.revealed:
                player.revealed.append(card)

        await self.game_channel.send(
            embed=discord.Embed(
                title="❌ ИГРОК ИЗГНАН",
                description=(
                    f"<@{player.user_id}> "
                    "становится изгнанным.\n\n"
                    "Все его карты раскрываются."
                ),
                color=discord.Color.red(),
            )
        )

        await self.game_channel.send(
            embed=discord.Embed(
                title="🎴 Карты изгнанного игрока",
                description=self.build_revealed_player_text(
                    player
                ),
                color=discord.Color.dark_red(),
            )
        )

    # ==========================================================
    # ФИНАЛ
    # ==========================================================

    async def finish_game(self):

        if self.finished:
            return

        self.finished = True
        self.started = False
        self.phase = "finished"

        winners = self.alive_players

        for player in winners:
            player.enter_bunker()

        await self.game_channel.send(
            embed=discord.Embed(
                title="🏆 ИГРА ЗАВЕРШЕНА",
                description=(
                    "Все 5 раундов завершены.\n\n"
                    f"🏚️ В Бункер попадают "
                    f"**{len(winners)} игроков**."
                ),
                color=discord.Color.gold(),
            )
        )

        winner_text = []

        for player in winners:

            winner_text.append(
                f"🏆 <@{player.user_id}>"
            )

        await self.game_channel.send(
            embed=discord.Embed(
                title="🏚️ ПОПАЛИ В БУНКЕР",
                description="\n".join(winner_text),
                color=discord.Color.green(),
            )
        )

        # Финальное раскрытие оставшихся карт
        for player in winners:

            await self.game_channel.send(
                embed=discord.Embed(
                    title=(
                        f"🎴 Финальные карты "
                        f"<@{player.user_id}>"
                    ),
                    description=(
                        self.build_revealed_player_text(
                            player
                        )
                    ),
                    color=discord.Color.blurple(),
                )
            )

        room_manager.delete_room(
            self.room.owner_id
        )

    def build_revealed_player_text(self, player):

        lines = []

        for card in self.CARD_ORDER:

            value = getattr(
                player,
                card,
                None,
            )

            if value is None:
                continue

            lines.append(
                f"{self.CARD_EMOJIS[card]} "
                f"**{self.CARD_NAMES[card]}**\n"
                f"{self.format_card_value(card, value)}"
            )

        return "\n\n".join(lines)


# ==============================================================
# VIEW — РАСКРЫТИЕ
# ==============================================================

class BunkerRevealView(discord.ui.View):

    def __init__(self, game: BunkerGame):

        super().__init__(timeout=None)

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

        if not player.alive:

            await interaction.response.send_message(
                "❌ Вы уже изгнаны.",
                ephemeral=True,
            )
            return

        if self.game.phase != "reveal":

            await interaction.response.send_message(
                "❌ Сейчас нельзя раскрывать карты.",
                ephemeral=True,
            )
            return

        if len(player.revealed) >= self.game.round:

            await interaction.response.send_message(
                "❌ Вы уже раскрыли карту в этом раунде.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "🎴 Выберите карту:",
            view=BunkerRevealSelectView(
                self.game,
                player,
            ),
            ephemeral=True,
        )


# ==============================================================
# VIEW — ВЫБОР КАРТЫ
# ==============================================================

class BunkerRevealSelectView(discord.ui.View):

    def __init__(
        self,
        game: BunkerGame,
        player: BunkerPlayer,
    ):

        super().__init__(timeout=60)

        self.add_item(
            BunkerCharacteristicSelect(
                game,
                player,
            )
        )


class BunkerCharacteristicSelect(
    discord.ui.Select
):

    def __init__(
        self,
        game: BunkerGame,
        player: BunkerPlayer,
    ):

        self.game = game
        self.player = player

        options = []

        available = (
            game.available_cards_for_player(
                player
            )
        )

        for card in available:

            options.append(
                discord.SelectOption(
                    label=game.CARD_NAMES[card],
                    emoji=game.CARD_EMOJIS[card],
                    value=card,
                )
            )

        super().__init__(
            placeholder="Выберите карту",
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(
        self,
        interaction: discord.Interaction,
    ):

        success, message = (
            await self.game.reveal_characteristic(
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

        # Голосовать могут все,
        # но кандидатами являются только живые.
        for player in game.alive_players:

            player_name = game.get_player_name(player)

            options.append(
                discord.SelectOption(
            label=player_name[:100],
            value=str(player.user_id)
                )
           )

        # Discord разрешает максимум 25 вариантов
        super().__init__(
            placeholder="Выберите кандидата",
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