from database.database import get_connection


async def create_tables():

    db = await get_connection()

    await db.execute("""
    CREATE TABLE IF NOT EXISTS mafia_players (

        user_id INTEGER PRIMARY KEY,

        username TEXT NOT NULL,

        games INTEGER DEFAULT 0,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,

        rating INTEGER DEFAULT 1000,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_game TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS mafia_role_stats (

        user_id INTEGER PRIMARY KEY,

        mafia_kills INTEGER DEFAULT 0,

        doctor_saves INTEGER DEFAULT 0,

        sheriff_checks INTEGER DEFAULT 0,

        hooker_blocks INTEGER DEFAULT 0,

        civilian_wins INTEGER DEFAULT 0,

       mafia_wins INTEGER DEFAULT 0
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS mafia_achievements (

        user_id INTEGER NOT NULL,

        achievement_id TEXT NOT NULL,

        unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        PRIMARY KEY (
            user_id,
            achievement_id
        )
    )
    """) 

    await db.commit()
    await db.close()