from games.mafia.role_base import BaseRole
from games.mafia.roles import Team


class Mafia(BaseRole):

    name = "Мафия"

    emoji = "🔫"

    team = Team.MAFIA

    has_night_action = True

    async def night_action(self, engine, player):

        target = engine.actions.mafia_target

        if target is None:
            return

        if target.protected:
            return

        target.alive = False