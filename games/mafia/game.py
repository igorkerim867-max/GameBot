
from games.mafia import player
from games.mafia.views import PlayerSelectView
import random
import asyncio
from games.room_manager import room_manager
import discord
from games.mafia.engine.check_win import check_win
from games.mafia.actions.doctor import handle_doctor_action
from games.mafia.actions.sheriff import handle_sheriff_action
from games.mafia.player import MafiaPlayer
from games.mafia.role_manager import ROLES
from games.mafia.roles import RoleType
from games.mafia.services.player_service import PlayerService
from games.mafia.services.message_service import MessageService
from games.mafia.engine.start_night import start_night
from games.mafia.night_state import NightState
from games.mafia.engine.check_night import check_night
from games.mafia.actions.mafia import handle_mafia_action
from games.mafia.actions.hooker import handle_hooker_action
from games.mafia.actions.maniac import handle_maniac_action
from games.mafia.engine.finish_night import finish_night as engine_finish_night
from games.mafia.settings import get_time_settings
from database.mafia.service import MafiaStatsService
try:
    from database.mafia.checker import AchievementChecker
except Exception:
    # Fallback stub if the checker module is unavailable in the environment
    class AchievementChecker:
        def __init__(self, *args, **kwargs):
            pass

        async def check_all(self, user_id):
            return []
ROLE_SETUP = {
    4: {
        RoleType.MAFIA: 1,
        RoleType.DOCTOR: 1,
        RoleType.SHERIFF: 1,
        RoleType.CIVILIAN: 1,
    },
    5: {
        RoleType.MAFIA: 1,
        RoleType.DOCTOR: 1,
        RoleType.SHERIFF: 1,
        RoleType.HOOKER: 1,
        RoleType.CIVILIAN: 1,
    },
    6: {
        RoleType.MAFIA: 1,
        RoleType.DOCTOR: 1,
        RoleType.SHERIFF: 1,
        RoleType.HOOKER: 1,
        RoleType.CIVILIAN: 2,
    },
    7: {
        RoleType.MAFIA: 1,
        RoleType.DOCTOR: 1,
        RoleType.SHERIFF: 1,
        RoleType.HOOKER: 1,
        RoleType.CIVILIAN: 3,
    },
    8: {
        RoleType.MAFIA: 1,
        RoleType.DOCTOR: 1,
        RoleType.SHERIFF: 1,
        RoleType.HOOKER: 1,
        RoleType.CIVILIAN: 4,
    },
    9: {
        RoleType.MAFIA: 2,
        RoleType.DOCTOR: 1,
        RoleType.SHERIFF: 1,
        RoleType.HOOKER: 1,
        RoleType.CIVILIAN: 4,
    },
    10: {
        RoleType.MAFIA: 2,
        RoleType.DOCTOR: 2,
        RoleType.SHERIFF: 1,
        RoleType.HOOKER: 1,
        RoleType.CIVILIAN: 4,
    },
    11: {
        RoleType.MAFIA: 2,
        RoleType.DOCTOR: 2,
        RoleType.SHERIFF: 1,
        RoleType.HOOKER: 2,
        RoleType.CIVILIAN: 4,
    },
    12: {
        RoleType.MAFIA: 3,
        RoleType.DOCTOR: 2,
        RoleType.SHERIFF: 2,
        RoleType.HOOKER: 1,
        RoleType.CIVILIAN: 4,
    },
    13: {
        RoleType.MAFIA: 3,
        RoleType.DOCTOR: 2,
        RoleType.SHERIFF: 2,
        RoleType.HOOKER: 1,
        RoleType.CIVILIAN: 5,
    },
    14: {
        RoleType.MAFIA: 3,
        RoleType.DOCTOR: 2,
        RoleType.SHERIFF: 2,
        RoleType.HOOKER: 2,
        RoleType.CIVILIAN: 5,
        },
    15: {
        RoleType.MAFIA: 3,
        RoleType.DOCTOR: 2,
        RoleType.SHERIFF: 2,
        RoleType.HOOKER: 2,
        RoleType.CIVILIAN: 6,
        },

}
class MafiaGame:

    def __init__(self, bot: discord.Client, room):
        self.stats = MafiaStatsService()
        self.achievement_checker = AchievementChecker(self.stats)
        self.bot = bot
        self.room = room

        self.players = [
            MafiaPlayer(user_id)
            for user_id in room.players
        ]
        self.player_service = PlayerService(self)
    

        self.day = 0
        self.night = 0

        self.started = False

        # Игровое сообщение
        self.game_channel = None
        # Ночные действия
        self.night_state = NightState()
        # Голосование
        self.votes = {}
        self.voted_players = set()
        self.voted_players = set()
        self.finished = False

    async def start(self):

        print("========== GAME START ==========")

        self.started = True
        for player in self.players:

            user = await self.bot.fetch_user(player.user_id)

            if not await self.stats.player_exists(player.user_id):

                await self.stats.create_player(
                    player.user_id,
                    user.name
                )

            else:

                await self.stats.update_username(
                    player.user_id,
                    user.name
                )

            await self.stats.add_game(player.user_id)

        self.give_roles()

        await self.send_roles()

        await self.start_night()

        print("========== GAME READY ==========")

    def give_roles(self):

        count = len(self.players)

        if count not in ROLE_SETUP:
            raise ValueError(f"Количество игроков {count} не поддерживается.")

        role_types = []

        for role_type, amount in ROLE_SETUP[count].items():
            role_types.extend([role_type] * amount)

        random.shuffle(role_types)

        for player, role_type in zip(self.players, role_types):
            player.role = ROLES[role_type]
    async def send_roles(self):

        print("Отправка ролей...")
        mafia_players = [
            p for p in self.players
            if p.role.role_type == RoleType.MAFIA
        ]
        ROLE_DESCRIPTIONS = {
    RoleType.CIVILIAN:
        "👤 **Мирный житель**\n\n"
        "Ваша задача — вычислить мафию и помочь мирным победить.\n"
        "Ночью вы спите.",

    RoleType.MAFIA:
        "🔪 **Мафия**\n\n"
        "Ваша задача — устранить всех мирных жителей.\n"
        "Каждую ночь вы выбираете жертву.",

    RoleType.DOCTOR:
        "💉 **Доктор**\n\n"
        "Каждую ночь вы можете спасти одного игрока от смерти.",

    RoleType.SHERIFF:
        "👮 **Шериф**\n\n"
        "Каждую ночь вы проверяете одного игрока.\n"
        "Бот сообщит, является ли он мафией.",

    RoleType.HOOKER:
        "💋 **Проститутка**\n\n"
        "Каждую ночь вы выбираете одного игрока.\n"
        "На следующий день он не сможет голосовать."
}


        for player in self.players:

            try:
                user = await self.bot.fetch_user(player.user_id)
                description = ROLE_DESCRIPTIONS.get(
                    player.role.role_type,
                    f"🎭 Ваша роль: **{player.role.name}**"
                )
                # Для мафии добавляем союзников
                if player.role.role_type == RoleType.MAFIA:

                    teammates = [
                        f"<@{p.user_id}>"
                        for p in mafia_players
                        if p.user_id != player.user_id
                    ]

                    description += "\n\n━━━━━━━━━━━━━━\n"

                    if teammates:
                        description += "🔪 **Ваши союзники:**\n"
                        description += "\n".join(f"• {mate}" for mate in teammates)
                    else:
                        description += "🔪 Вы единственный представитель мафии."

               
                print(f"Отправляем {player.role.name}:")
                print(description)
                print("----------------")
                await user.send(description)

                print(f"✔ Роль отправлена {user}")

            except Exception as e:
                print(f"Не удалось отправить роль {player.user_id}: {e}")

    async def start_night(self):
        if self.finished:
            return
        return await start_night(self)
    async def mafia_action(
        self,
        interaction,
        actor,
        target_id
    ):
        return await handle_mafia_action(
            self,
            interaction,
            actor,
            target_id
        )
    async def doctor_action(
        self,
        interaction,
        actor,
        target_id
    ):
        await handle_doctor_action(self, interaction, actor, target_id)
    async def sheriff_action(
       self,
       interaction,
       actor,
       target_id
    ):
        return await handle_sheriff_action(
           self,
           interaction,
           actor,
           target_id
       )
    async def handle_hooker_action(
        self,
        interaction,
        actor,
        target_id
    ):
        return await handle_hooker_action(
            self,
            interaction,
            actor,
            target_id
        )
    async def maniac_action(
        self,
        interaction,
        actor,
        target_id
    ):
        return await handle_maniac_action(
            self,
            interaction,
            actor,
            target_id
        )
    async def check_night_finished(self):
        await check_night(self)

    async def finish_night(self):
        await engine_finish_night(self)


    async def check_win(self):
        return await check_win(self)
    async def game_over(self, text: str):
        self.finished = True

        embed = discord.Embed(
            title="🏁 Игра окончена",
            description=text,
            color=discord.Color.green()
        )

        await self.game_channel.send(embed=embed)
        # Определяем победителей
        mafia_won = "маф" in text.lower()

        for player in self.players:

            if mafia_won:

                if player.role.role_type == RoleType.MAFIA:
                    await self.stats.add_win(player.user_id)
                else:
                    await self.stats.add_loss(player.user_id)

            else:

                if player.role.role_type == RoleType.MAFIA:
                    await self.stats.add_loss(player.user_id)
                else:
                    await self.stats.add_win(player.user_id)
        for player in self.players:

            unlocked = await self.achievement_checker.check_all(
                player.user_id
            )

            if not unlocked:
                continue

            user = await self.bot.fetch_user(player.user_id)

            for achievement_id in unlocked:

                # Try to fetch achievement definition from global ACHIEVEMENTS
                achievement = None
                _achievements_map = globals().get("ACHIEVEMENTS")
                if _achievements_map and achievement_id in _achievements_map:
                    achievement = _achievements_map[achievement_id]
                else:
                    # Fallback placeholder if ACHIEVEMENTS is not available
                    achievement = type("Achievement", (), {
                        "name": str(achievement_id),
                        "description": "",
                        "points": 0,
                    })()

                await user.send(
                    embed=discord.Embed(
                        title="🏆 Новое достижение!",
                        description=(
                            f"**{achievement.name}**\n\n"
                            f"{achievement.description}\n\n"
                            f"⭐ Очков: **{achievement.points}**"
                        ),
                        color=discord.Color.gold()
                    )
                )

        # Сообщаем всем игрокам роли
        roles = "\n".join(
            f"<@{player.user_id}> — **{player.role.name}**"
            for player in self.players
        )

        await self.game_channel.send(
            embed=discord.Embed(
                title="🎭 Роли игроков",
                description=roles,
                color=discord.Color.blurple()
            )
        )

        # Игра завершена
        self.started = False

        # Удаляем комнату
        room_manager.delete_room(self.room.owner_id)

        # Если используется список активных игр — удаляем и оттуда
        if hasattr(room_manager, "games"):
            room_manager.games.pop(self.room.room_id, None)

    async def start_day(self):
        if self.finished:
            return

        print("===== START DAY =====")

        settings = get_time_settings(len(self.players))

        ...
        await asyncio.sleep(settings.discussion)

        print("===== START VOTING =====")

        await self.start_voting()
        settings = get_time_settings(len(self.players))

        embed = discord.Embed(
            title="☀️ День",
            description=(
                "Обсудите произошедшее.\n\n"
                "⏳ Голосование начнётся через 60 секунд."
            ),
            color=discord.Color.gold()
        )

        await self.game_channel.send(embed=embed)

        await asyncio.sleep(settings.discussion)

        await self.start_voting()
    async def start_voting(self):
        if self.finished:
            return
        print("===== VOTING FUNCTION =====")


        self.votes.clear()
        self.voted_players.clear()
        self.voting_finished = False
        settings = get_time_settings(len(self.players))

        embed = discord.Embed(
            title="🗳 Голосование",
            description=(
                "Все живые игроки выбирают, кого хотят изгнать.\n\n"
                f"⏳ На голосование даётся **{settings.vote} секунд**."
            ),
            color=discord.Color.orange()
        )

        await self.game_channel.send(embed=embed)
        print("Alive players:", len(self.player_service.alive_players()))
        for player in self.player_service.alive_players():

            print("Sending vote to", player.user_id)

            try:

                user = await self.bot.fetch_user(player.user_id)

                if not player.can_vote:
                    await user.send(
                        "💋 Прошлой ночью вас посетила Проститутка.\n\n"
                        "Сегодня вы не сможете участвовать в голосовании."
                    )
                    continue

                await user.send(
                    "🗳 Выберите игрока для изгнания.",
                    view=PlayerSelectView(
                        self,
                        player,
                        "vote_action"
                    )
                )

                print("Vote sent!")

            except Exception as e:

                print("ERROR SENDING VOTE:", e)
    
        print("===== CREATING VOTE TASK =====")
        self.vote_task = asyncio.create_task(
            self.vote_timeout()
        )
    async def vote_timeout(self):
        if self.finished:
            return

        settings = get_time_settings(len(self.players))

        # Ждём до предупреждения
        if settings.vote > settings.warning:
            await asyncio.sleep(settings.vote - settings.warning)

            if self.voting_finished:
                return

            await self.game_channel.send(
                f"⚠️ До окончания голосования осталось **{settings.warning} секунд!**"
            )

            await asyncio.sleep(settings.warning)

        else:
            await asyncio.sleep(settings.vote)

        if self.voting_finished:
            return

        await self.game_channel.send(
            "⏳ Время голосования истекло.\nПодводим итоги..."
        )

        await self.finish_voting()
    async def vote_action(
        self,
        interaction,
        actor,
        target_id
    ):
        if target_id is None:

            self.voted_players.add(actor.user_id)

            await interaction.response.send_message(
                "⏭️ Вы решили воздержаться от голосования.",
                ephemeral=True
            )

            can_vote_players = [
                p for p in self.player_service.alive_players()
                if p.can_vote
            ]

            if len(self.voted_players) == len(can_vote_players):

                if self.vote_task:
                   self.vote_task.cancel()

                await self.finish_voting()

            return
        
        target = self.player_service.get_player(target_id)

        if target is None or not target.alive:
            await interaction.response.send_message(
                "❌ Этот игрок уже мёртв.",
                ephemeral=True
            )
            return
        if not actor.can_vote:
            await interaction.response.send_message(
                "💋 Проститутка провела с вами ночь.\n"
                "Сегодня вы не можете голосовать.",
                ephemeral=True
            )
            return

        if actor.user_id in self.voted_players:
            await interaction.response.send_message(
                "❌ Вы уже проголосовали.",
                ephemeral=True
            )
            return

        self.voted_players.add(actor.user_id)
        self.votes[target_id] = self.votes.get(target_id, 0) + 1

        await interaction.response.send_message(
            "✅ Голос принят.",
            ephemeral=True
        )

        can_vote_players = [
            p for p in self.player_service.alive_players()
            if p.can_vote
        ]

        if len(self.voted_players) == len(can_vote_players):

            if self.vote_task:
                self.vote_task.cancel()

            await self.finish_voting()
    async def finish_voting(self):
        if self.voting_finished:
            return

        self.voting_finished = True

        # Если никто не проголосовал
        if not self.votes:

            await self.start_night()
            return

        max_votes = max(self.votes.values())

        leaders = [
            player_id
            for player_id, votes in self.votes.items()
            if votes == max_votes
        ]

        # Ничья
        if len(leaders) > 1:
            embed = discord.Embed(
                title="🗳 Итоги голосования",
                description=(
                    "Голоса разделились поровну.\n\n"
                    "Никто не был изгнан."
                ),
                color=discord.Color.orange()
            )

            await self.game_channel.send(embed=embed)

            await asyncio.sleep(5)
            await self.start_night()
            return

        # Изгнанный игрок
        kicked = self.player_service.get_player(leaders[0])

        kicked.alive = False
        user = await self.bot.fetch_user(kicked.user_id)

        await user.send(
            "💀 Вы были изгнаны голосованием.\n"
            "Вы больше не участвуете в игре."
        )

        embed = discord.Embed(
            title="🗳 Итоги голосования",
                description=(
                f"Игрок <@{kicked.user_id}> был изгнан.\n\n"
                f"🎭 Роль: **{kicked.role.name}**"
            ),
            color=discord.Color.red()
        )

        await self.game_channel.send(embed=embed)

        # Проверяем победу
        if await self.check_win():
            return

        await asyncio.sleep(5)
        for player in self.players:
            player.can_vote = True
            player.blocked_by_hooker = False

        await self.start_night()