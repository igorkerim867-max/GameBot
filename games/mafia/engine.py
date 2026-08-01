from enum import Enum, auto


class GameState(Enum):
    WAITING = auto()
    STARTING = auto()
    NIGHT = auto()
    MORNING = auto()
    DAY = auto()
    VOTING = auto()
    FINISHED = auto()


class MafiaEngine:

    def __init__(self, game):

        self.game = game

        self.state = GameState.WAITING

        self.day = 0

        self.night = 0

    # ============================
    # Смена состояний
    # ============================

    async def start_game(self):

        self.state = GameState.STARTING

        self.day = 1

        self.night = 0

    async def start_night(self):

        self.state = GameState.NIGHT

        self.night += 1

    async def finish_night(self):

        self.state = GameState.MORNING

    async def start_day(self):

        self.state = GameState.DAY

    async def start_voting(self):

        self.state = GameState.VOTING

    async def finish_game(self):

        self.state = GameState.FINISHED