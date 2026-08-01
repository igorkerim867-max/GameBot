import discord
from discord.ext import commands
from discord import app_commands


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ping",
        description="Проверить работу GameBot"
    )
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"🏓 Pong!\nЗадержка: {round(self.bot.latency * 1000)} мс"
        )


async def setup(bot):
    await bot.add_cog(Ping(bot))