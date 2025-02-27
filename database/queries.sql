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

-- Проверка названия услуги
CREATE OR REPLACE FUNCTION check_service_exists(p_name TEXT)
RETURNS TABLE (
    id INTEGER,
    name TEXT,
    duration INTEGER,
    box_id INTEGER
) AS $$
    SELECT * FROM services 
    WHERE normalize_string(name) = normalize_string($1);
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
