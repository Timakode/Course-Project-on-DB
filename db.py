import asyncpg
from decouple import config
from datetime import datetime, timedelta, date
import logging
from faker import Faker
import random


# Инициализация Faker
fake = Faker('ru_RU')

# Настройка логирования
logging.basicConfig(level=logging.INFO)


# Загрузка параметров подключения из файла .env
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_NAME = config('DB_NAME')
DB_HOST = config('DB_HOST')
DB_PORT = config('DB_PORT', default=5432)

async def initialize_database():
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE,
                username TEXT,
                first_name TEXT,
                phone_number TEXT UNIQUE
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS cars (
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                car_number TEXT PRIMARY KEY,
                car_brand TEXT,
                car_model TEXT,
                car_year INTEGER,
                car_color TEXT,
                wrapped_car TEXT,
                repainted_car TEXT
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id SERIAL PRIMARY KEY,
                car_number TEXT REFERENCES cars(car_number) ON DELETE CASCADE,
                date DATE,
                post_number INTEGER,
                service_description TEXT,
                status TEXT CHECK(status IN ('запланировано', 'в работе', 'завершено', 'отменено')) DEFAULT 'запланировано'
            );
        """)
    finally:
        await conn.close()

async def add_user(first_name: str, phone_number: str, telegram_id: int, username: str):
    try:
        conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
        await conn.execute("""
            INSERT INTO users (telegram_id, username, first_name, phone_number)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT(phone_number) DO NOTHING
        """, telegram_id, username, first_name, phone_number)
    except Exception as e:
        logging.error(f"Error while adding user: {e}")
    finally:
        await conn.close()

async def get_user_by_phone(phone_number: str):
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        row = await conn.fetchrow("SELECT * FROM users WHERE phone_number = $1", phone_number)

        if row is None:
            logging.error(f"Такого пользователя ещё нет в базе данных")
            return None

        user = {
            "id": row['id'],
            "telegram_id": row['telegram_id'],
            "username": row['username'],
            "name": row['first_name'],
            "phone_number": row['phone_number'],
        }
        return user
    finally:
        await conn.close()

async def get_user_by_id(telegram_id: int):
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        row = await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)

        if row is None:
            logging.error(f"Такого пользователя ещё нет в базе данных")
            return None

        user = {
            "id": row['id'],
            "telegram_id": row['telegram_id'],
            "username": row['username'],
            "name": row['first_name'],
            "phone_number": row['phone_number'],
        }
        return user
    finally:
        await conn.close()

async def update_phone(old_phone_number: str, new_phone_number: str):
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        exists = await conn.fetchval("SELECT 1 FROM users WHERE phone_number = $1", new_phone_number)

        if exists:
            raise ValueError(f"Номер {new_phone_number} уже существует в базе данных.")

        await conn.execute("""
            UPDATE users
            SET phone_number = $1
            WHERE phone_number = $2
        """, new_phone_number, old_phone_number)
    finally:
        await conn.close()

async def add_car(car_number: str, user_id: int, car_brand: str, car_model: str, car_year: str, car_color: str, wrapped_car: str, repainted_car: str):
    try:
        conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
        await conn.execute("""
            INSERT INTO cars (user_id, car_number, car_brand, car_model, car_year, car_color, wrapped_car, repainted_car)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT(car_number) DO NOTHING
        """, user_id, car_number, car_brand, car_model, int(car_year), car_color, wrapped_car, repainted_car)
    except Exception as e:
        logging.error(f"Error while adding car: {e}")
    finally:
        await conn.close()


async def get_car_by_number(car_number: str):
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        row = await conn.fetchrow("SELECT * FROM cars WHERE car_number = $1", car_number)

        if row is None:
            logging.error(f"Такого авто нет в базе данных")
            return None

        car = {
            "user_id": row['user_id'],
            "car_number": row['car_number'],
            "car_brand": row['car_brand'],
            "car_model": row['car_model'],
            "car_year": row['car_year'],
            "car_color": row['car_color'],
            "wrapped_car": row['wrapped_car'],
            "repainted_car": row['repainted_car'],
        }
        return car
    finally:
        await conn.close()

async def get_client_and_cars_by_phone(phone_number: str):
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        query = """
        SELECT users.id, users.telegram_id, users.username, users.first_name, users.phone_number,
               cars.car_number, cars.car_brand, cars.car_model, cars.car_year, cars.car_color
        FROM users
        LEFT JOIN cars ON users.id = cars.user_id
        WHERE users.phone_number = $1;
        """
        rows = await conn.fetch(query, phone_number)

        if not rows:
            logging.error(f"Такого пользователя ещё нет в базе данных")
            return None

        client_info = {
            "user": {
                "id": rows[0]['id'],
                "telegram_id": rows[0]['telegram_id'],
                "username": rows[0]['username'],
                "first_name": rows[0]['first_name'],
                "phone_number": rows[0]['phone_number'],
            },
            "cars": []
        }

        for row in rows:
            car = {
                "car_number": row['car_number'],
                "car_brand": row['car_brand'],
                "car_model": row['car_model'],
                "car_year": row['car_year'],
                "car_color": row['car_color'],
            }
            if car["car_number"] is not None:
                client_info["cars"].append(car)

        return client_info
    finally:
        await conn.close()

async def get_car_and_owner_by_number(car_number: str):
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        query = """
        SELECT cars.user_id, cars.car_number, cars.car_brand, cars.car_model, cars.car_year, cars.car_color,
               users.id, users.telegram_id, users.username, users.first_name, users.phone_number
        FROM cars
        LEFT JOIN users ON cars.user_id = users.id
        WHERE cars.car_number = $1;
        """
        row = await conn.fetchrow(query, car_number)

        if row is None:
            logging.error(f"Такого авто нет в базе данных")
            return None

        car_info = {
            "car": {
                "user_id": row['user_id'],
                "car_number": row['car_number'],
                "car_brand": row['car_brand'],
                "car_model": row['car_model'],
                "car_year": row['car_year'],
                "car_color": row['car_color'],
            },
            "owner": {
                "id": row['id'],
                "telegram_id": row['telegram_id'],
                "username": row['username'],
                "first_name": row['first_name'],
                "phone_number": row['phone_number'],
            }
        }

        return car_info
    finally:
        await conn.close()

async def get_available_dates():
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        today = datetime.now().date()
        free_dates = []

        for i in range(30):
            date_obj = today + timedelta(days=i)
            count = await conn.fetchval("""
                SELECT COUNT(DISTINCT post_number) FROM bookings WHERE date = $1
            """, date_obj)

            if count < 5:
                free_dates.append(date_obj)

        return free_dates
    finally:
        await conn.close()

async def get_client_by_id(user_id: int):
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)

        if row:
            client = dict(row)
            return client
        return None
    finally:
        await conn.close()

async def get_cars_by_client(user_id: int):
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        cars = await conn.fetch("SELECT * FROM cars WHERE user_id = $1", user_id)
        return [dict(car) for car in cars] if cars else []
    finally:
        await conn.close()

async def add_booking(booking_date: date, car_number: str, client_id: int, service_description: str):
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        taken_posts = await conn.fetch("""
            SELECT post_number FROM bookings WHERE date = $1 ORDER BY post_number
        """, booking_date)

        if len(taken_posts) >= 5:
            return False

        all_posts = {1, 2, 3, 4, 5}
        taken_posts_set = set(post['post_number'] for post in taken_posts)
        free_posts = all_posts - taken_posts_set
        post_number = min(free_posts)

        await conn.execute("""
            INSERT INTO bookings (car_number, date, service_description, post_number, status)
            VALUES ($1, $2, $3, $4, $5)
        """, car_number, booking_date, service_description, post_number, 'запланировано')
        return True
    finally:
        await conn.close()


async def get_active_bookings():
    query = """
    SELECT
        b.status,
        b.date AS booking_date,
        b.service_description,
        c.car_brand,
        c.car_model,
        c.car_year,
        c.car_color,
        c.car_number,
        u.first_name,
        u.phone_number,
        u.username
    FROM bookings b
    JOIN cars c ON b.car_number = c.car_number
    JOIN users u ON c.user_id = u.id
    WHERE b.status IN ('запланировано', 'в работе')
    ORDER BY
        CASE
            WHEN b.status = 'в работе' THEN 1
            WHEN b.status = 'запланировано' THEN 2
        END,
        b.date ASC;
    """
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        bookings = await conn.fetch(query)
        return bookings
    finally:
        await conn.close()

async def cancel_booking(booking_id: int):
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        await conn.execute("""
            UPDATE bookings
            SET status = $1
            WHERE id = $2
        """, 'отменено', booking_id)
    finally:
        await conn.close()

async def get_all_active_bookings():
    query = """
    SELECT
        b.id AS booking_id,
        b.date AS booking_date,
        b.service_description,
        c.car_brand,
        c.car_number,
        u.first_name,
        u.phone_number
    FROM bookings b
    JOIN cars c ON b.car_number = c.car_number
    JOIN users u ON c.user_id = u.id
    WHERE b.status NOT IN ('отменено', 'завершено')
    ORDER BY b.date ASC;
    """
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        bookings = await conn.fetch(query)
        return bookings
    finally:
        await conn.close()

async def get_scheduled_bookings():
    query = """
    SELECT
        b.id AS booking_id,
        b.date AS booking_date,
        b.service_description,
        c.car_brand,
        c.car_number,
        u.first_name,
        u.phone_number
    FROM bookings b
    JOIN cars c ON b.car_number = c.car_number
    JOIN users u ON c.user_id = u.id
    WHERE b.status = 'запланировано'
    ORDER BY b.date ASC;
    """
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        bookings = await conn.fetch(query)
        return bookings
    finally:
        await conn.close()

async def get_booking_by_id(booking_id):
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        booking = await conn.fetchrow("SELECT * FROM bookings WHERE id = $1", booking_id)
        return booking
    finally:
        await conn.close()

async def delete_booking(booking_id):
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        await conn.execute("DELETE FROM bookings WHERE id = $1", booking_id)
    finally:
        await conn.close()

async def complete_booking(booking_id: int):
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        await conn.execute("""
            UPDATE bookings
            SET status = $1
            WHERE id = $2
        """, 'завершено', booking_id)
    finally:
        await conn.close()

async def get_total_bookings():
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        total = await conn.fetchval("SELECT COUNT(*) FROM bookings;")
        return total
    finally:
        await conn.close()

async def get_completed_bookings():
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        completed = await conn.fetchval("SELECT COUNT(*) FROM bookings WHERE status = 'завершено';")
        return completed
    finally:
        await conn.close()

async def get_cancelled_bookings():
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        cancelled = await conn.fetchval("SELECT COUNT(*) FROM bookings WHERE status = 'отменено';")
        return cancelled
    finally:
        await conn.close()

async def get_bookings_by_date_range(start_date: date, end_date: date):
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        bookings = await conn.fetch("""
            SELECT
                b.status,
                b.car_number,
                c.car_brand,
                c.car_model,
                u.first_name,
                u.phone_number
            FROM bookings b
            INNER JOIN cars c ON b.car_number = c.car_number
            INNER JOIN users u ON c.user_id = u.id
            WHERE b.date BETWEEN $1 AND $2
        """, start_date, end_date)

        most_frequent_car = await conn.fetchrow("""
            SELECT
                b.car_number,
                COUNT(*) as count,
                c.car_brand,
                c.car_model,
                u.first_name,
                u.phone_number
            FROM bookings b
            INNER JOIN cars c ON b.car_number = c.car_number
            INNER JOIN users u ON c.user_id = u.id
            WHERE b.date BETWEEN $1 AND $2 AND b.status IN ('запланировано', 'в работе', 'завершено')
            GROUP BY b.car_number
            ORDER BY count DESC
            LIMIT 1
        """, start_date, end_date)

        return bookings, most_frequent_car
    finally:
        await conn.close()

async def get_bookings_by_car_number(car_number: str):
    one_year_ago = (datetime.now() - timedelta(days=365)).date()
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        bookings = await conn.fetch("""
                SELECT
                    b.*,
                    u.first_name,
                    u.phone_number
                FROM bookings b
                LEFT JOIN cars c ON b.car_number = c.car_number
                LEFT JOIN users u ON c.user_id = u.id
                WHERE b.car_number LIKE $1
            """, car_number)

        count_last_year = await conn.fetchval("""
                SELECT COUNT(*)
                FROM bookings
                WHERE car_number LIKE $1
                  AND status IN ('запланировано', 'в работе', 'завершено')
                  AND date >= $2
            """, car_number, one_year_ago)

        if not bookings:
            return [], count_last_year, None, None

        owner = await conn.fetchrow("""
                SELECT u.first_name, u.phone_number
                FROM users u
                JOIN cars c ON u.id = c.user_id
                WHERE c.car_number LIKE $1
            """, car_number)

        owner_name = owner['first_name'] if owner else None
        owner_phone = owner['phone_number'] if owner else None

        return bookings, count_last_year, owner_name, owner_phone
    finally:
        await conn.close()

async def get_most_frequent_car():
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        most_frequent = await conn.fetchrow("""
            SELECT car_number, COUNT(*) as count
            FROM bookings
            GROUP BY car_number
            ORDER BY count DESC
            LIMIT 1;
        """)
        return most_frequent
    finally:
        await conn.close()


async def get_bookings_by_brand(car_brands):
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        query = """
            SELECT bookings.id, bookings.car_number, bookings.date, bookings.post_number, bookings.service_description, bookings.status
            FROM bookings
            INNER JOIN cars ON bookings.car_number = cars.car_number
            WHERE cars.car_brand IN ($1)
            AND bookings.date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '1 month'
        """
        bookings = await conn.fetch(query, car_brands)
        return bookings
    finally:
        await conn.close()










async def generate_fake_data():
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        # Генерация пользователей
        users = []
        unique_telegram_ids = set()
        unique_phone_numbers = set()

        while len(users) < 10000:
            telegram_id = fake.random_int(min=100000000, max=999999999)
            phone_number = f"+7{fake.random_int(min=9000000000, max=9999999999)}"

            if telegram_id not in unique_telegram_ids and phone_number not in unique_phone_numbers:
                unique_telegram_ids.add(telegram_id)
                unique_phone_numbers.add(phone_number)
                username = fake.user_name()
                first_name = fake.first_name()
                users.append((telegram_id, username, first_name, phone_number))

        await conn.executemany("""
            INSERT INTO users (telegram_id, username, first_name, phone_number)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (phone_number) DO NOTHING
        """, users)

        # Получение всех user_id
        user_ids = await conn.fetch("SELECT id FROM users")
        user_ids = [user['id'] for user in user_ids]

        # Генерация автомобилей
        cars = []
        unique_car_numbers = set()

        for user_id in user_ids:
            car_number = fake.license_plate()

            if car_number not in unique_car_numbers:
                unique_car_numbers.add(car_number)
                car_brand = fake.company()
                car_model = fake.word()
                car_year = fake.random_int(min=1990, max=2023)
                car_color = fake.color_name()
                wrapped_car = random.choice(["Полностью", "Частично", "Нет"])
                repainted_car = random.choice(["Да", "Нет"])
                cars.append((user_id, car_number, car_brand, car_model, car_year, car_color, wrapped_car, repainted_car))

        await conn.executemany("""
            INSERT INTO cars (user_id, car_number, car_brand, car_model, car_year, car_color, wrapped_car, repainted_car)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (car_number) DO NOTHING
        """, cars)

        # Генерация записей
        bookings = []
        today = datetime.now().date()

        for car_number in unique_car_numbers:
            for _ in range(random.randint(1, 5)):  # Генерируем от 1 до 5 записей для каждого автомобиля
                date = today + timedelta(days=random.randint(0, 30))  # Записи на месяц вперед
                post_number = random.randint(1, 5)
                service_description = random.choice(["Химчистка", "Тонировка", "Оклейка", "Полировка", "Мойка"])

                # Проверка наличия записи перед вставкой
                existing_booking = await conn.fetchrow("""
                    SELECT 1 FROM bookings WHERE car_number = $1 AND date = $2
                """, car_number, date)

                if not existing_booking:
                    bookings.append((car_number, date, post_number, service_description))

        await conn.executemany("""
            INSERT INTO bookings (car_number, date, post_number, service_description, status)
            VALUES ($1, $2, $3, $4, 'запланировано')
        """, bookings)

    finally:
        await conn.close()

async def clear_all_data():
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST, port=DB_PORT)
    try:
        await conn.execute("TRUNCATE TABLE bookings RESTART IDENTITY CASCADE;")
        await conn.execute("TRUNCATE TABLE cars RESTART IDENTITY CASCADE;")
        await conn.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE;")
    finally:
        await conn.close()