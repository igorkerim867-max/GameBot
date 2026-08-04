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

        print("1. /panel вызвана")

        embed = GameEmbed(
            title="🎮 GameBot",
            description=(
                "Добро пожаловать в игровой центр!\n\n"
                "Выберите нужный раздел с помощью кнопок ниже."
            )
        )

        print("2. Embed создан")

        view = MainMenu()

        print("3. MainMenu создан")

        await interaction.response.send_message(
            embed=embed,
            view=view
        )

        print("4. Сообщение отправлено")

async def setup(bot):
    await bot.add_cog(Panel(bot))