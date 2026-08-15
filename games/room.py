from dataclasses import dataclass, field


@dataclass(slots=True)
class Room:
    owner_id: int
    game: str

    players: list[int] = field(default_factory=list)

    started: bool = False

    min_players: int = field(init=False)
    max_players: int = field(init=False)

    channel_id: int | None = None
    message_id: int | None = None
    def __post_init__(self):

        if self.game == "bunker":
            self.min_players = 4
            self.max_players = 16

        else:
            self.min_players = 4
            self.max_players = 15

    def add_player(self, player_id: int) -> bool:
        if self.started:
            return False

        if player_id in self.players:
            return False

        if len(self.players) >= self.max_players:
            return False

        self.players.append(player_id)
        return True

    def remove_player(self, player_id: int) -> bool:
        if player_id not in self.players:
            return False

        self.players.remove(player_id)
        return True

    def is_player(self, player_id: int) -> bool:
        return player_id in self.players

    def is_owner(self, player_id: int) -> bool:
        return self.owner_id == player_id

    def is_full(self) -> bool:
        return len(self.players) >= self.max_players

    def can_start(self) -> bool:
        return (
            not self.started
            and len(self.players) >= self.min_players
        )

    def transfer_owner(self) -> int | None:
        if not self.players:
            return None

        self.owner_id = self.players[0]
        return self.owner_id

    @property
    def player_count(self) -> int:
        return len(self.players)