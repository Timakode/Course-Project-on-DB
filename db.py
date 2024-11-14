import aiosqlite
import asyncio
from create_bot import dp



async def initialize_database():
    # Подключаемся к базе данных (если база данных не существует, она будет создана)
    async with aiosqlite.connect("users.db") as db:
        # Создаем таблицу users, если она не существует
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER NULL,
                username TEXT NULL,
                first_name TEXT,
                phone_number TEXT PRIMARY KEY
            )
        """)
        # Сохраняем изменения
        await db.commit()


async def add_user(first_name: str, phone_number: str, telegram_id: int, username: str):
    try:
        async with aiosqlite.connect("users.db") as db:
            async with db.execute("BEGIN"):
                await db.execute("""
                    INSERT INTO users (telegram_id, username, first_name, phone_number)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(phone_number) DO NOTHING
                """, (telegram_id, username, first_name, phone_number))
                await db.commit()
    except Exception as e:
        print(f"Error while adding user: {e}")


async def get_user_by_phone(phone_number: str):# Функция для получения пользователя по его тг-id
    async with aiosqlite.connect("users.db") as db:
        cursor = await db.execute("SELECT * FROM users WHERE phone_number = ?", (phone_number,))
        row = await cursor.fetchone()

        if row is None:
            print(f"Такого пользователя ещё нет в базе данных")
            return None

        # Преобразуем результат в словарь
        user = {
            "telegram_id": row[0],
            "username": row[1],
            "name": row[2],
            "phone_number": row[3],
        }
        return user

async def get_user_by_id(telegram_id: int):# Функция для получения пользователя по его тг-id
    async with aiosqlite.connect("users.db") as db:
        cursor = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        row = await cursor.fetchone()

        if row is None:
            print(f"Такого пользователя ещё нет в базе данных")
            return None

        # Преобразуем результат в словарь
        user = {
            "telegram_id": row[0],
            "username": row[1],
            "name": row[2],
            "phone_number": row[3],
        }
        return user