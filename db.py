import aiosqlite
import asyncio
from create_bot import dp



async def initialize_database():
    # Подключаемся к базе данных (если база данных не существует, она будет создана)
    async with aiosqlite.connect("users.db") as db:
        # Создаем таблицу users, если она не существует
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                phone_number TEXT
            )
        """)
        # Сохраняем изменения
        await db.commit()

async def add_user(telegram_id: int, username: str, first_name: str, phone_number: str):
    async with aiosqlite.connect("users.db") as db:
        await db.execute("""
            INSERT INTO users (telegram_id, username, first_name, phone_number)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO NOTHING
        """, (telegram_id, username, first_name, phone_number))
        await db.commit()

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
