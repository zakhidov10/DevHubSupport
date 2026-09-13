import aiosqlite


DB_NAME = "devhub.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON")

        # Пользователи
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                username TEXT,
                full_name TEXT,
                is_admin INTEGER NOT NULL DEFAULT 0
            )
        """)

        # Тикеты
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                support_type TEXT NOT NULL,
                text TEXT NOT NULL,
                photo_id TEXT,
                status TEXT NOT NULL DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                admin_chat_id INTEGER,
                admin_message_id INTEGER,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # Сообщения внутри тикетов
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


# =========================
# USERS
# =========================

async def add_user(
    user_id: int,
    username: str | None,
    full_name: str
):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO users (
                user_id,
                username,
                full_name
            )
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name
        """, (
            user_id,
            username,
            full_name
        ))

        await db.commit()


async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT
                id,
                user_id,
                username,
                full_name,
                is_admin
            FROM users
            WHERE user_id = ?
        """, (user_id,))

        return await cursor.fetchone()


async def is_admin(user_id: int) -> bool:
    user = await get_user(user_id)

    if user is None:
        return False

    return user[4] == 1


# =========================
# TICKETS
# =========================

async def create_ticket(
    user_id: int,
    support_type: str,
    text: str,
    photo_id: str | None = None
) -> int:

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            INSERT INTO tickets (
                user_id,
                support_type,
                text,
                photo_id
            )
            VALUES (?, ?, ?, ?)
        """, (
            user_id,
            support_type,
            text,
            photo_id
        ))

        await db.commit()

        return cursor.lastrowid


async def get_ticket(ticket_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT
                id,
                user_id,
                support_type,
                text,
                photo_id,
                status,
                created_at,
                closed_at,
                admin_chat_id,
                admin_message_id
            FROM tickets
            WHERE id = ?
        """, (ticket_id,))

        return await cursor.fetchone()


async def set_admin_message(
    ticket_id: int,
    admin_chat_id: int,
    admin_message_id: int
):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE tickets
            SET
                admin_chat_id = ?,
                admin_message_id = ?
            WHERE id = ?
        """, (
            admin_chat_id,
            admin_message_id,
            ticket_id
        ))

        await db.commit()


async def get_ticket_by_admin_message(
    admin_chat_id: int,
    admin_message_id: int
):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT
                id,
                user_id,
                status
            FROM tickets
            WHERE admin_chat_id = ?
              AND admin_message_id = ?
        """, (
            admin_chat_id,
            admin_message_id
        ))

        return await cursor.fetchone()


async def close_ticket(ticket_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE tickets
            SET
                status = 'closed',
                closed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (ticket_id,))

        await db.commit()


# =========================
# TICKET MESSAGES
# =========================

async def add_ticket_message(
    ticket_id: int,
    sender_id: int,
    sender_type: str,
    text: str
):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO ticket_messages (
                ticket_id,
                sender_id,
                sender_type,
                text
            )
            VALUES (?, ?, ?, ?)
        """, (
            ticket_id,
            sender_id,
            sender_type,
            text
        ))

        await db.commit()


async def get_ticket_messages(ticket_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT
                id,
                sender_id,
                sender_type,
                text,
                created_at
            FROM ticket_messages
            WHERE ticket_id = ?
            ORDER BY id ASC
        """, (ticket_id,))

        return await cursor.fetchall()