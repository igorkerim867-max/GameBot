from __future__ import annotations
print("ROOM MANAGER LOADED:", __file__)
import discord

from games.room import Room


class RoomManager:

    def __init__(self):
        self.rooms: dict[int, Room] = {}

    # ==========================================================
    # Поиск комнат
    # ==========================================================

    def get_room(self, owner_id: int) -> Room | None:
        return self.rooms.get(owner_id)

    def get_room_by_player(self, player_id: int) -> Room | None:
        for room in self.rooms.values():
            if room.is_player(player_id):
                return room
        return None

    def get_room_by_message(self, message_id: int) -> Room | None:
        for room in self.rooms.values():
            if room.message_id == message_id:
                return room
        return None

    def owner_has_room(self, owner_id: int) -> bool:
        return owner_id in self.rooms

    def player_in_room(self, player_id: int) -> bool:
        return self.get_room_by_player(player_id) is not None

    # ==========================================================
    # Комнаты
    # ==========================================================

    def create_room(
        self,
        owner_id: int,
        game: str
    ) -> Room:

        room = Room(
            owner_id=owner_id,
            game=game
        )

        room.add_player(owner_id)

        self.rooms[owner_id] = room

        return room

    def delete_room(self, owner_id: int):
        print(f"[ROOM] Удаляю комнату владельца {owner_id}")
        self.rooms.pop(owner_id, None)
        print(f"[ROOM] Осталось комнат: {len(self.rooms)}")

    # ==========================================================
    # Игроки
    # ==========================================================

    def join_room(
        self,
        owner_id: int,
        player_id: int
    ) -> bool:

        room = self.get_room(owner_id)

        if room is None:
            return False

        if self.player_in_room(player_id):
            return False

        return room.add_player(player_id)

    def leave_room(
        self,
        player_id: int
    ) -> tuple[Room | None, bool]:

        room = self.get_room_by_player(player_id)

        if room is None:
            return None, False

        was_owner = room.owner_id == player_id

        room.remove_player(player_id)

        if room.player_count == 0:
            self.delete_room(room.owner_id)
            return room, True

        if was_owner:

            old_owner = player_id
            new_owner = room.transfer_owner()

            if new_owner is not None:
                self.rooms.pop(old_owner, None)
                self.rooms[new_owner] = room

        return room, False

    # ==========================================================
    # Сообщение комнаты
    # ==========================================================

    def register_message(
        self,
        room: Room,
        channel_id: int,
        message_id: int
    ):
        room.channel_id = channel_id
        room.message_id = message_id
    async def update_room_message(
        self,
        bot: discord.Client,
        room: Room,
        *,
        embed: discord.Embed,
        view: discord.ui.View
    ):

        if room.channel_id is None:
            return

        if room.message_id is None:
            return

        channel = bot.get_channel(room.channel_id)

        if channel is None:
            try:
                channel = await bot.fetch_channel(room.channel_id)
            except Exception:
                return

        try:
            message = await channel.fetch_message(room.message_id)

        except discord.NotFound:
            return

        except discord.Forbidden:
            return

        except discord.HTTPException:
            return

        await message.edit(
            embed=embed,
            view=view
        )

    async def delete_room_message(
        self,
        bot: discord.Client,
        room: Room
    ):

        if room.channel_id is None:
            return

        if room.message_id is None:
            return

        channel = bot.get_channel(room.channel_id)

        if channel is None:
            try:
                channel = await bot.fetch_channel(room.channel_id)
            except Exception:
                return

        try:
            message = await channel.fetch_message(room.message_id)
            await message.delete()

        except Exception:
            pass

    # ==========================================================
    # Игра
    # ==========================================================

    def start_game(
        self,
        owner_id: int
    ) -> bool:

        room = self.get_room(owner_id)

        if room is None:
            return False

        if not room.can_start():
            return False

        room.started = True
        return True

    # ==========================================================
    # Отладка
    # ==========================================================

    def room_count(self) -> int:
        return len(self.rooms)

    def all_rooms(self) -> list[Room]:
        return list(self.rooms.values())

    def clear(self):
        self.rooms.clear()
print("ROOM_MANAGER FILE:", __file__)
print("Has register_message:", hasattr(RoomManager, "register_message"))
room_manager = RoomManager()