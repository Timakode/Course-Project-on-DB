-- User queries
CREATE OR REPLACE FUNCTION check_phone_exists(p_phone VARCHAR(12))
RETURNS TABLE (
    id INTEGER,
    username VARCHAR(100),
    phone_number VARCHAR(12)
) AS $$
    SELECT * FROM users WHERE phone_number = $1;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION check_user_exists(p_id INTEGER)
RETURNS TABLE (
    id INTEGER,
    username VARCHAR(100),
    phone_number VARCHAR(12)
) AS $$
    SELECT * FROM users WHERE id = $1;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION check_phone_used_by_other(p_phone VARCHAR(12), p_user_id INTEGER)
RETURNS TABLE (
    id INTEGER
) AS $$
    SELECT id FROM users WHERE phone_number = $1 AND id != $2;
$$ LANGUAGE SQL;

-- Нормализация строк (приведение к нижнему регистру и удаление лишних пробелов)
CREATE OR REPLACE FUNCTION normalize_string(p_str TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN LOWER(TRIM(p_str));
END;
$$ LANGUAGE plpgsql;

-- Проверка существования значения (общая функция)
CREATE OR REPLACE FUNCTION check_value_exists(
    p_table TEXT,
    p_column TEXT,
    p_value TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    v_exists BOOLEAN;
BEGIN
    EXECUTE format('
        SELECT EXISTS(
            SELECT 1 FROM %I 
            WHERE normalize_string(%I) = normalize_string($1)
        )', p_table, p_column)
    INTO v_exists
    USING p_value;
    
    RETURN v_exists;
END;
$$ LANGUAGE plpgsql;

-- Удаляем старые функции
DROP FUNCTION IF EXISTS get_service_details(integer);
DROP FUNCTION IF EXISTS check_service_exists(text);

-- Обновляем функции для работы с services
CREATE OR REPLACE FUNCTION check_service_exists(p_name TEXT)
RETURNS TABLE (
    id INTEGER,
    name TEXT,
    duration validated_duration  -- Изменяем тип на validated_duration
) AS $$
    SELECT id, name, duration 
    FROM services 
    WHERE normalize_string(name) = normalize_string($1);
$$ LANGUAGE SQL;

-- Получение данных сервиса для редактирования
CREATE OR REPLACE FUNCTION get_service_details(p_service_id INTEGER)
RETURNS TABLE (
    id INTEGER,
    name TEXT,
    duration validated_duration  -- Изменяем тип на validated_duration
) AS $$
    SELECT s.id, s.name, s.duration
    FROM services s
    WHERE s.id = $1;
$$ LANGUAGE SQL;

-- Проверка типа бокса
CREATE OR REPLACE FUNCTION check_box_exists(p_type TEXT)
RETURNS TABLE (
    id INTEGER,
    type TEXT,
    capacity INTEGER
) AS $$
    SELECT * FROM boxes 
    WHERE normalize_string(type) = normalize_string($1);
$$ LANGUAGE SQL;

-- Проверка существования типа бокса с учетом регистра
CREATE OR REPLACE FUNCTION check_box_exists_except(p_type TEXT, p_id INTEGER)
RETURNS TABLE (
    id INTEGER,
    type TEXT,
    capacity INTEGER
) AS $$
    SELECT id, type, capacity FROM boxes 
    WHERE normalize_string(type) = normalize_string($1) 
    AND id != $2;
$$ LANGUAGE SQL;

-- Получение всех боксов для комбобокса
CREATE OR REPLACE FUNCTION get_box_types()
RETURNS TABLE (
    id INTEGER,
    type TEXT,
    capacity INTEGER
) AS $$
    SELECT id, type, capacity 
    FROM boxes 
    ORDER BY type;
$$ LANGUAGE SQL;

-- Поиск бокса по названию (без учета регистра)
CREATE OR REPLACE FUNCTION find_box_by_type(p_type TEXT)
RETURNS TABLE (
    id INTEGER,
    type TEXT,
    capacity INTEGER
) AS $$
    SELECT id, type, capacity 
    FROM boxes 
    WHERE normalize_string(type) = normalize_string($1);
$$ LANGUAGE SQL;

-- Проверки для других таблиц
CREATE OR REPLACE FUNCTION check_work_status_exists(p_status TEXT)
RETURNS TABLE (id INTEGER, status TEXT) AS $$
    SELECT id, status FROM work_status 
    WHERE normalize_string(status) = normalize_string($1);
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION check_car_brand_exists(p_brand TEXT)
RETURNS TABLE (id INTEGER, brand TEXT) AS $$
    SELECT id, brand FROM car_brands 
    WHERE normalize_string(brand) = normalize_string($1);
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION check_car_color_exists(p_color TEXT)
RETURNS TABLE (id INTEGER, color TEXT) AS $$
    SELECT id, color FROM car_colors 
    WHERE normalize_string(color) = normalize_string($1);
$$ LANGUAGE SQL;

-- Проверка существования бренда по ID
CREATE OR REPLACE FUNCTION check_car_brand_by_id(p_id INTEGER)
RETURNS TABLE (
    id INTEGER,
    brand TEXT
) AS $$
    SELECT id, brand FROM car_brands WHERE id = $1;
$$ LANGUAGE SQL;

-- Проверка существования бренда с таким же названием
CREATE OR REPLACE FUNCTION check_car_brand_exists_except(p_brand TEXT, p_id INTEGER)
RETURNS TABLE (
    id INTEGER,
    brand TEXT
) AS $$
    SELECT id, brand FROM car_brands 
    WHERE normalize_string(brand) = normalize_string($1) 
    AND id != $2;
$$ LANGUAGE SQL;

-- Проверка существования модели
CREATE OR REPLACE FUNCTION check_car_model_exists(p_model TEXT, p_brand_id INTEGER)
RETURNS TABLE (
    id INTEGER,
    model TEXT,
    brand_id INTEGER
) AS $$
    SELECT id, model, brand_id 
    FROM car_models 
    WHERE normalize_string(model) = normalize_string($1) 
    AND brand_id = $2;
$$ LANGUAGE SQL;

-- Получение всех брендов для комбобокса
CREATE OR REPLACE FUNCTION get_car_brands()
RETURNS TABLE (
    id INTEGER,
    brand TEXT
) AS $$
    SELECT id, brand FROM car_brands ORDER BY brand;
$$ LANGUAGE SQL;

-- Поиск бренда по названию
CREATE OR REPLACE FUNCTION find_car_brand_by_name(p_brand TEXT)
RETURNS TABLE (
    id INTEGER,
    brand TEXT
) AS $$
    SELECT id, brand 
    FROM car_brands 
    WHERE normalize_string(brand) = normalize_string($1);
$$ LANGUAGE SQL;

-- Получение данных модели для редактирования
CREATE OR REPLACE FUNCTION get_car_model_details(p_model_id INTEGER)
RETURNS TABLE (
    id INTEGER,
    model TEXT,
    brand_id INTEGER,
    brand TEXT
) AS $$
    SELECT * FROM car_model_details WHERE id = $1;
$$ LANGUAGE SQL;

-- Проверка существования цвета с таким же названием (исключая текущий ID)
CREATE OR REPLACE FUNCTION check_car_color_exists_except(p_color TEXT, p_id INTEGER)
RETURNS TABLE (
    id INTEGER,
    color TEXT
) AS $$
    SELECT id, color FROM car_colors 
    WHERE normalize_string(color) = normalize_string($1) 
    AND id != $2;
$$ LANGUAGE SQL;

-- Получение данных цвета по ID
CREATE OR REPLACE FUNCTION get_car_color_details(p_color_id INTEGER)
RETURNS TABLE (
    id INTEGER,
    color TEXT
) AS $$
    SELECT id, color FROM car_colors WHERE id = $1;
$$ LANGUAGE SQL;

-- Проверка существования статуса оклейки
CREATE OR REPLACE FUNCTION check_car_wrap_exists_except(p_status TEXT, p_id INTEGER)
RETURNS TABLE (
    id INTEGER,
    status TEXT
) AS $$
    SELECT id, status FROM car_wraps 
    WHERE normalize_string(status) = normalize_string($1) 
    AND id != $2;
$$ LANGUAGE SQL;

-- Проверка существования статуса перекраса
CREATE OR REPLACE FUNCTION check_car_repaint_exists_except(p_status TEXT, p_id INTEGER)
RETURNS TABLE (
    id INTEGER,
    status TEXT
) AS $$
    SELECT id, status FROM car_repaints 
    WHERE normalize_string(status) = normalize_string($1) 
    AND id != $2;
$$ LANGUAGE SQL;

-- Функция проверки существования статуса с учетом регистра
CREATE OR REPLACE FUNCTION check_status_exists_except(
    p_status TEXT,
    p_id INTEGER
) RETURNS TABLE (
    id INTEGER,
    status TEXT
) AS $$
    SELECT id, status 
    FROM work_status 
    WHERE normalize_string(status) = normalize_string($1) 
    AND id != $2;
$$ LANGUAGE SQL;

-- Функция поиска пользователя по username и phone
CREATE OR REPLACE FUNCTION find_user_by_credentials(
    p_username TEXT,
    p_phone TEXT
) RETURNS TABLE (
    id INTEGER,
    username TEXT,
    phone_number TEXT
) AS $$
    SELECT id, username, phone_number
    FROM users 
    WHERE username = $1 AND phone_number = $2;
$$ LANGUAGE SQL;

-- Функция получения деталей сервиса
CREATE OR REPLACE FUNCTION get_services_list()
RETURNS TABLE (
    id INTEGER,
    name TEXT,
    duration_value INTEGER,
    duration_unit duration_unit
) AS $$
    SELECT 
        id, 
        name,
        (duration).value,  -- Используем правильный синтаксис для доступа к полям
        (duration).unit    -- составного типа
    FROM services
    ORDER BY id;
$$ LANGUAGE SQL;

-- Переписываем функцию проверки номера машины полностью
CREATE OR REPLACE FUNCTION check_plate_number_exists(p_plate TEXT) 
RETURNS BOOLEAN AS $$
DECLARE
    v_exists BOOLEAN;
    v_normalized_plate TEXT;
BEGIN
    -- Нормализуем входной номер
    v_normalized_plate := LOWER(TRIM(p_plate));
    
    -- Добавляем отладочную информацию
    RAISE NOTICE 'Checking plate: %, normalized: %', p_plate, v_normalized_plate;
    
    -- Проверяем существование
    SELECT EXISTS (
        SELECT 1 
        FROM cars 
        WHERE LOWER(TRIM(plate_number)) = v_normalized_plate
    ) INTO v_exists;
    
    -- Добавляем отладочную информацию
    RAISE NOTICE 'Result: %', v_exists;
    
    RETURN v_exists;
END;
$$ LANGUAGE plpgsql;

-- Получение пользователей по номеру телефона
CREATE OR REPLACE FUNCTION get_users_by_phone(p_phone TEXT)
RETURNS TABLE (
    id INTEGER,
    username TEXT,
    phone_number TEXT
) AS $$
    SELECT id, username, phone_number 
    FROM users 
    WHERE phone_number LIKE '%' || p_phone || '%'
    ORDER BY username;
$$ LANGUAGE SQL;

-- Получение моделей с брендами
CREATE OR REPLACE FUNCTION get_models_with_brands()
RETURNS TABLE (
    model_id INTEGER,
    model_name TEXT,
    brand_name TEXT
) AS $$
    SELECT m.id, m.model, b.brand
    FROM car_models m
    JOIN car_brands b ON m.brand_id = b.id
    ORDER BY b.brand, m.model;
$$ LANGUAGE SQL;

-- Исправляем функцию получения или создания цвета
CREATE OR REPLACE FUNCTION get_or_create_color(p_color TEXT)
RETURNS INTEGER AS $$
DECLARE
    v_color_id INTEGER;
    v_normalized_color TEXT;
BEGIN
    -- Нормализуем название цвета
    v_normalized_color := normalize_string(p_color);
    
    -- Добавляем отладочную информацию
    RAISE NOTICE 'Getting or creating color: %, normalized: %', p_color, v_normalized_color;
    
    -- Пытаемся найти существующий цвет
    SELECT id INTO v_color_id 
    FROM car_colors 
    WHERE normalize_string(color) = v_normalized_color;
    
    -- Если цвет не найден, создаем новый
    IF NOT FOUND THEN
        INSERT INTO car_colors (color) 
        VALUES (p_color)
        RETURNING id INTO v_color_id;
        
        RAISE NOTICE 'Created new color with ID: %', v_color_id;
    ELSE
        RAISE NOTICE 'Found existing color with ID: %', v_color_id;
    END IF;
    
    RETURN v_color_id;
EXCEPTION
    WHEN unique_violation THEN
        -- В случае конкурентной вставки пробуем найти снова
        SELECT id INTO v_color_id 
        FROM car_colors 
        WHERE normalize_string(color) = v_normalized_color;
        
        RAISE NOTICE 'Resolved concurrent insert, using ID: %', v_color_id;
        RETURN v_color_id;
END;
$$ LANGUAGE plpgsql;

-- Получение доступных элементов перекраса
CREATE OR REPLACE FUNCTION get_available_repaints(p_car_id TEXT)
RETURNS TABLE (
    id INTEGER,
    status TEXT
) AS $$
    SELECT id, status FROM car_repaints
    WHERE id NOT IN (
        SELECT repaint_id FROM car_repaint_links 
        WHERE car_id = p_car_id
    )
    ORDER BY status;
$$ LANGUAGE SQL;

-- Получение доступных элементов оклейки
CREATE OR REPLACE FUNCTION get_available_wraps(p_car_id TEXT)
RETURNS TABLE (
    id INTEGER,
    status TEXT
) AS $$
    SELECT id, status FROM car_wraps
    ORDER BY status;
$$ LANGUAGE SQL;

-- Получение списка всех пользователей
CREATE OR REPLACE FUNCTION get_all_users()
RETURNS TABLE (
    id INTEGER,
    username TEXT,
    phone_number TEXT
) AS $$
    SELECT id, username, phone_number 
    FROM users 
    ORDER BY username;
$$ LANGUAGE SQL;

-- Получение всех доступных элементов перекраса
CREATE OR REPLACE FUNCTION get_all_repaints()
RETURNS TABLE (
    id INTEGER,
    status TEXT
) AS $$
    SELECT id, status FROM car_repaints ORDER BY status;
$$ LANGUAGE SQL;

-- Получение всех доступных элементов оклейки
CREATE OR REPLACE FUNCTION get_all_wraps()
RETURNS TABLE (
    id INTEGER,
    status TEXT
) AS $$
    SELECT id, status FROM car_wraps ORDER BY status;
$$ LANGUAGE SQL;
