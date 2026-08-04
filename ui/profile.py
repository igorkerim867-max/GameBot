import discord

from database.mafia.service import MafiaStatsService
from ui.achievements import get_achievements_embed
from ui.achievements import (
    get_achievements_embed,
    AchievementView
)

class ProfileView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=180)

    async def achievements(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = await get_achievements_embed(
            interaction.user
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
    async def achievements(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = await get_achievements_embed(
            interaction.user
        )

        await interaction.response.send_message(
            embed=embed,
            view=AchievementView(),
            ephemeral=True
        )
    @discord.ui.button(
        label="🎭 Роли",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def roles(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "🎭 Статистика ролей скоро появится.",
            ephemeral=True
        )

    @discord.ui.button(
        label="📈 Рейтинг",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def rating(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "📈 Рейтинг скоро появится.",
            ephemeral=True
        )

async def get_profile_embed(user: discord.User):

    stats = MafiaStatsService()

    player = await stats.get_player(user.id)

    if player is None:

        games = 0
        wins = 0
        losses = 0
        rating = 1000

    else:

        games = player[2]
        wins = player[3]
        losses = player[4]
        rating = player[5]

    winrate = 0

    if games > 0:
        winrate = round((wins / games) * 100, 1)

    embed = discord.Embed(
        title="👤 Профиль",
        color=discord.Color.blurple()
    )

    embed.set_author(
        name=user.display_name,
        icon_url=user.display_avatar.url
    )

    embed.add_field(
        name="🎮 Игры",
        value=games,
        inline=True
    )

    embed.add_field(
        name="🏆 Победы",
        value=wins,
        inline=True
    )

    embed.add_field(
        name="❌ Поражения",
        value=losses,
        inline=True
    )

    embed.add_field(
        name="📈 Победы",
        value=f"{winrate}%",
        inline=True
    )

    embed.add_field(
        name="⭐ Рейтинг",
        value=rating,
        inline=True
    )

    embed.add_field(
        name="🏅 Очки достижений",
        value="0",
        inline=True
    )

    embed.set_footer(
        text="GameBot • Профиль игрока"
    )

    return embed