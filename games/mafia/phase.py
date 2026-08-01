from enum import Enum


class Phase(Enum):

    WAITING = 0

    NIGHT = 1

    DAY = 2

    VOTING = 3

    END = 4