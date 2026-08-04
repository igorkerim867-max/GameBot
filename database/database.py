import aiosqlite


DATABASE = "database/mafia.db"


async def get_connection():
    return await aiosqlite.connect(DATABASE)