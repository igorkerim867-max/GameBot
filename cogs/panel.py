import discord
from discord.ext import commands
from discord import app_commands

from core.embeds import GameEmbed
from ui.main_menu import MainMenu


class Panel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="panel",
        description="Открыть главное меню GameBot"
    )
    async def panel(self, interaction: discord.Interaction):

        embed = GameEmbed(
            title="🎮 GameBot",
            description=(
                "Добро пожаловать в игровой центр!\n\n"
                "Выберите нужный раздел с помощью кнопок ниже."
            )
        )

        await interaction.response.send_message(
            embed=embed,
            view=MainMenu()
        )


async def setup(bot):
    await bot.add_cog(Panel(bot))