import os
import asyncio
import discord
from discord.ext import commands
from ui.main_menu import MainMenu
from ui.games_menu import GamesMenu
from ui.mafia_menu import MafiaMenu
from ui.mafia_lobby import MafiaLobbyView

from config import TOKEN


intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class GameBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents
        )

    async def setup_hook(self):
        # Загружаем все файлы из папки cogs
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and filename != "__init__.py":
                await self.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Загружен модуль: {filename}")
        synced = await self.tree.sync()
        print(f"✅ Slash-команд синхронизировано: {len(synced)}")

    async def on_ready(self):
        print("=" * 40)
        print(f"🎮 {self.user} готов к работе!")
        print(f"📡 Серверов: {len(self.guilds)}")
        print("=" * 40)
    async def on_error(self, event, *args, **kwargs):
        import traceback

        print(f"\n=== ERROR: {event} ===")
        traceback.print_exc()

from games.room_manager import room_manager

async def main():
    room_manager.clear()
    print("✅ Все комнаты очищены")

    bot = GameBot()

    async with bot:
        await bot.start(TOKEN)


asyncio.run(main())