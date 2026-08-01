from games.mafia.engine.night import process


async def finish_night(game):
    """
    Выполняет все ночные действия.
    """

    # Сброс временной защиты перед обработкой ночи
    for player in game.players:
        player.protected = False

    # Выполнить все ночные роли
    await process(game)