from abc import ABC


class BaseRole(ABC):

    name = ""
    emoji = ""
    team = None

    has_night_action = False

    async def night_action(self, engine, player):
        """
        Выполнить ночное действие.
        """
        return

    async def on_morning(self, engine, player):
        """
        Вызывается утром.
        """
        return

    async def on_death(self, engine, player):
        """
        Вызывается после смерти игрока.
        """
        return