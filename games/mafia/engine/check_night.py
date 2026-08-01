from games.mafia.roles import RoleType


async def check_night(game):
    """
    Проверяет, сделали ли все живые ночные роли свой выбор.
    """

    # Все живые мафии
    alive_mafia = game.player_service.mafia_players()

    mafia_ready = (
        len(game.night_state.mafia_targets) == len(alive_mafia)
    )

    # Все живые доктора
    alive_doctors = game.player_service.find_alive_roles(
        RoleType.DOCTOR
    )

    doctor_ready = (
        len(game.night_state.doctor_targets) == len(alive_doctors)
    )

    # Все живые шерифы
    alive_sheriffs = game.player_service.find_alive_roles(
        RoleType.SHERIFF
    )

    sheriff_ready = (
        len(game.night_state.sheriff_targets) == len(alive_sheriffs)
    )

    # Все живые проститутки
    alive_hookers = game.player_service.find_alive_roles(
        RoleType.HOOKER
    )

    hooker_ready = (
        len(game.night_state.hooker_targets) == len(alive_hookers)
    )

    # Маньяк (он один)
    alive_maniac = game.player_service.find_alive_role(
        RoleType.MANIAC
    )

    maniac_ready = (
        alive_maniac is None
        or game.night_state.maniac_target is not None
    )

    if all((
        mafia_ready,
        doctor_ready,
        sheriff_ready,
        hooker_ready,
        maniac_ready,
    )):
        await game.finish_night()