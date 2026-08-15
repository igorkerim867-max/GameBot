class BunkerPlayer:

    def __init__(self, user_id: int):

        self.user_id = user_id

        # ==========================================
        # ХАРАКТЕРИСТИКИ ПЕРСОНАЖА
        # ==========================================

        self.profession = None
        self.health = None
        self.biology = None
        self.hobby = None
        self.baggage = None
        self.phobia = None

        # ==========================================
        # СОСТОЯНИЕ ИГРОКА
        # ==========================================

        self.alive = True
        self.voted = False

        # Какие карты уже были раскрыты
        self.revealed = []

        # Попал ли игрок в Бункер
        self.in_bunker = False

    # ==========================================
    # ИЗГНАНИЕ
    # ==========================================

    def kill(self):

        self.alive = False
        self.voted = False

    # ==========================================
    # ПОПАДАНИЕ В БУНКЕР
    # ==========================================

    def enter_bunker(self):

        self.in_bunker = True

    # ==========================================
    # ПРОВЕРКИ
    # ==========================================

    def is_alive(self):

        return self.alive

    def is_exiled(self):

        return not self.alive

    def has_revealed(self, characteristic: str):

        return characteristic in self.revealed

    # ==========================================
    # РАСКРЫТИЕ КАРТЫ
    # ==========================================

    def reveal(self, characteristic: str):

        if characteristic in self.revealed:
            return False

        self.revealed.append(characteristic)

        return True