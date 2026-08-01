from __future__ import annotations
print("LOADED mafia_lobby.py")
import discord

from games.room import Room
from games.room_manager import room_manager
from games.room import Room
from games.room_manager import room_manager
from core.embeds import GameEmbed


def build_lobby_embed(room: Room) -> discord.Embed:
    """
    Создает Embed комнаты ожидания.
    """

    embed = GameEmbed(
        title="🎭 Мафия",
        description="Ожидание игроков..."
    )

    players = []

    for index, player_id in enumerate(room.players, start=1):
        crown = " 👑" if player_id == room.owner_id else ""
        players.append(f"{index}. <@{player_id}>{crown}")

    if not players:
        players.append("Нет игроков")

    embed.add_field(
        name=f"👥 Игроки ({room.player_count}/{room.max_players})",
        value="\n".join(players),
        inline=False
    )

    embed.add_field(
        name="▶ Старт",
        value=f"Минимум игроков: **{room.min_players}**",
        inline=False
    )

    if room.started:
        embed.set_footer(text="Игра уже началась")
    else:
        embed.set_footer(text="Ожидание начала игры")

    return embed


class MafiaLobbyView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(
    label="🟢 Войти",
    style=discord.ButtonStyle.success,
    custom_id="mafia_join",
    row=0
)
    async def join_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
):

        room = room_manager.get_room_by_message(interaction.message.id)

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

        if room.is_player(interaction.user.id):
            await interaction.response.send_message(
                "❌ Вы уже находитесь в этой комнате.",
                ephemeral=True
            )
            return
        print("[ROOMS]", room_manager.rooms)

        if room_manager.player_in_room(interaction.user.id):
            await interaction.response.send_message(
                "❌ Вы уже находитесь в другой комнате.",
                ephemeral=True
            )
            return

        if room.is_full():
            await interaction.response.send_message(
                "❌ Комната заполнена.",
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
            embed=build_lobby_embed(room),
            view=MafiaLobbyView()
        )

        await interaction.response.send_message(
              "✅ Вы вошли в комнату.",
               ephemeral=True
        )
    @discord.ui.button(
    label="🚪 Выйти",
    style=discord.ButtonStyle.secondary,
    custom_id="mafia_leave",
    row=0
)
    async def leave_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        try:
            room = room_manager.get_room_by_message(interaction.message.id)

        except Exception as e:
            print(f"Error occurred while fetching room: {e}")
            await interaction.response.send_message(
                "❌ Произошла ошибка.",
                ephemeral=True
            )
            return

        if room is None:
            await interaction.response.send_message(
                "❌ Вы не находитесь в комнате.",
                ephemeral=True
            )
            return

        room, deleted = room_manager.leave_room(interaction.user.id)
        print("deleted =", deleted)
        print("После leave_room")
        print("Owner:", room.owner_id if room else None)
        print("Players:", room.players if room else None)
        if room is None:
            await interaction.response.send_message(
                "❌ Не удалось покинуть комнату.",
                ephemeral=True
            )
            return

        if deleted:

            await room_manager.delete_room_message(
                interaction.client,
                room
            )

            await interaction.response.send_message(
                "✅ Комната была удалена.",
                ephemeral=True
            )

            return

        # Если сменился владелец — обновляем View
        new_view = MafiaLobbyView()
        await room_manager.update_room_message(
            interaction.client,
            room,
            embed=build_lobby_embed(room),
            view=new_view
   )

        await interaction.response.send_message(
            "✅ Вы покинули комнату.",
            ephemeral=True
        )
    @discord.ui.button(
        label="▶ Начать игру",
        style=discord.ButtonStyle.primary,
        custom_id="mafia_start",
        row=1
    )
    async def start_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        print("========== START BUTTON ==========")
        room = room_manager.get_room_by_message(
            interaction.message.id
        )

        if room is None:
            await interaction.response.send_message(
                "❌ Комната больше не существует.",
                ephemeral=True
            )
            return

        # Только владелец может начать игру
        if interaction.user.id != room.owner_id:
            await interaction.response.send_message(
                "❌ Только владелец комнаты может начать игру.",
                ephemeral=True
            )
            return

        # Уже запущена
        if room.started:
            await interaction.response.send_message(
                "❌ Игра уже началась.",
                ephemeral=True
            )
            return

        # Недостаточно игроков
        if not room.can_start():
            await interaction.response.send_message(
                f"❌ Для начала игры необходимо минимум {room.min_players} игроков.",
                ephemeral=True
            )
            return

        room.started = True

        # Блокируем все кнопки
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

        await room_manager.update_room_message(
            interaction.client,
            room,
            embed=build_lobby_embed(room),
            view=self
        )

        await interaction.response.send_message(
            "🎭 Игра начинается...",
            ephemeral=True
        )

        try:
            from games.mafia.game import MafiaGame

            print("A")
            print("B")

            game = MafiaGame(
                interaction.client,
                room
            )
            print("C")
            game.game_channel = interaction.channel

            await game.start()
            print("D")

        except Exception as e:
            import traceback

            print("===== ОШИБКА ЗАПУСКА ИГРЫ =====")
            traceback.print_exc() 