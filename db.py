import aiosqlite

async def initialize_database():
    # Подключаемся к базе данных (если база данных не существует, она будет создана)
    async with aiosqlite.connect("users.db") as db:
        # Создаем таблицу users, если она не существует
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,  -- Telegram ID должен быть уникальным
                username TEXT,
                first_name TEXT,
                phone_number TEXT UNIQUE      -- Если phone_number также уникальный
            );
        """)

        # Создаем таблицу cars, если она не существует
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