from games.mafia.roles import RoleType


class PlayerService:

    def __init__(self, game):
        self.game = game

    def get_player(self, user_id):
        for player in self.game.players:
            if player.user_id == user_id:
                return player
        return None

    def alive_players(self):
        """Список всех живых игроков."""
        return [
            player
            for player in self.game.players
            if player.alive
        ]

    def mafia_players(self):
        return [
            player
            for player in self.game.players
            if (
                player.alive
                and player.role.role_type in (
                    RoleType.MAFIA,
                    RoleType.DON
            )
        )
    ]

    
    def civilians(self):
        return [
            player
            for player in self.game.players
            if (
                player.alive
                and player.role.role_type not in (
                    RoleType.MAFIA,
                    RoleType.DON
            )
        )
    ]

    def has_alive_role(self, role_type):
        return any(
            player.alive
            and player.role.role_type == role_type
            for player in self.game.players
    )

    def find_alive_role(self, role_type):
        for player in self.game.players:
            if (
                player.alive
                and player.role.role_type == role_type
        ):
                return player

        return None
    def find_alive_roles(self, role_type):
        return [
            player
            for player in self.game.players
            if (
                player.alive
                and player.role.role_type == role_type
            )
        ]

    def alive_count(self):
        return len(self.alive_players())

    def dead_players(self):
        return [
            player
            for player in self.game.players
            if not player.alive
        ]


    def role_count(self, role_type):
        return sum(
            1
            for player in self.alive_players()
            if player.role.role_type == role_type
        )