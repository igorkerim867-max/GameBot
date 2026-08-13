class BunkerPlayer:

    def __init__(self, user_id):
        self.user_id = user_id

        # Характеристики игрока
        self.profession = None
        self.health = None
        self.character = None
        self.baggage = None
        self.hobby = None
        self.special = None
        self.additional_info = None

        # Состояние игрока
        self.alive = True
        self.revealed = []
        self.voted = False

    def reveal(self, characteristic):
        """
        Открыть одну из своих характеристик.
        """
        if characteristic not in self.revealed:
            self.revealed.append(characteristic)

    def is_alive(self):
        return self.alive

    def kill(self):
        self.alive = False