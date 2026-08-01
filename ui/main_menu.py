import discord

from core.embeds import GameEmbed


class MainMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🎲 Игры",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def games(self, interaction: discord.Interaction, button: discord.ui.Button):
        from ui.games_menu import GamesMenu

        embed = GameEmbed(
            "🎲 Игры",
            "Выберите игру."
        )

        await interaction.response.edit_message(
            embed=embed,
            view=GamesMenu()
        )

    @discord.ui.button(
        label="👤 Профиль",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"👤 Профиль игрока {interaction.user.mention} пока не реализован.",
            ephemeral=True
        )

    @discord.ui.button(
        label="🏆 Рейтинг",
        style=discord.ButtonStyle.success,
        row=1
    )
    async def rating(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🏆 Рейтинг скоро появится.",
            ephemeral=True
        )

    @discord.ui.button(
        label="⚙️ Настройки",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "⚙️ Настройки находятся в разработке.",
            ephemeral=True
        )