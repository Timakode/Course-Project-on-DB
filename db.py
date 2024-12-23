import aiosqlite
from datetime import datetime, timedelta

async def initialize_database():
    # Подключаемся к базе данных (если база данных не существует, она будет создана)
    async with aiosqlite.connect("users.db") as db:
        # Создаем таблицу users
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,  -- Telegram ID должен быть уникальным
                username TEXT,
                first_name TEXT,
                phone_number TEXT UNIQUE      -- Если phone_number также уникальный
            );
        """)

        # Создаем таблицу cars
        await db.execute("""
                    CREATE TABLE IF NOT EXISTS cars (
                        user_id INTEGER,  -- Ссылка на id пользователя из таблицы users
                        car_number TEXT PRIMARY KEY,
                        car_brand TEXT,
                        car_model TEXT,
                        car_year INTEGER,
                        car_color TEXT,
                        wrapped_car TEXT,
                        repainted_car TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    );
                """)

        # Таблица записей
        await db.execute("""
                    CREATE TABLE IF NOT EXISTS bookings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        car_number TEXT,
                        date TEXT,
                        post_number INTEGER,
                        service_description TEXT,
                        status TEXT CHECK(status IN ('запланировано', 'в работе', 'завершено', 'отменено')) DEFAULT 'запланировано',
                        FOREIGN KEY (car_number) REFERENCES cars(car_number) ON DELETE CASCADE
                    );
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
            "id": row[0],
            "telegram_id": row[1],
            "username": row[2],
            "name": row[3],
            "phone_number": row[4],
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
            "id": row[0],
            "telegram_id": row[1],
            "username": row[2],
            "name": row[3],
            "phone_number": row[4],
        }
        return user

async def update_phone(old_phone_number: str, new_phone_number: str):
    async with aiosqlite.connect("users.db") as db:
        # Проверяем, существует ли новый номер в таблице
        cursor = await db.execute("""
        SELECT 1 FROM users WHERE phone_number = ?;
        """, (new_phone_number,))
        exists = await cursor.fetchone()
        await cursor.close()

        if exists:
            raise ValueError(f"Номер {new_phone_number} уже существует в базе данных.")

        # Выполняем обновление
        await db.execute("""
        UPDATE users
        SET phone_number = ?
        WHERE phone_number = ?;
        """, (new_phone_number, old_phone_number))
        await db.commit()


async def add_car(car_number: str, user_id: int, car_brand: str, car_model: str, car_year: int, car_color: str, wrapped_car: str, repainted_car: str):
    try:
        async with aiosqlite.connect("users.db") as db:
            async with db.execute("BEGIN"):
                await db.execute("""
                    INSERT INTO cars (user_id, car_number, car_brand, car_model, car_year, car_color, wrapped_car, repainted_car)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(car_number) DO NOTHING
                """, (user_id, car_number, car_brand, car_model, car_year, car_color, wrapped_car, repainted_car))
                await db.commit()
    except Exception as e:
        print(f"Error while adding car: {e}")


async def get_car_by_number(car_number: str):# Функция для получения авто по его номеру
    async with aiosqlite.connect("users.db") as db:
        cursor = await db.execute("SELECT * FROM cars WHERE car_number = ?", (car_number,))
        row = await cursor.fetchone()

        if row is None:
            print(f"Такого авто нет в базе данных")
            return None

        # Преобразуем результат в словарь
        car = {
            "user_id": row[0],
            "car_number": row[1],
            "car_brand": row[2],
            "car_model": row[3],
            "car_year": row[4],
            "car_color": row[5],
            "wrapped_car": row[6],
            "repainted_car": row[7],
        }
        return car


async def get_client_and_cars_by_phone(phone_number: str):
    async with aiosqlite.connect("users.db") as db:
        query = """
        SELECT users.id, users.telegram_id, users.username, users.first_name, users.phone_number,
               cars.car_number, cars.car_brand, cars.car_model, cars.car_year, cars.car_color
        FROM users
        LEFT JOIN cars ON users.id = cars.user_id
        WHERE users.phone_number = ?;
        """
        cursor = await db.execute(query, (phone_number,))
        rows = await cursor.fetchall()

        if not rows:
            print(f"Такого пользователя ещё нет в базе данных")
            return None

        # Преобразуем результат в словарь
        client_info = {
            "user": {
                "id": rows[0][0],
                "telegram_id": rows[0][1],
                "username": rows[0][2],
                "first_name": rows[0][3],
                "phone_number": rows[0][4],
            },
            "cars": []
        }

        for row in rows:
            car = {
                "car_number": row[5],
                "car_brand": row[6],
                "car_model": row[7],
                "car_year": row[8],
                "car_color": row[9],
            }
            if car["car_number"] is not None:  # Проверяем, что автомобиль существует
                client_info["cars"].append(car)

        return client_info


async def get_car_and_owner_by_number(car_number: str):
    async with aiosqlite.connect("users.db") as db:
        query = """
        SELECT cars.user_id, cars.car_number, cars.car_brand, cars.car_model, cars.car_year, cars.car_color,
               users.id, users.telegram_id, users.username, users.first_name, users.phone_number
        FROM cars
        LEFT JOIN users ON cars.user_id = users.id
        WHERE cars.car_number = ?;
        """
        cursor = await db.execute(query, (car_number,))
        row = await cursor.fetchone()

        if row is None:
            print(f"Такого авто нет в базе данных")
            return None

        # Преобразуем результат в словарь
        car_info = {
            "car": {
                "user_id": row[0],
                "car_number": row[1],
                "car_brand": row[2],
                "car_model": row[3],
                "car_year": row[4],
                "car_color": row[5],
            },
            "owner": {
                "id": row[6],
                "telegram_id": row[7],
                "username": row[8],
                "first_name": row[9],
                "phone_number": row[10],
            }
        }

        return car_info


async def get_available_dates():
    async with aiosqlite.connect("users.db") as db:
        today = datetime.now()
        free_dates = []

        for i in range(30):  # Проверяем на 30 дней вперёд
            date = (today + timedelta(days=i)).strftime("%Y-%m-%d")
            # Для каждой даты считаем количество занятых постов
            cursor = await db.execute("""
                SELECT COUNT(DISTINCT post_number) FROM bookings WHERE date = ?
            """, (date,))
            count = await cursor.fetchone()

            if count[0] < 5:  # Если занято меньше 5 постов, дата считается свободной
                free_dates.append(date)

        return free_dates


async def get_client_by_id(user_id: int):
    async with aiosqlite.connect('users.db') as db:
        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()

        if row:
            # Преобразуем кортеж в словарь с помощью имен столбцов
            columns = [description[0] for description in cursor.description]
            client = dict(zip(columns, row))
            return client
    return None



async def get_cars_by_client(user_id: int):
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM cars WHERE user_id = ?", (user_id,)) as cursor:
            cars = await cursor.fetchall()
    return [dict(car) for car in cars] if cars else []


async def add_booking(booking_date, car_number, client_id, service_description):
    async with aiosqlite.connect('users.db') as db:
        # Найдём первый свободный пост для выбранной даты
        cursor = await db.execute("""
            SELECT post_number FROM bookings WHERE date = ? ORDER BY post_number
        """, (booking_date,))
        taken_posts = await cursor.fetchall()

        # Если все посты заняты, возвращаем ошибку
        if len(taken_posts) >= 5:
            return False  # Нет свободных постов

        # Находим первый свободный пост
        all_posts = {1, 2, 3, 4, 5}
        taken_posts_set = set(post[0] for post in taken_posts)
        free_posts = all_posts - taken_posts_set

        # Выбираем первый свободный пост
        post_number = min(free_posts)

        # Убираем "date:" из даты
        if booking_date.startswith("date:"):
            booking_date = booking_date[len("date:"):]

        # Вставляем запись в таблицу bookings
        await db.execute("""
            INSERT INTO bookings (car_number, date, service_description, post_number, status)
            VALUES (?, ?, ?, ?, ?)
        """, (car_number, booking_date, service_description, post_number, 'запланировано'))
        await db.commit()

        return True


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
        DATE(b.date) ASC;  -- Преобразуем строку в дату
    """
    async with aiosqlite.connect("users.db") as db:
        cursor = await db.execute(query)
        bookings = await cursor.fetchall()
        await cursor.close()
    return bookings


async def cancel_booking(booking_id: int):
    """
    Обновляет статус записи на 'отменено'.
    """
    async with aiosqlite.connect("users.db") as db:
        await db.execute("""
            UPDATE bookings
            SET status = ?
            WHERE id = ?
        """, ('отменено', booking_id))
        await db.commit()


async def get_all_active_bookings():
    """
    Возвращает список всех активных записей, кроме уже отменённых и завершённых.
    """
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
    ORDER BY DATE(b.date) ASC;
    """
    async with aiosqlite.connect("users.db") as db:
        cursor = await db.execute(query)
        bookings = await cursor.fetchall()
        await cursor.close()
    return bookings


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
    ORDER BY DATE(b.date) ASC;
    """
    async with aiosqlite.connect("users.db") as db:
        cursor = await db.execute(query)
        bookings = await cursor.fetchall()
        await cursor.close()
    return bookings

async def get_booking_by_id(booking_id):
    async with aiosqlite.connect("users.db") as db:
        cursor = await db.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
        booking = await cursor.fetchone()
        return booking

async def delete_booking(booking_id):
    async with aiosqlite.connect("users.db") as db:
        await db.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        await db.commit()


async def complete_booking(booking_id: int):
    """
    Обновляет статус записи на 'завершено'.
    """
    async with aiosqlite.connect("users.db") as db:
        await db.execute("""
            UPDATE bookings
            SET status = ?
            WHERE id = ?
        """, ('завершено', booking_id))
        await db.commit()