-- 1. Процедура для добавления нового автомобиля с проверками
CREATE OR REPLACE PROCEDURE добавить_автомобиль(
    p_номер_авто TEXT,
    p_id_пользователя INTEGER,
    p_бренд TEXT,
    p_модель TEXT,
    p_год_выпуска INTEGER,
    p_цвет TEXT,
    p_статус_оклейки TEXT,
    p_статус_перекраса TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_бренда INTEGER;
    v_id_модели INTEGER;
    v_id_цвета INTEGER;
    v_id_оклейки INTEGER;
    v_id_перекраса INTEGER;
BEGIN
    -- Проверка существования пользователя
    IF NOT EXISTS (SELECT 1 FROM пользователи WHERE id = p_id_пользователя) THEN
        RAISE EXCEPTION 'Пользователь с ID % не найден', p_id_пользователя;
    END IF;

    -- Получение или создание ID бренда
    SELECT id INTO v_id_бренда FROM бренд_авто WHERE бренд = p_бренд;
    IF NOT FOUND THEN
        INSERT INTO бренд_авто (бренд) VALUES (p_бренд) RETURNING id INTO v_id_бренда;
    END IF;

    -- Получение или создание ID модели
    SELECT id INTO v_id_модели FROM модель_авто WHERE модель = p_модель AND id_бренда = v_id_бренда;
    IF NOT FOUND THEN
        INSERT INTO модель_авто (модель, id_бренда) VALUES (p_модель, v_id_бренда) RETURNING id INTO v_id_модели;
    END IF;

    -- Получение или создание ID цвета
    SELECT id INTO v_id_цвета FROM цвет_авто WHERE цвет = p_цвет;
    IF NOT FOUND THEN
        INSERT INTO цвет_авто (цвет) VALUES (p_цвет) RETURNING id INTO v_id_цвета;
    END IF;

    -- Получение ID оклейки
    SELECT id INTO v_id_оклейки FROM оклейка_авто WHERE статус_оклейки = p_статус_оклейки;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Неверный статус оклейки: %', p_статус_оклейки;
    END IF;

    -- Получение ID перекраса
    SELECT id INTO v_id_перекраса FROM перекрас_авто WHERE статус_перекраса = p_статус_перекраса;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Неверный статус перекраса: %', p_статус_перекраса;
    END IF;

    -- Добавление автомобиля
    INSERT INTO автомобили (
        номер_авто, id_пользователя, id_модели, год_выпуска,
        id_цвета, id_оклейки, id_перекраса
    ) VALUES (
        p_номер_авто, p_id_пользователя, v_id_модели, p_год_выпуска,
        v_id_цвета, v_id_оклейки, v_id_перекраса
    );
END;
$$;

-- Drop existing procedure
DROP PROCEDURE IF EXISTS add_user CASCADE;

CREATE OR REPLACE PROCEDURE add_user(
    p_username VARCHAR(100),
    p_phone_number VARCHAR(12)
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Базовая проверка на пустые значения
    IF p_username IS NULL OR LENGTH(TRIM(p_username)) = 0 THEN
        RAISE EXCEPTION 'Username cannot be empty';
    END IF;

    IF p_phone_number IS NULL OR LENGTH(TRIM(p_phone_number)) = 0 THEN
        RAISE EXCEPTION 'Phone number cannot be empty';
    END IF;

    -- Вставка данных (формат телефона будет проверен триггером)
    INSERT INTO users (username, phone_number)
    VALUES (TRIM(p_username), TRIM(p_phone_number));
    
    RAISE NOTICE 'User added successfully';
END;
$$;

-- Test procedure functionality
DO $$ 
BEGIN
    CALL add_user('Test User', '+79999999999');
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Test failed: %', SQLERRM;
END $$;

-- Пересоздаем процедуру update_user
DROP PROCEDURE IF EXISTS update_user CASCADE;

CREATE OR REPLACE PROCEDURE update_user(
    p_id INTEGER,
    p_username VARCHAR(100),
    p_phone_number VARCHAR(12)
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Input validation
    IF p_username IS NULL OR LENGTH(TRIM(p_username)) = 0 THEN
        RAISE EXCEPTION 'Username cannot be empty';
    END IF;

    IF p_phone_number IS NULL OR LENGTH(TRIM(p_phone_number)) = 0 THEN
        RAISE EXCEPTION 'Phone number cannot be empty';
    END IF;

    IF NOT p_phone_number ~ '^\+7[0-9]{10}$' THEN
        RAISE EXCEPTION 'Invalid phone number format. Expected: +7XXXXXXXXXX, got: %', p_phone_number;
    END IF;

    -- Check if user exists
    IF NOT EXISTS (SELECT 1 FROM users WHERE id = p_id) THEN
        RAISE EXCEPTION 'User with ID % not found', p_id;
    END IF;

    -- Check if phone number is already in use by another user
    IF EXISTS (
        SELECT 1 FROM users 
        WHERE phone_number = TRIM(p_phone_number) 
        AND id != p_id
    ) THEN
        RAISE EXCEPTION 'Phone number already exists';
    END IF;

    -- Update user
    UPDATE users 
    SET username = TRIM(p_username),
        phone_number = TRIM(p_phone_number)
    WHERE id = p_id;
END;
$$;

-- Test the procedure
DO $$
BEGIN
    -- Тестовое обновление (подставьте реальный ID)
    CALL update_user(1, 'Test Name', '+71234567890');
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Test update failed: %', SQLERRM;
END $$;

-- 2. Функция для получения популярных брендов
CREATE OR REPLACE FUNCTION получить_популярные_бренды(
    количество INTEGER DEFAULT 3
)
RETURNS TABLE (
    бренд TEXT,
    количество_автомобилей BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        б.бренд,
        COUNT(DISTINCT а.номер_авто) as количество_автомобилей
    FROM бренд_авто б
    JOIN модель_авто м ON м.id_бренда = б.id
    JOIN автомобили а ON а.id_модели = м.id
    GROUP BY б.id, б.бренд
    ORDER BY количество_автомобилей DESC
    LIMIT количество;
END;
$$;

-- 3. Функция для получения непопулярных боксов
CREATE OR REPLACE FUNCTION получить_непопулярные_боксы(
    p_дата_начала DATE DEFAULT NULL,
    p_дата_конца DATE DEFAULT NULL
)
RETURNS TABLE (
    тип_бокса TEXT,
    количество_записей BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        б.тип_бокса,
        COUNT(з.id) as количество_записей
    FROM боксы б
    LEFT JOIN записи з ON з.id_бокса = б.id
    WHERE (p_дата_начала IS NULL OR з.дата_записи >= p_дата_начала)
    AND (p_дата_конца IS NULL OR з.дата_записи <= p_дата_конца)
    GROUP BY б.id, б.тип_бокса
    ORDER BY количество_записей ASC;
END;
$$;

-- 4. Функция для получения популярных услуг
CREATE OR REPLACE FUNCTION получить_популярные_услуги()
RETURNS TABLE (
    название_услуги TEXT,
    количество_заказов BIGINT,
    процент_от_общего NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    total_orders BIGINT;
BEGIN
    SELECT COUNT(*) INTO total_orders FROM услуги_записей;
    
    RETURN QUERY
    SELECT 
        у.название_услуги,
        COUNT(уз.id_услуги) as количество_заказов,
        ROUND(COUNT(уз.id_услуги)::NUMERIC * 100 / NULLIF(total_orders, 0), 2) as процент_от_общего
    FROM услуги у
    LEFT JOIN услуги_записей уз ON уз.id_услуги = у.id
    GROUP BY у.id, у.название_услуги
    ORDER BY количество_заказов DESC;
END;
$$;

-- 5. Процедура для создания новой записи
CREATE OR REPLACE PROCEDURE создать_запись(
    p_id_пользователя INTEGER,
    p_номер_авто TEXT,
    p_дата_записи DATE,
    p_услуги INTEGER[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_записи INTEGER;
    v_id_бокса INTEGER;
    v_услуга INTEGER;
BEGIN
    -- Проверка существования автомобиля и пользователя
    IF NOT EXISTS (
        SELECT 1 
        FROM автомобили 
        WHERE номер_авто = p_номер_авто 
        AND id_пользователя = p_id_пользователя
    ) THEN
        RAISE EXCEPTION 'Автомобиль % не принадлежит пользователю с ID %', 
                      p_номер_авто, p_id_пользователя;
    END IF;

    -- Находим наименее загруженный бокс
    SELECT id INTO v_id_бокса
    FROM боксы б
    LEFT JOIN (
        SELECT id_бокса, COUNT(*) as занято
        FROM записи
        WHERE дата_записи = p_дата_записи
        GROUP BY id_бокса
    ) з ON б.id = з.id_бокса
    ORDER BY з.занято NULLS FIRST
    LIMIT 1;

    -- Создаем запись
    INSERT INTO записи (
        id_бокса,
        id_пользователя,
        номер_авто,
        дата_записи,
        id_статуса_работы
    )
    VALUES (
        v_id_бокса,
        p_id_пользователя,
        p_номер_авто,
        p_дата_записи,
        (SELECT id FROM статус_работы WHERE статус_работы = 'Ожидает выполнения')
    )
    RETURNING id INTO v_id_записи;

    -- Добавляем услуги
    FOREACH v_услуга IN ARRAY p_услуги
    LOOP
        INSERT INTO услуги_записей (id_записи, id_услуги)
        VALUES (v_id_записи, v_услуга);
    END LOOP;
END;
$$;

-- Процедуры для добавления данных
CREATE OR REPLACE PROCEDURE add_status_work(p_status TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO статус_работы (статус_работы) VALUES (p_status);
END;
$$;

CREATE OR REPLACE PROCEDURE add_car_brand(p_brand TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO бренд_авто (бренд) VALUES (p_brand);
END;
$$;

CREATE OR REPLACE PROCEDURE add_car_model(p_model TEXT, p_brand_id INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO модель_авто (модель, id_бренда) VALUES (p_model, p_brand_id);
END;
$$;

CREATE OR REPLACE PROCEDURE add_car_color(p_color TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_color IS NULL OR LENGTH(TRIM(p_color)) = 0 THEN
        RAISE EXCEPTION 'Color name cannot be empty';
    END IF;

    -- Добавляем цвет (нормализация будет выполнена триггером)
    INSERT INTO car_colors (color) VALUES (p_color);
END;
$$;

CREATE OR REPLACE PROCEDURE add_wrap_status(p_status TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO оклейка_авто (статус_оклейки) VALUES (p_status);
END;
$$;

CREATE OR REPLACE PROCEDURE add_paint_status(p_status TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO перекрас_авто (статус_перекраса) VALUES (p_status);
END;
$$;

CREATE OR REPLACE PROCEDURE add_box(p_type TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO боксы (тип_бокса) VALUES (p_type);
END;
$$;

CREATE OR REPLACE PROCEDURE add_service(p_name TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO услуги (название_услуги) VALUES (p_name);
END;
$$;

CREATE OR REPLACE PROCEDURE add_service_appointment(p_appointment_id INTEGER, p_service_id INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO услуги_записей (id_записи, id_услуги) VALUES (p_appointment_id, p_service_id);
END;
$$;

-- Процедуры для справочников с нормализацией строк
CREATE OR REPLACE PROCEDURE add_work_status(p_status TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO work_status (status) 
    VALUES (normalize_string(p_status));
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Status "%" already exists', p_status;
END;
$$;

CREATE OR REPLACE PROCEDURE add_car_brand(p_brand TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO car_brands (brand) 
    VALUES (normalize_string(p_brand));
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Brand "%" already exists', p_brand;
END;
$$;

CREATE OR REPLACE PROCEDURE add_car_wrap(p_status TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO car_wraps (status) 
    VALUES (normalize_string(p_status));
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Wrap status "%" already exists', p_status;
END;
$$;

CREATE OR REPLACE PROCEDURE add_car_repaint(p_status TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO car_repaints (status) 
    VALUES (normalize_string(p_status));
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Repaint status "%" already exists', p_status;
END;
$$;

CREATE OR REPLACE PROCEDURE add_box(p_type TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO boxes (type) 
    VALUES (normalize_string(p_type));
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Box type "%" already exists', p_type;
END;
$$;

CREATE OR REPLACE PROCEDURE add_service(p_name TEXT, p_duration INTEGER, p_box_id INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO services (name, duration, box_id)
    VALUES (normalize_string(p_name), p_duration, p_box_id);
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Service "%" already exists', p_name;
END;
$$;

CREATE OR REPLACE PROCEDURE update_work_status(
    p_id INTEGER,
    p_status TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Input validation
    IF p_status IS NULL OR LENGTH(TRIM(p_status)) = 0 THEN
        RAISE EXCEPTION 'Status cannot be empty';
    END IF;

    -- Check if status exists
    IF NOT EXISTS (SELECT 1 FROM work_status WHERE id = p_id) THEN
        RAISE EXCEPTION 'Status with ID % not found', p_id;
    END IF;

    -- Update (триггер check_case_insensitive_unique проверит уникальность)
    UPDATE work_status 
    SET status = TRIM(p_status)
    WHERE id = p_id;
END;
$$;

CREATE OR REPLACE PROCEDURE update_car_brand(
    p_id INTEGER,
    p_brand TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Input validation
    IF p_brand IS NULL OR LENGTH(TRIM(p_brand)) = 0 THEN
        RAISE EXCEPTION 'Brand name cannot be empty';
    END IF;

    -- Check if brand exists
    IF NOT EXISTS (SELECT 1 FROM car_brands WHERE id = p_id) THEN
        RAISE EXCEPTION 'Brand with ID % not found', p_id;
    END IF;

    -- Update (триггер автоматически нормализует значение)
    UPDATE car_brands 
    SET brand = TRIM(p_brand)
    WHERE id = p_id;
END;
$$;

-- Процедура добавления модели
CREATE OR REPLACE PROCEDURE add_car_model(
    p_model TEXT,
    p_brand TEXT
)
LANGUAGE plpgsql AS $$
DECLARE
    v_brand_id INTEGER;
BEGIN
    -- Проверяем/добавляем бренд
    SELECT id INTO v_brand_id
    FROM find_car_brand_by_name(p_brand);
    
    IF NOT FOUND THEN
        -- Добавляем новый бренд
        INSERT INTO car_brands (brand)
        VALUES (normalize_string(p_brand))
        RETURNING id INTO v_brand_id;
    END IF;

    -- Проверяем существование модели
    IF EXISTS (
        SELECT 1 FROM car_models 
        WHERE normalize_string(model) = normalize_string(p_model)
        AND brand_id = v_brand_id
    ) THEN
        RAISE EXCEPTION 'Model "%" already exists for this brand', p_model;
    END IF;

    -- Добавляем модель
    INSERT INTO car_models (model, brand_id)
    VALUES (normalize_string(p_model), v_brand_id);
END;
$$;

-- Процедура обновления модели
CREATE OR REPLACE PROCEDURE update_car_model(
    p_model_id INTEGER,
    p_new_model TEXT,
    p_new_brand TEXT
)
LANGUAGE plpgsql AS $$
DECLARE
    v_brand_id INTEGER;
BEGIN
    -- Проверяем существование модели
    IF NOT EXISTS (SELECT 1 FROM car_models WHERE id = p_model_id) THEN
        RAISE EXCEPTION 'Model with ID % not found', p_model_id;
    END IF;

    -- Проверяем/добавляем бренд
    SELECT id INTO v_brand_id
    FROM find_car_brand_by_name(p_new_brand);
    
    IF NOT FOUND THEN
        -- Добавляем новый бренд
        INSERT INTO car_brands (brand)
        VALUES (normalize_string(p_new_brand))
        RETURNING id INTO v_brand_id;
    END IF;

    -- Проверяем уникальность новой модели
    IF EXISTS (
        SELECT 1 FROM car_models 
        WHERE normalize_string(model) = normalize_string(p_new_model)
        AND brand_id = v_brand_id
        AND id != p_model_id
    ) THEN
        RAISE EXCEPTION 'Model "%" already exists for brand "%"', p_new_model, p_new_brand;
    END IF;

    -- Обновляем модель
    UPDATE car_models 
    SET model = normalize_string(p_new_model),
        brand_id = v_brand_id
    WHERE id = p_model_id;
END;
$$;

-- Процедура добавления цвета
CREATE OR REPLACE PROCEDURE add_car_color(
    p_color TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Input validation
    IF p_color IS NULL OR LENGTH(TRIM(p_color)) = 0 THEN
        RAISE EXCEPTION 'Color name cannot be empty';
    END IF;

    -- Проверяем существование
    IF EXISTS (
        SELECT 1 FROM car_colors 
        WHERE normalize_string(color) = normalize_string(p_color)
    ) THEN
        RAISE EXCEPTION 'Color "%" already exists', p_color;
    END IF;

    -- Добавляем цвет
    INSERT INTO car_colors (color)
    VALUES (normalize_string(p_color));
END;
$$;

-- Удаляем старые процедуры
DROP PROCEDURE IF EXISTS add_car_color(text);
DROP PROCEDURE IF EXISTS update_car_color(integer,text);

-- Простая процедура добавления цвета
CREATE OR REPLACE PROCEDURE add_car_color(p_color TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO car_colors (color) VALUES (p_color);
END;
$$;

-- Простая процедура обновления цвета
CREATE OR REPLACE PROCEDURE update_car_color(p_id INTEGER, p_color TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE car_colors SET color = p_color WHERE id = p_id;
END;
$$;

-- Удаляем старые процедуры
DROP PROCEDURE IF EXISTS add_car_wrap(text);
DROP PROCEDURE IF EXISTS update_car_wrap(integer,text);
DROP PROCEDURE IF EXISTS add_car_repaint(text);
DROP PROCEDURE IF EXISTS update_car_repaint(integer,text);

-- Простая процедура добавления статуса оклейки
CREATE OR REPLACE PROCEDURE add_car_wrap(p_status TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO car_wraps (status) VALUES (p_status);
END;
$$;

-- Простая процедура обновления статуса оклейки
CREATE OR REPLACE PROCEDURE update_car_wrap(p_id INTEGER, p_status TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE car_wraps SET status = p_status WHERE id = p_id;
END;
$$;

-- Простая процедура добавления статуса перекраса
CREATE OR REPLACE PROCEDURE add_car_repaint(p_status TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO car_repaints (status) VALUES (p_status);
END;
$$;

-- Простая процедура обновления статуса перекраса
CREATE OR REPLACE PROCEDURE update_car_repaint(p_id INTEGER, p_status TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE car_repaints SET status = p_status WHERE id = p_id;
END;
$$;

-- Удаляем старые процедуры
DROP PROCEDURE IF EXISTS add_box(text);
DROP PROCEDURE IF EXISTS update_box(integer,text);

-- Процедура добавления бокса
CREATE OR REPLACE PROCEDURE add_box(p_type TEXT, p_capacity INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    -- Проверка входных данных
    IF p_type IS NULL OR LENGTH(TRIM(p_type)) = 0 THEN
        RAISE EXCEPTION 'Box type cannot be empty';
    END IF;

    IF p_capacity IS NULL OR p_capacity < 1 THEN
        RAISE EXCEPTION 'Box capacity must be greater than 0';
    END IF;

    -- Добавляем бокс (нормализация будет выполнена триггером)
    INSERT INTO boxes (type, capacity) VALUES (p_type, p_capacity);
END;
$$;

-- Процедура обновления бокса
CREATE OR REPLACE PROCEDURE update_box(
    p_id INTEGER,
    p_type TEXT,
    p_capacity INTEGER
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Проверка входных данных
    IF p_type IS NULL OR LENGTH(TRIM(p_type)) = 0 THEN
        RAISE EXCEPTION 'Box type cannot be empty';
    END IF;

    IF p_capacity IS NULL OR p_capacity < 1 THEN
        RAISE EXCEPTION 'Box capacity must be greater than 0';
    END IF;

    -- Проверка существования
    IF NOT EXISTS (SELECT 1 FROM boxes WHERE id = p_id) THEN
        RAISE EXCEPTION 'Box with ID % not found', p_id;
    END IF;

    -- Обновляем данные (нормализация будет выполнена триггером)
    UPDATE boxes 
    SET type = p_type,
        capacity = p_capacity
    WHERE id = p_id;
END;
$$;

-- Процедура добавления сервиса
CREATE OR REPLACE PROCEDURE add_service_with_box(
    p_name TEXT,
    p_duration INTEGER,
    p_box_type TEXT,
    p_box_capacity INTEGER DEFAULT NULL
)
LANGUAGE plpgsql AS $$
DECLARE
    v_box_id INTEGER;
BEGIN
    -- Проверка входных данных
    IF p_name IS NULL OR LENGTH(TRIM(p_name)) = 0 THEN
        RAISE EXCEPTION 'Service name cannot be empty';
    END IF;

    IF p_duration < 15 THEN
        RAISE EXCEPTION 'Duration must be at least 15 minutes';
    END IF;

    -- Ищем существующий бокс
    SELECT id INTO v_box_id
    FROM boxes 
    WHERE normalize_string(type) = normalize_string(p_box_type);

    -- Если бокс не найден и указана вместимость, создаем новый
    IF NOT FOUND AND p_box_capacity IS NOT NULL THEN
        INSERT INTO boxes (type, capacity)
        VALUES (p_box_type, p_box_capacity)
        RETURNING id INTO v_box_id;
    ELSIF NOT FOUND THEN
        RAISE EXCEPTION 'Box type "%" not found', p_box_type;
    END IF;

    -- Добавляем сервис
    INSERT INTO services (name, duration, box_id)
    VALUES (p_name, p_duration, v_box_id);
END;
$$;