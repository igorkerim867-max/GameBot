import discord

from database.mafia.achievements import (
    ACHIEVEMENTS,
    get_progress
)
from database.mafia.service import MafiaStatsService

def progress_bar(current: int, maximum: int) -> str:
    """
    Возвращает красивую полосу прогресса длиной 10 блоков.
    """

    if maximum <= 0:
        return "░" * 10

    blocks = 10

    filled = round((current / maximum) * blocks)

    filled = max(0, min(filled, blocks))

    return (
        "█" * filled +
        "░" * (blocks - filled)
    )
RARITY_TEXT = {
    "COMMON": "⚪ Обычное",
    "RARE": "🟢 Редкое",
    "EPIC": "🟣 Эпическое",
    "LEGENDARY": "🟡 Легендарное"
}
def format_achievement(
    achievement,
    progress
):
    rarity = RARITY_TEXT.get(
        achievement.rarity,
        "⚪ Обычное"
    )

    if progress["completed"]:

       return (
            f"{rarity}\n\n"
            f"██████████\n\n"
            f"✅ **Получено**\n\n"
            f"⭐ Награда: **+{achievement.points} очков**"
        )

    if achievement.hidden:

        return (
            f"{rarity}\n\n"
            f"🔒 Секретное достижение\n\n"
            f"Получите его, чтобы узнать подробности."
           )

    if achievement.max_progress == 1:

        return (
            f"{rarity}\n\n"
            "❌ Не получено\n\n"
            f"⭐ Награда: **+{achievement.points} очков**"
        )

    bar = progress_bar(
        progress["progress"],
        achievement.max_progress
    )

    return (
        f"{rarity}\n\n"
        f"{bar}\n\n"
        f"📈 Прогресс: "
        f"**{progress['progress']} / {achievement.max_progress}**\n"
        f"⏳ Осталось: "
        f"**{progress['remaining']}**\n\n"
        f"⭐ Награда: **+{achievement.points} очков**"
    )

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

    embed.description = (
        f"⭐ **Очков:** {points}\n"
        f"🏅 **Получено:** {unlocked}/{total}\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Выберите категорию достижений ниже."
    )

    return embed
import discord
async def get_category_embed(
    user: discord.User,
    title: str,
    category: dict
):

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

    embed = await get_category_embed(
        interaction.user,
        title,
        category
    )

    await interaction.response.edit_message(
        embed=embed,
        view=AchievementView()
    )

    unlocked = 0
    points = 0
    for achievement in category.values():

        progress = get_progress(
            achievement,
            stats
        )

        if progress["completed"]:
            unlocked += 1
            points += achievement.points

        status = format_achievement(
            achievement,
            progress
        )

        embed.add_field(
            name=achievement.name,
            value=(
                f"{achievement.description}\n\n"
                f"{status}"
            ),
            inline=False
        )
    embed.description = (
        f"⭐ **Очков:** {points}\n"
        f"🏅 **Получено:** {unlocked}/{len(category)}"
    )

    return embed

from database.mafia.achievements import (
    ACHIEVEMENTS,
    GENERAL,
    MAFIA,
    DOCTOR,
    SHERIFF,
    HOOKER,
    CIVILIAN,
    SECRET,
    LEGENDARY,
)



class AchievementView(discord.ui.View):

    def __init__(self):

        super().__init__(timeout=180)

        self.add_item(
            AchievementCategorySelect()
        )
@discord.ui.button(
    label="🎮 Общие",
    style=discord.ButtonStyle.primary,
    row=0
)
async def general(
    self,
    interaction: discord.Interaction,
    button: discord.ui.Button
):
    await interaction.response.edit_message(
        embed=await get_category_embed(
            interaction.user,
            "🎮 Общие достижения",
            GENERAL
        ),
        view=self
    )
def get_category_embed(
    title,
    category
):

    embed = discord.Embed(
        title=title,
        color=discord.Color.gold()
    )

    for achievement in category.values():

        if achievement.hidden:

            embed.add_field(
                name="❓ Секретное достижение",
                value="Получите его, чтобы узнать подробности.",
                inline=False
            )

        else:

            embed.add_field(
                name=achievement.name,
                value=achievement.description,
                inline=False
            )

    return embed
class AchievementCategorySelect(discord.ui.Select):


    def __init__(self):

        options = [

            discord.SelectOption(
                label="Общие",
                emoji="🎮",
                value="general"
            ),

            discord.SelectOption(
                label="Мафия",
                emoji="🔪",
                value="mafia"
            ),

            discord.SelectOption(
                label="Доктор",
                emoji="💉",
                value="doctor"
            ),

            discord.SelectOption(
                label="Шериф",
                emoji="👮",
                value="sheriff"
            ),

            discord.SelectOption(
                label="Проститутка",
                emoji="💋",
                value="hooker"
            ),

            discord.SelectOption(
                label="Мирный",
                emoji="👤",
                value="civilian"
            ),

            discord.SelectOption(
                label="Легендарные",
                emoji="👑",
                value="legendary"
            )

        ]

        super().__init__(
            placeholder="Выберите категорию достижений",
            options=options
        )