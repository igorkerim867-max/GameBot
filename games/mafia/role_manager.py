from games.mafia.roles import *


ROLES = {

    RoleType.CIVILIAN: Role(
        RoleType.CIVILIAN,
        "Мирный",
        "👨",
        Team.CIVILIAN,
        "Найдите всю мафию.",
        False
    ),

    RoleType.MAFIA: Role(
        RoleType.MAFIA,
        "Мафия",
        "🔫",
        Team.MAFIA,
        "Каждую ночь выбирает жертву.",
        True
    ),

    RoleType.DON: Role(
        RoleType.DON,
        "Дон",
        "🤵",
        Team.MAFIA,
        "Возглавляет мафию.",
        True
    ),

    RoleType.DOCTOR: Role(
        RoleType.DOCTOR,
        "Доктор",
        "💉",
        Team.CIVILIAN,
        "Лечит одного игрока ночью.",
        True
    ),

    RoleType.SHERIFF: Role(
        RoleType.SHERIFF,
        "Шериф",
        "👮",
        Team.CIVILIAN,
        "Проверяет игроков.",
        True
    ),
    RoleType.HOOKER: Role(
        RoleType.HOOKER,
        "Проститутка",
        "💋",
        Team.CIVILIAN,
        "Проводит ночь с игроком. Он не сможет голосовать днём.",
        True
    ),
    RoleType.MANIAC: Role(
        RoleType.MANIAC,
        "Маньяк",
        "🔪",
        Team.CIVILIAN,
        "Убивает одного игрока каждую ночь.",
        True
    )
}
