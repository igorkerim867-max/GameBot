
from games.mafia.roles import Team, RoleType


async def check_win(game):
    alive = game.player_service.alive_players()

    mafia = [
        p for p in alive
        if p.role.team == Team.MAFIA
    ]

    civilians = [
        p for p in alive
        if p.role.team == Team.CIVILIAN
        and p.role.role_type != RoleType.MANIAC
    ]

    maniac = game.player_service.find_alive_role(
        RoleType.MANIAC
    )

    # Победа Маньяка
    if maniac and len(alive) == 2 and len(mafia) == 0:
        await game.game_over(
            "🔪 Маньяк уничтожил город и победил!"
        )
        return True

    if maniac and len(alive) == 1:
        await game.game_over(
            "🔪 Маньяк остался последним в живых!"
        )
        return True

    # Победа Мирных
    if len(mafia) == 0 and maniac is None:
        await game.game_over(
            "👨 Мирные жители уничтожили всех преступников!"
        )
        return True

    # Победа Мафии
    if len(mafia) >= len(civilians) + (1 if maniac else 0):
        await game.game_over(
            "🔫 Мафия захватила город!"
        )
        return True

    return False