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


-- Процедуры для добавления данных
CREATE OR REPLACE PROCEDURE add_status_work(p_status TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO статус_работы (статус_работы) VALUES (p_status);
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

CREATE OR REPLACE PROCEDURE add_service(
    p_name TEXT,
    p_duration_value INTEGER,
    p_duration_unit duration_unit
)
LANGUAGE plpgsql AS $$
DECLARE
    v_duration validated_duration;
BEGIN
    -- Создаем значение типа validated_duration
    v_duration := ROW(p_duration_value, p_duration_unit)::validated_duration;
    
    -- Добавляем сервис
    INSERT INTO services (name, duration)
    VALUES (normalize_string(p_name), v_duration);
    
EXCEPTION
    WHEN check_violation THEN
        RAISE EXCEPTION 'Invalid duration: value must be between 15-480 for minutes or 1-30 for days';
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Service with name "%" already exists', p_name;
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

-- Простая процедура обновления цвета
CREATE OR REPLACE PROCEDURE update_car_color(p_id INTEGER, p_color TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE car_colors SET color = p_color WHERE id = p_id;
END;
$$;


-- Простая процедура обновления статуса оклейки
CREATE OR REPLACE PROCEDURE update_car_wrap(p_id INTEGER, p_status TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE car_wraps SET status = p_status WHERE id = p_id;
END;
$$;


-- Простая процедура обновления статуса перекраса
CREATE OR REPLACE PROCEDURE update_car_repaint(p_id INTEGER, p_status TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE car_repaints SET status = p_status WHERE id = p_id;
END;
$$;


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

-- Процедура обновления сервиса
CREATE OR REPLACE PROCEDURE update_service(
    p_service_id INTEGER,
    p_name TEXT,
    p_duration_value INTEGER,
    p_duration_unit duration_unit
)
LANGUAGE plpgsql AS $$
DECLARE
    v_duration validated_duration;
BEGIN
    -- Проверяем существование сервиса
    IF NOT EXISTS (SELECT 1 FROM services WHERE id = p_service_id) THEN
        RAISE EXCEPTION 'Service with ID % not found', p_service_id;
    END IF;

    -- Создаем значение типа validated_duration
    v_duration := ROW(p_duration_value, p_duration_unit)::validated_duration;
    
    -- Обновляем сервис
    UPDATE services 
    SET name = normalize_string(p_name),
        duration = v_duration
    WHERE id = p_service_id;

EXCEPTION
    WHEN check_violation THEN
        RAISE EXCEPTION 'Invalid duration: value must be between 15-480 for minutes or 1-30 for days';
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Service with name "%" already exists', p_name;
END;
$$;

