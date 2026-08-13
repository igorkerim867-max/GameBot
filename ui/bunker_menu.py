from __future__ import annotations

import traceback

import discord

from core.embeds import GameEmbed
from games.room_manager import room_manager
from ui.games_menu import GamesMenu
from ui.bunker_lobby import BunkerLobbyView, build_bunker_lobby_embed


class BunkerMenu(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="➕ Создать комнату",
        style=discord.ButtonStyle.success,
        row=0
    )
    async def create_room(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        try:

            if room_manager.player_in_room(interaction.user.id):
                await interaction.response.send_message(
                    "❌ Вы уже находитесь в комнате.",
                    ephemeral=True
                )
                return

            room = room_manager.create_room(
                owner_id=interaction.user.id,
                game="bunker"
            )

            embed = build_bunker_lobby_embed(room)
            view = BunkerLobbyView()

            message = await interaction.channel.send(
                embed=embed,
                view=view
            )

            room_manager.register_message(
                room=room,
                channel_id=message.channel.id,
                message_id=message.id
            )

            await interaction.response.send_message(
                "✅ Комната Бункера создана.",
                ephemeral=True
            )

        except Exception:
            traceback.print_exc()

            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Произошла ошибка при создании комнаты.",
                    ephemeral=True
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

        embed = GameEmbed(
            "🎮 Игры",
            "Выберите игру."
        )

        await interaction.response.edit_message(
            embed=embed,
            view=GamesMenu()
        )