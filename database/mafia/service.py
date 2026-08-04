from database.database import get_connection


class MafiaStatsService:

    async def player_exists(self, user_id: int) -> bool:

        db = await get_connection()

        cursor = await db.execute(
            "SELECT 1 FROM mafia_players WHERE user_id = ?",
            (user_id,)
        )

        player = await cursor.fetchone()

        await db.close()

        return player is not None


    async def create_player(self, user_id: int, username: str):

        db = await get_connection()

        await db.execute(
            """
            INSERT INTO mafia_players (
                user_id,
                username
            )
            VALUES (?, ?)
            """,
            (
                user_id,
                username
            )
        )

        await db.commit()
        await db.close()


    async def get_player(self, user_id: int):

        db = await get_connection()

        cursor = await db.execute(
            """
            SELECT *
            FROM mafia_players
            WHERE user_id = ?
            """,
            (user_id,)
        )

        player = await cursor.fetchone()

        await db.close()

        return player
    async def update_username(
        self,
        user_id: int,
        username: str
    ):

        db = await get_connection()

        await db.execute(
            """
            UPDATE mafia_players
            SET username = ?
            WHERE user_id = ?
            """,
            (
                username,
                user_id
            )
        )

        await db.commit()
        await db.close()
    async def add_game(
        self,
        user_id: int
    ):

        db = await get_connection()

        await db.execute(
            """
            UPDATE mafia_players
            SET
                games = games + 1,
                last_game = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """,
            (user_id,)
        )

        await db.commit()
        await db.close()
    async def add_win(self, user_id: int):

        db = await get_connection()

        await db.execute(
            """
            UPDATE mafia_players
            SET wins = wins + 1
            WHERE user_id = ?
            """,
            (user_id,)
        )

        await db.commit()
        await db.close()
    async def add_loss(self, user_id: int):

        db = await get_connection()

        await db.execute(
            """
            UPDATE mafia_players
            SET losses = losses + 1
            WHERE user_id = ?
            """,
            (user_id,)
        )

        await db.commit()
        await db.close()
    async def has_achievement(
        self,
        user_id: int,
        achievement_id: str
    ):

        db = await get_connection()

        cursor = await db.execute(
            """
            SELECT 1
            FROM mafia_achievements
            WHERE user_id = ?
            AND achievement_id = ?
            """,
            (
                user_id,
                achievement_id
            ) 
        )

        result = await cursor.fetchone()

        await db.close()

        return result is not None
    async def unlock_achievement(
        self,
        user_id: int,
        achievement_id: str
    ):

        db = await get_connection()

        await db.execute(
            """
            INSERT INTO mafia_achievements(
                user_id,
                achievement_id
            )
            VALUES (?, ?)
            """,
            (
                user_id,
                achievement_id
            )
        )

        await db.commit()
        await db.close()