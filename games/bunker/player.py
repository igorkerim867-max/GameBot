class BunkerPlayer:

    def __init__(self, user_id):
        self.user_id = user_id

        # Карты персонажа
        self.superpower = None
        self.phobia = None
        self.character = None
        self.hobby = None
        self.baggage = None
        self.fact = None

        # Особое условие
        self.special_condition = None

        # Состояние игрока
        self.exiled = False
        self.revealed = []
        self.voted = False

    def reveal(self, card_type):

        if card_type not in self.revealed:
            self.revealed.append(card_type)

    def is_exiled(self):
        return self.exiled

    def exile(self):
        self.exiled = True