from games.mafia.role_base import BaseRole
from games.mafia.roles import Team


class Doctor(BaseRole):

    name = "Доктор"

    emoji = "💉"

    team = Team.CIVILIAN

    has_night_action = True

    async def night_action(self, engine, player):

        target = engine.actions.doctor_target

        if target is None:
            return

        target.protected = True