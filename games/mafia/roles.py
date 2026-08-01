from dataclasses import dataclass
from enum import Enum, auto


class Team(Enum):
    CIVILIAN = auto()
    MAFIA = auto()


class RoleType(Enum):
    CIVILIAN = auto()
    MAFIA = auto()
    DON = auto()
    DOCTOR = auto()
    SHERIFF = auto()
    HOOKER = auto()
    MANIAC = auto()


@dataclass(frozen=True)
class Role:
    role_type: RoleType
    name: str
    emoji: str
    team: Team
    description: str
    has_night_action: bool