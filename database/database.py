import aiosqlite

DB_NAME = "devhub.db"

async def create_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGRER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGRER NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            closed_at TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS ticket_message (
                id INTEGRER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGRER NOT NULL,
                sender_id INTEGRER NOT NULL,
                sender_type TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN_KEY (TICKET_ID)
                    REFERENCES tickets(id)
                    ON DELETE CASCADE
            )
        """)

        await db.commit()

async def create_ticket(user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor =  await db.execute(
            """
            INSERT INTO tickets (user_id)
            VALUES (?)
            """,
            (user_id, )
        )

        await db.commit()

        return cursor.lastrowid


async def add_ticket_message(
        ticket_id: int,
        sender_id: int,
        sender_type: str,
        text: str
):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO ticket_messages
            (ticket_id, sender_id, sender_type, text)
            VALUES(?, ?, ?, ?)
            """,
            (
                    ticket_id,
                    sender_id,
                    sender_type,
                    text
            )
        )
        await db.commit()

async def get_ticket(ticket_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT id, user_id, status, created_at, closed_at
            FROM tickets
            WHERE id = ?
            """,
            (ticket_id, )
        )

        return await cursor.fetchone()

async def close_ticket(ticket_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE tickets
            SET status = "closed",
                closed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (ticket_id, )
        )
        await db.commit()

async def get_ticket_message(ticket_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT id, sender_id, sender_type, text, created_at
            FROM ticket_message
            WHERE ticket_id = ?
            ORDER BY id ASC
            """,
            (ticket_id, )
        )

        return await cursor.fetchall