-- Drop all existing triggers first
DROP TRIGGER IF EXISTS before_insert_phone_number ON users;
DROP TRIGGER IF EXISTS after_insert_log ON bookings;
DROP TRIGGER IF EXISTS before_update_booking_date ON bookings;
DROP TRIGGER IF EXISTS after_update_status ON bookings;
DROP TRIGGER IF EXISTS before_delete_booking ON bookings;
DROP TRIGGER IF EXISTS check_work_status_unique ON work_status;
DROP TRIGGER IF EXISTS work_status_case_check ON work_status;
DROP TRIGGER IF EXISTS car_brands_case_check ON car_brands;
DROP TRIGGER IF EXISTS car_colors_case_check ON car_colors;
DROP TRIGGER IF EXISTS boxes_case_check ON boxes;
DROP TRIGGER IF EXISTS services_case_check ON services;

-- Удаляем старые триггеры
DROP TRIGGER IF EXISTS normalize_car_colors ON car_colors;
DROP TRIGGER IF EXISTS car_colors_case_check ON car_colors;

-- Create audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    record_id TEXT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1. Phone number format check trigger
CREATE OR REPLACE FUNCTION check_phone_number()
RETURNS TRIGGER AS $$
BEGIN
    -- Проверка формата номера телефона
    IF NOT NEW.phone_number ~ '^\+7[0-9]{10}$' THEN
        RAISE EXCEPTION 'Invalid phone number format. Expected: +7XXXXXXXXXX, got: %', NEW.phone_number;
    END IF;

    -- Проверка уникальности номера
    IF EXISTS (
        SELECT 1 FROM users 
        WHERE phone_number = NEW.phone_number 
        AND id != COALESCE(NEW.id, -1)
    ) THEN
        RAISE EXCEPTION 'Phone number already exists';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_insert_phone_number
    BEFORE INSERT OR UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION check_phone_number();

-- 2. Audit log trigger
CREATE OR REPLACE FUNCTION log_new_record()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, operation, record_id)
    VALUES (TG_TABLE_NAME, TG_OP, NEW.id::TEXT);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_insert_log
    AFTER INSERT ON bookings
    FOR EACH ROW
    EXECUTE FUNCTION log_new_record();

-- 3. Booking date check trigger
CREATE OR REPLACE FUNCTION check_booking_date()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.date < CURRENT_DATE THEN
        RAISE EXCEPTION 'Cannot set booking date in the past';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_update_booking_date
    BEFORE UPDATE ON bookings
    FOR EACH ROW
    EXECUTE FUNCTION check_booking_date();

-- 4. Status changes tracking
CREATE TABLE IF NOT EXISTS status_changes (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL,
    old_status INTEGER,
    new_status INTEGER,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION track_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status_id != NEW.status_id THEN
        INSERT INTO status_changes (booking_id, old_status, new_status)
        VALUES (NEW.id, OLD.status_id, NEW.status_id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_update_status
    AFTER UPDATE ON bookings
    FOR EACH ROW
    EXECUTE FUNCTION track_status_change();

-- 5. Prevent deletion of active bookings
CREATE OR REPLACE FUNCTION prevent_delete_active_booking()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status_id IN (
        SELECT id FROM work_status WHERE status IN ('In Progress', 'Pending')
    ) THEN
        RAISE EXCEPTION 'Cannot delete active booking';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_delete_booking
    BEFORE DELETE ON bookings
    FOR EACH ROW
    EXECUTE FUNCTION prevent_delete_active_booking();

-- Case-insensitive check function for all tables
CREATE OR REPLACE FUNCTION check_case_insensitive_unique()
RETURNS TRIGGER AS $$
BEGIN
    -- Проверка для work_status
    IF TG_TABLE_NAME = 'work_status' THEN
        IF EXISTS (
            SELECT 1 FROM work_status 
            WHERE normalize_string(status) = normalize_string(NEW.status)
            AND id != COALESCE(NEW.id, -1)
        ) THEN
            RAISE EXCEPTION 'Status "%" already exists (case-insensitive)', NEW.status;
        END IF;
        RETURN NEW;
    END IF;

    -- Проверка для car_brands
    IF TG_TABLE_NAME = 'car_brands' THEN
        IF EXISTS (
            SELECT 1 FROM car_brands 
            WHERE normalize_string(brand) = normalize_string(NEW.brand)
            AND id != COALESCE(NEW.id, -1)
        ) THEN
            RAISE EXCEPTION 'Brand "%" already exists (case-insensitive)', NEW.brand;
        END IF;
        RETURN NEW;
    END IF;

    -- Проверка для car_colors
    IF TG_TABLE_NAME = 'car_colors' AND EXISTS (
        SELECT 1 FROM car_colors 
        WHERE normalize_string(color) = normalize_string(NEW.color)
        AND id != COALESCE(NEW.id, -1)
    ) THEN
        RAISE EXCEPTION 'Color "%" already exists (case-insensitive)', NEW.color;
    END IF;

    -- Проверка для boxes
    IF TG_TABLE_NAME = 'boxes' AND EXISTS (
        SELECT 1 FROM boxes 
        WHERE normalize_string(type) = normalize_string(NEW.type)
        AND id != COALESCE(NEW.id, -1)
    ) THEN
        RAISE EXCEPTION 'Box type "%" already exists (case-insensitive)', NEW.type;
    END IF;

    -- Проверка для services
    IF TG_TABLE_NAME = 'services' AND EXISTS (
        SELECT 1 FROM services 
        WHERE normalize_string(name) = normalize_string(NEW.name)
        AND id != COALESCE(NEW.id, -1)
    ) THEN
        RAISE EXCEPTION 'Service "%" already exists (case-insensitive)', NEW.name;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create all case-insensitive check triggers
CREATE TRIGGER work_status_case_check
    BEFORE INSERT OR UPDATE ON work_status
    FOR EACH ROW EXECUTE FUNCTION check_case_insensitive_unique();

CREATE TRIGGER car_brands_case_check
    BEFORE INSERT OR UPDATE ON car_brands
    FOR EACH ROW EXECUTE FUNCTION check_case_insensitive_unique();

CREATE TRIGGER car_colors_case_check
    BEFORE INSERT OR UPDATE ON car_colors
    FOR EACH ROW EXECUTE FUNCTION check_case_insensitive_unique();

CREATE TRIGGER boxes_case_check
    BEFORE INSERT OR UPDATE ON boxes
    FOR EACH ROW EXECUTE FUNCTION check_case_insensitive_unique();

CREATE TRIGGER services_case_check
    BEFORE INSERT OR UPDATE ON services
    FOR EACH ROW EXECUTE FUNCTION check_case_insensitive_unique();

-- Нормализация строк
CREATE OR REPLACE FUNCTION normalize_string_on_update()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_TABLE_NAME = 'work_status' THEN
        NEW.status := normalize_string(NEW.status);
    ELSIF TG_TABLE_NAME = 'car_brands' THEN
        NEW.brand := normalize_string(NEW.brand);
    ELSIF TG_TABLE_NAME = 'car_colors' THEN
        NEW.color := normalize_string(NEW.color);
    ELSIF TG_TABLE_NAME = 'car_wraps' THEN
        NEW.status := normalize_string(NEW.status);
    ELSIF TG_TABLE_NAME = 'car_repaints' THEN
        NEW.status := normalize_string(NEW.status);
    ELSIF TG_TABLE_NAME = 'boxes' THEN
        NEW.type := normalize_string(NEW.type);
    ELSIF TG_TABLE_NAME = 'services' THEN
        NEW.name := normalize_string(NEW.name);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Добавляем триггеры для всех таблиц со строковыми полями
CREATE OR REPLACE TRIGGER normalize_work_status
    BEFORE INSERT OR UPDATE ON work_status
    FOR EACH ROW EXECUTE FUNCTION normalize_string_on_update();

CREATE OR REPLACE TRIGGER normalize_car_brands
    BEFORE INSERT OR UPDATE ON car_brands
    FOR EACH ROW EXECUTE FUNCTION normalize_string_on_update();

CREATE TRIGGER normalize_car_colors
    BEFORE INSERT OR UPDATE ON car_colors
    FOR EACH ROW EXECUTE FUNCTION normalize_string_on_update();

CREATE OR REPLACE TRIGGER normalize_car_wraps
    BEFORE INSERT OR UPDATE ON car_wraps
    FOR EACH ROW EXECUTE FUNCTION normalize_string_on_update();

CREATE OR REPLACE TRIGGER normalize_car_repaints
    BEFORE INSERT OR UPDATE ON car_repaints
    FOR EACH ROW EXECUTE FUNCTION normalize_string_on_update();

CREATE OR REPLACE TRIGGER normalize_boxes
    BEFORE INSERT OR UPDATE ON boxes
    FOR EACH ROW EXECUTE FUNCTION normalize_string_on_update();

CREATE OR REPLACE TRIGGER normalize_services
    BEFORE INSERT OR UPDATE ON services
    FOR EACH ROW EXECUTE FUNCTION normalize_string_on_update();

-- Сначала удаляем все триггеры для car_colors
DROP TRIGGER IF EXISTS normalize_car_colors ON car_colors;
DROP TRIGGER IF EXISTS car_colors_case_check ON car_colors;

-- Нормализация строк для отдельной таблицы car_colors
CREATE OR REPLACE FUNCTION normalize_car_colors()
RETURNS TRIGGER AS $$
BEGIN
    NEW.color := normalize_string(NEW.color);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Проверка уникальности для car_colors
CREATE OR REPLACE FUNCTION check_car_colors_unique()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM car_colors 
        WHERE normalize_string(color) = normalize_string(NEW.color)
        AND id != COALESCE(NEW.id, -1)
    ) THEN
        RAISE EXCEPTION 'Color "%" already exists (case-insensitive)', NEW.color;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Создаем новые триггеры для car_colors
CREATE OR REPLACE TRIGGER car_colors_normalize
    BEFORE INSERT OR UPDATE ON car_colors
    FOR EACH ROW EXECUTE FUNCTION normalize_car_colors();

CREATE OR REPLACE TRIGGER car_colors_unique
    BEFORE INSERT OR UPDATE ON car_colors
    FOR EACH ROW EXECUTE FUNCTION check_car_colors_unique();

-- Удаляем и создаем заново триггеры для boxes
DROP TRIGGER IF EXISTS normalize_boxes ON boxes;
DROP TRIGGER IF EXISTS boxes_case_check ON boxes;

-- Создаем новые триггеры для boxes
CREATE TRIGGER boxes_case_check
    BEFORE INSERT OR UPDATE ON boxes
    FOR EACH ROW EXECUTE FUNCTION check_case_insensitive_unique();

CREATE TRIGGER normalize_boxes
    BEFORE INSERT OR UPDATE ON boxes
    FOR EACH ROW EXECUTE FUNCTION normalize_string_on_update();

-- Удаляем все триггеры для boxes
DROP TRIGGER IF EXISTS normalize_boxes ON boxes;
DROP TRIGGER IF EXISTS boxes_case_check ON boxes;

-- Нормализация строк для boxes
CREATE OR REPLACE FUNCTION normalize_boxes()
RETURNS TRIGGER AS $$
BEGIN
    NEW.type := normalize_string(NEW.type);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Проверка уникальности для boxes
CREATE OR REPLACE FUNCTION check_boxes_unique()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM boxes 
        WHERE normalize_string(type) = normalize_string(NEW.type)
        AND id != COALESCE(NEW.id, -1)
    ) THEN
        RAISE EXCEPTION 'Box type "%" already exists (case-insensitive)', NEW.type;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Создаем отдельные триггеры для boxes
CREATE OR REPLACE  TRIGGER boxes_normalize
    BEFORE INSERT OR UPDATE ON boxes
    FOR EACH ROW EXECUTE FUNCTION normalize_boxes();

CREATE OR REPLACE  TRIGGER boxes_unique
    BEFORE INSERT OR UPDATE ON boxes
    FOR EACH ROW EXECUTE FUNCTION check_boxes_unique();

-- Удаляем все триггеры для services
DROP TRIGGER IF EXISTS normalize_services ON services;
DROP TRIGGER IF EXISTS services_case_check ON services;

-- Нормализация строк для services
CREATE OR REPLACE FUNCTION normalize_services()
RETURNS TRIGGER AS $$
BEGIN
    NEW.name := normalize_string(NEW.name);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Проверка уникальности для services
CREATE OR REPLACE FUNCTION check_services_unique()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM services 
        WHERE normalize_string(name) = normalize_string(NEW.name)
        AND id != COALESCE(NEW.id, -1)
    ) THEN
        RAISE EXCEPTION 'Service "%" already exists (case-insensitive)', NEW.name;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Создаем отдельные триггеры для services
CREATE OR REPLACE TRIGGER services_normalize
    BEFORE INSERT OR UPDATE ON services
    FOR EACH ROW EXECUTE FUNCTION normalize_services();

CREATE OR REPLACE TRIGGER services_unique
    BEFORE INSERT OR UPDATE ON services
    FOR EACH ROW EXECUTE FUNCTION check_services_unique();