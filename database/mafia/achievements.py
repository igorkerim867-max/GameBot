from dataclasses import dataclass


@dataclass(frozen=True)
class Achievement:
    id: str
    name: str
    description: str
    points: int
    rarity: str

    hidden: bool = False
    max_progress: int = 1
COMMON = "common"
RARE = "rare"
EPIC = "epic"
LEGENDARY = "legendary"
SECRET = "secret"
GENERAL = {

    "FIRST_GAME": Achievement(
        id="FIRST_GAME",
        name="🎮 Первая игра",
        description="Сыграйте свою первую игру.",
        points=5,
        rarity=COMMON
    ),

    "FIRST_WIN": Achievement(
        id="FIRST_WIN",
        name="🏆 Первая победа",
        description="Одержите свою первую победу.",
        points=5,
        rarity=COMMON
    ),

    "GAMES_10": Achievement(
        id="GAMES_10",
        name="🎲 Новичок",
        description="Сыграйте 10 игр.",
        points=10,
        rarity=COMMON
    ),

    "GAMES_50": Achievement(
        id="GAMES_50",
        name="🏅 Опытный игрок",
        description="Сыграйте 50 игр.",
        points=20,
        rarity=RARE
    ),

    "GAMES_100": Achievement(
        id="GAMES_100",
        name="👑 Ветеран",
        description="Сыграйте 100 игр.",
        points=40,
        rarity=EPIC
    ),
}
MAFIA = {

    "FIRST_KILL": Achievement(
        id="FIRST_KILL",
        name="🩸 Первая кровь",
        description="Совершите первое успешное убийство.",
        points=10,
        rarity=COMMON
    ),

    "KILLS_10": Achievement(
        id="KILLS_10",
        name="🔪 Наёмник",
        description="Совершите 10 успешных убийств.",
        points=20,
        rarity=RARE,
        max_progress=10
    ),

    "KILLS_100": Achievement(
        id="KILLS_100",
        name="☠ Безжалостный",
        description="Совершите 100 успешных убийств.",
        points=50,
        rarity=EPIC,
        max_progress=100
    ),
}
DOCTOR = {

    "FIRST_SAVE": Achievement(
        id="FIRST_SAVE",
        name="💉 Первый пациент",
        description="Успешно спасите игрока.",
        points=10,
        rarity=COMMON
    ),

    "SAVE_10": Achievement(
        id="SAVE_10",
        name="❤️ Спаситель",
        description="Спасите 10 игроков.",
        points=20,
        rarity=RARE
    ),
}
SHERIFF = {

    "FIRST_CHECK": Achievement(
        id="FIRST_CHECK",
        name="🔍 Первая проверка",
        description="Проведите первую проверку.",
        points=10,
        rarity=COMMON
    ),
}
HOOKER = {

    "FIRST_VISIT": Achievement(
        id="FIRST_VISIT",
        name="💋 Первый визит",
        description="Используйте способность впервые.",
        points=10,
        rarity=COMMON
    ),
}
CIVILIAN = {

    "SURVIVOR": Achievement(
        id="SURVIVOR",
        name="🪖 Выживший",
        description="Победите, оставшись в живых.",
        points=15,
        rarity=RARE
    ),
}
SECRET = {

    "FIRST_NIGHT_DEATH": Achievement(
        id="FIRST_NIGHT_DEATH",
        name="💀 Не повезло",
        description="Погибните в первую ночь.",
        points=15,
        rarity=SECRET
    ),
}
LEGENDARY = {

    "LAST_DON": Achievement(
        id="LAST_DON",
        name="👑 Последний Дон",
        description=(
            "Останьтесь последним живым "
            "представителем мафии "
            "и приведите её к победе."
        ),
        points=100,
        rarity=LEGENDARY,
        hidden=True
    ),

    "PERFECT_GAME": Achievement(
        id="PERFECT_GAME",
        name="⭐ Идеальная игра",
        description=(
            "Победите, не получив "
            "ни одного голоса "
            "за всю партию."
        ),
        points=125,
        rarity=LEGENDARY,
        hidden=True
    ),

    "MASTER_OF_MAFIA": Achievement(
        id="MASTER_OF_MAFIA",
        name="🏆 Мастер мафии",
        description=(
            "Получите все достижения "
            "игры «Мафия»."
        ),
        points=250,
        rarity=LEGENDARY,
        hidden=True
    ),

}
ACHIEVEMENTS = {}

ACHIEVEMENTS.update(GENERAL)
ACHIEVEMENTS.update(MAFIA)
ACHIEVEMENTS.update(DOCTOR)
ACHIEVEMENTS.update(SHERIFF)
ACHIEVEMENTS.update(HOOKER)
ACHIEVEMENTS.update(CIVILIAN)
ACHIEVEMENTS.update(SECRET)
ACHIEVEMENTS.update(LEGENDARY)
def get_progress(achievement: Achievement, stats: dict):

    if achievement.id == "FIRST_GAME":
        progress = min(stats.get("games", 0), 1)

    elif achievement.id == "FIRST_WIN":
        progress = min(stats.get("wins", 0), 1)

    elif achievement.id == "GAMES_10":
        progress = min(stats.get("games", 0), 10)

    elif achievement.id == "GAMES_50":
        progress = min(stats.get("games", 0), 50)

    elif achievement.id == "GAMES_100":
        progress = min(stats.get("games", 0), 100)

    else:
        progress = 0

    return {
        "progress": progress,
        "remaining": max(0, achievement.max_progress - progress),
        "completed": progress >= achievement.max_progress
    }