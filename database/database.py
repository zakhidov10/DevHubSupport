import aiosqlite


DB_NAME = "devhub.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON")

        await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                support_type TEXT NOT NULL,
                text TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                admin_chat_id INTEGER,
                admin_message_id INTEGER
            )
        """)

        # Проверяем существующие колонки
        cursor = await db.execute("PRAGMA table_info(tickets)")
        columns = {row[1] for row in await cursor.fetchall()}

        # Если база старая, добавляем недостающие колонки
        if "support_type" not in columns:
            await db.execute(
                """
                ALTER TABLE tickets
                ADD COLUMN support_type TEXT NOT NULL DEFAULT 'Не указано'
                """
            )

        if "text" not in columns:
            await db.execute(
                """
                ALTER TABLE tickets
                ADD COLUMN text TEXT NOT NULL DEFAULT ''
                """
            )

        if "admin_chat_id" not in columns:
            await db.execute(
                "ALTER TABLE tickets ADD COLUMN admin_chat_id INTEGER"
            )

        if "admin_message_id" not in columns:
            await db.execute(
                "ALTER TABLE tickets ADD COLUMN admin_message_id INTEGER"
            )

        if "status" not in columns:
            await db.execute(
        """
        ALTER TABLE tickets
        ADD COLUMN status TEXT NOT NULL DEFAULT 'open'
        """
    )

        await db.execute("""
            CREATE TABLE IF NOT EXISTS ticket_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                sender_id INTEGER NOT NULL,
                sender_type TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (ticket_id)
                    REFERENCES tickets(id)
                    ON DELETE CASCADE
            )
        """)

        await db.commit()


async def create_ticket(
    user_id: int,
    support_type: str,
    text: str
) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            INSERT INTO tickets (
                user_id,
                support_type,
                text
            )
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                support_type,
                text
            )
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
        await db.execute(
            """
            INSERT INTO ticket_messages
            (ticket_id, sender_id, sender_type, text)
            VALUES (?, ?, ?, ?)
            """,
            (
                ticket_id,
                sender_id,
                sender_type,
                text
            )
        )

        await db.commit()


async def set_admin_message(
    ticket_id: int,
    admin_chat_id: int,
    admin_message_id: int
):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE tickets
            SET admin_chat_id = ?,
                admin_message_id = ?
            WHERE id = ?
            """,
            (
                admin_chat_id,
                admin_message_id,
                ticket_id
            )
        )

        await db.commit()


async def get_ticket_by_admin_message(
    admin_chat_id: int,
    admin_message_id: int
):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT id, user_id, status
            FROM tickets
            WHERE admin_chat_id = ?
              AND admin_message_id = ?
            """,
            (
                admin_chat_id,
                admin_message_id
            )
        )

        return await cursor.fetchone()


async def get_ticket(ticket_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT
                id,
                user_id,
                support_type,
                text,
                status,
                created_at,
                closed_at
            FROM tickets
            WHERE id = ?
            """,
            (ticket_id,)
        )

        return await cursor.fetchone()


async def close_ticket(ticket_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE tickets
            SET status = 'closed',
                closed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (ticket_id,)
        )

        await db.commit()


async def get_ticket_messages(ticket_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT
                id,
                sender_id,
                sender_type,
                text,
                created_at
            FROM ticket_messages
            WHERE ticket_id = ?
            ORDER BY id ASC
            """,
            (ticket_id,)
        )

        return await cursor.fetchall()


async def add_ticket(
    user_id: int,
    username: str,
    full_name: str,
    support_type: str,
    text: str,
    photo_id: str | None = None
) -> int:
    return await create_ticket(
        user_id=user_id,
        support_type=support_type,
        text=text
    )
