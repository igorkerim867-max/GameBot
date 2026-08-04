from database.mafia.achievements import ACHIEVEMENTS


class AchievementChecker:

    def __init__(self, stats_service):
        self.stats = stats_service

    async def check_all(self, player):

        unlocked = []

        unlocked += await self.check_general(player)
        unlocked += await self.check_mafia(player)
        unlocked += await self.check_doctor(player)
        unlocked += await self.check_sheriff(player)
        unlocked += await self.check_hooker(player)
        unlocked += await self.check_civilian(player)
        unlocked += await self.check_secret(player)
        unlocked += await self.check_legendary(player)

        return unlocked
    async def check_general(self, user_id):

        unlocked = []

        stats = await self.stats.get_player(user_id)

        if stats is None:
            return unlocked

        games = stats[2]
        wins = stats[3]

        achievements = [

            ("FIRST_GAME", games >= 1),

            ("FIRST_WIN", wins >= 1),

            ("GAMES_10", games >= 10),

            ("GAMES_50", games >= 50),

            ("GAMES_100", games >= 100),

            ("WINS_10", wins >= 10),
            
            ("WINS_50", wins >= 50),

            ("WINS_100", wins >= 100),
        ]

        for achievement_id, completed in achievements:

            if not completed:
                continue

            if await self.stats.has_achievement(
                user_id,
                achievement_id
            ):
                continue

            await self.stats.unlock_achievement(
                user_id,
                achievement_id
            )

            unlocked.append(achievement_id)

        return unlocked

    async def check_mafia(self, player):
        return []

    async def check_doctor(self, player):
        return []

    async def check_sheriff(self, player):
        return []

    async def check_hooker(self, player):
        return []

    async def check_civilian(self, player):
        return []

    async def check_secret(self, player):
        return []

    async def check_legendary(self, player):
        return []