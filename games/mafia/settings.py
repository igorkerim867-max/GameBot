from dataclasses import dataclass


@dataclass(frozen=True)
class TimeSettings:
    night: int
    discussion: int
    vote: int
    warning: int = 10


MIN_PLAYERS = 4
MAX_PLAYERS = 15


TIME_SETTINGS = {
    range(4, 7): TimeSettings(
        night=30,
        discussion=60,
        vote=30,
    ),

    range(7, 10): TimeSettings(
        night=45,
        discussion=90,
        vote=45,
    ),

    range(10, 13): TimeSettings(
        night=60,
        discussion=120,
        vote=60,
    ),

    range(13, 16): TimeSettings(
        night=75,
        discussion=150,
        vote=75,
    ),
}


def get_time_settings(player_count: int) -> TimeSettings:

    for player_range, settings in TIME_SETTINGS.items():
        if player_count in player_range:
            return settings

    return TimeSettings(
        night=30,
        discussion=60,
        vote=30,
    )