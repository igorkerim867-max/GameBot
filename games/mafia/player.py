from dataclasses import dataclass

from games.mafia.roles import Role


@dataclass
class MafiaPlayer:

    user_id: int

    role: Role | None = None

    alive: bool = True

    protected: bool = False

    silenced: bool = False

    voted: bool = False

    checked: bool = False

    can_vote: bool = True

    blocked_by_hooker: bool = False