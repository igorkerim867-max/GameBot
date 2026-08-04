import discord

from database.mafia.achievements import (
    ACHIEVEMENTS,
    get_progress
)
from database.mafia.service import MafiaStatsService


async def get_achievements_embed(user: discord.User):

    stats_service = MafiaStatsService()

    player = await stats_service.get_player(user.id)

    if player is None:
        stats = {
            "games": 0,
            "wins": 0,
            "losses": 0
        }
    else:
        stats = {
            "games": player[2],
            "wins": player[3],
            "losses": player[4]
        }

    embed = discord.Embed(
        title="🏆 Достижения",
        color=discord.Color.gold()
    )

    total = len(ACHIEVEMENTS)
    unlocked = 0
    points = 0

    for achievement in ACHIEVEMENTS.values():

        progress = get_progress(
            achievement,
            stats
        )

        if progress["completed"]:

            unlocked += 1
            points += achievement.points

            value = "✅ Получено"

        else:

            if achievement.hidden:

                value = "🔒 Секретное достижение"

            elif achievement.max_progress == 1:

                value = "❌ Не получено"

            else:

                value = (
                    f"📈 {progress['progress']}/{achievement.max_progress}\n"
                    f"Осталось: {progress['remaining']}"
                )

        embed.add_field(
            name=achievement.name,
            value=value,
            inline=False
        )

    embed.description = (
        f"⭐ Очков: **{points}**\n"
        f"🏅 Получено: **{unlocked}/{total}**"
    )

    return embed