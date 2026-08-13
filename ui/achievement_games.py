import discord

from ui.achievements import (
    get_achievements_embed,
    AchievementView
)


class AchievementGameView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=180)


    @discord.ui.button(
        label="🎭 Мафия",
        style=discord.ButtonStyle.primary
    )
    async def mafia(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = await get_achievements_embed(
            interaction.user
        )

        await interaction.response.edit_message(
            embed=embed,
            view=AchievementView()
        )
    @discord.ui.button(
        label="⬅️ Назад",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def back(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            title="🏆 Достижения",
            description="Выберите игру.",
            color=discord.Color.gold()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=AchievementGameView()
        )