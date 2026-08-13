from __future__ import annotations

import discord

from games.room import Room
from games.room_manager import room_manager


def build_bunker_lobby_embed(room: Room) -> discord.Embed:

    embed = discord.Embed(
        title="🏚️ Бункер",
        description="Соберите команду из 6 игроков.",
        color=discord.Color.dark_gold()
    )

    players = []

    for index, player_id in enumerate(room.players, start=1):

        crown = " 👑" if player_id == room.owner_id else ""

        players.append(
            f"{index}. <@{player_id}>{crown}"
        )

    if not players:
        players.append("Нет игроков")

    embed.add_field(
        name=f"👥 Игроки ({room.player_count}/6)",
        value="\n".join(players),
        inline=False
    )

    embed.add_field(
        name="▶ Условия",
        value="Для начала игры необходимо ровно **6 игроков**.",
        inline=False
    )

    if room.started:
        embed.set_footer(
            text="Игра уже началась"
        )
    else:
        embed.set_footer(
            text="Ожидание игроков"
        )

    return embed


class BunkerLobbyView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🟢 Войти",
        style=discord.ButtonStyle.success,
        custom_id="bunker_join",
        row=0
    )
    async def join_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        room = room_manager.get_room_by_message(
            interaction.message.id
        )

        if room is None:
            await interaction.response.send_message(
                "❌ Комната больше не существует.",
                ephemeral=True
            )
            return

        if room.started:
            await interaction.response.send_message(
                "❌ Игра уже началась.",
                ephemeral=True
            )
            return

        if room_manager.player_in_room(interaction.user.id):
            await interaction.response.send_message(
                "❌ Вы уже находитесь в комнате.",
                ephemeral=True
            )
            return

        if room.is_full():
            await interaction.response.send_message(
                "❌ В Бункере может быть только 6 игроков.",
                ephemeral=True
            )
            return

        room_manager.join_room(
            room.owner_id,
            interaction.user.id
        )

        await room_manager.update_room_message(
            interaction.client,
            room,
            embed=build_bunker_lobby_embed(room),
            view=BunkerLobbyView()
        )

        await interaction.response.send_message(
            "✅ Вы вошли в Бункер.",
            ephemeral=True
        )

    @discord.ui.button(
        label="🚪 Выйти",
        style=discord.ButtonStyle.secondary,
        custom_id="bunker_leave",
        row=0
    )
    async def leave_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        room = room_manager.get_room_by_message(
            interaction.message.id
        )

        if room is None:
            await interaction.response.send_message(
                "❌ Комната больше не существует.",
                ephemeral=True
            )
            return

        room, deleted = room_manager.leave_room(
            interaction.user.id
        )

        if room is None:
            await interaction.response.send_message(
                "❌ Вы не находитесь в комнате.",
                ephemeral=True
            )
            return

        if deleted:

            await room_manager.delete_room_message(
                interaction.client,
                room
            )

            await interaction.response.send_message(
                "✅ Комната удалена.",
                ephemeral=True
            )

            return

        await room_manager.update_room_message(
            interaction.client,
            room,
            embed=build_bunker_lobby_embed(room),
            view=BunkerLobbyView()
        )

        await interaction.response.send_message(
            "✅ Вы вышли из комнаты.",
            ephemeral=True
        )

    @discord.ui.button(
        label="▶ Начать игру",
        style=discord.ButtonStyle.primary,
        custom_id="bunker_start",
        row=1
    )
    async def start_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        room = room_manager.get_room_by_message(
            interaction.message.id
        )

        if room is None:
            await interaction.response.send_message(
                "❌ Комната больше не существует.",
                ephemeral=True
            )
            return

        if interaction.user.id != room.owner_id:
            await interaction.response.send_message(
                "❌ Только владелец комнаты может начать игру.",
                ephemeral=True
            )
            return

        if room.started:
            await interaction.response.send_message(
                "❌ Игра уже началась.",
                ephemeral=True
            )
            return

        if not room.can_start():
            await interaction.response.send_message(
                "❌ Для начала Бункера необходимо ровно 6 игроков.",
                ephemeral=True
            )
            return

        room.started = True

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

        await room_manager.update_room_message(
            interaction.client,
            room,
            embed=build_bunker_lobby_embed(room),
            view=self
        )

        await interaction.response.send_message(
            "🏚️ Бункер начинается!",
            ephemeral=True
        )

        try:

            from games.bunker.game import BunkerGame

            game = BunkerGame(
                interaction.client,
                room
            )

            game.game_channel = interaction.channel

            await game.start()

        except Exception:

            import traceback
            print("===== ОШИБКА ЗАПУСКА БУНКЕРА =====")
            traceback.print_exc()