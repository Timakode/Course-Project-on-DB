-- Create sequences
CREATE SEQUENCE IF NOT EXISTS services_id_seq;
CREATE SEQUENCE IF NOT EXISTS work_status_id_seq;
CREATE SEQUENCE IF NOT EXISTS car_brands_id_seq;
CREATE SEQUENCE IF NOT EXISTS car_models_id_seq;
CREATE SEQUENCE IF NOT EXISTS car_colors_id_seq;
CREATE SEQUENCE IF NOT EXISTS car_wraps_id_seq;
CREATE SEQUENCE IF NOT EXISTS bookings_id_seq;
CREATE SEQUENCE IF NOT EXISTS car_repaints_id_seq;
CREATE SEQUENCE IF NOT EXISTS users_id_seq;
CREATE SEQUENCE IF NOT EXISTS boxes_id_seq;

-- Create tables
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY DEFAULT nextval('services_id_seq'),
    name TEXT NOT NULL UNIQUE,
    duration validated_duration NOT NULL  -- Добавляем поле с правильным типом
);

CREATE TABLE IF NOT EXISTS work_status (
    id INTEGER PRIMARY KEY DEFAULT nextval('work_status_id_seq'),
    status TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS car_brands (
    id INTEGER PRIMARY KEY DEFAULT nextval('car_brands_id_seq'),
    brand TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS car_models (
    id INTEGER PRIMARY KEY DEFAULT nextval('car_models_id_seq'),
    model TEXT NOT NULL,
    brand_id INTEGER NOT NULL REFERENCES car_brands(id) ON DELETE RESTRICT,
    UNIQUE(model, brand_id)
);

CREATE TABLE IF NOT EXISTS car_colors (
    id INTEGER PRIMARY KEY DEFAULT nextval('car_colors_id_seq'),
    color TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS car_wraps (
    id INTEGER PRIMARY KEY DEFAULT nextval('car_wraps_id_seq'),
    status TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS car_repaints (
    id INTEGER PRIMARY KEY DEFAULT nextval('car_repaints_id_seq'),
    status TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY DEFAULT nextval('users_id_seq'),
    username TEXT NOT NULL,
    phone_number TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS boxes (
    id INTEGER PRIMARY KEY DEFAULT nextval('boxes_id_seq'),
    type TEXT NOT NULL UNIQUE,
    capacity INTEGER NOT NULL CHECK (capacity > 0)
);

CREATE TABLE IF NOT EXISTS cars (
    plate_number TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    model_id INTEGER NOT NULL REFERENCES car_models(id) ON DELETE RESTRICT,
    year INTEGER NOT NULL CHECK (year BETWEEN 1900 AND EXTRACT(YEAR FROM CURRENT_DATE)),
    color_id INTEGER NOT NULL REFERENCES car_colors(id) ON DELETE RESTRICT,
    wrap_id INTEGER NOT NULL REFERENCES car_wraps(id) ON DELETE RESTRICT,
    repaint_id INTEGER NOT NULL REFERENCES car_repaints(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY DEFAULT nextval('bookings_id_seq'),
    box_id INTEGER NOT NULL REFERENCES boxes(id) ON DELETE RESTRICT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    plate_number TEXT NOT NULL REFERENCES cars(plate_number) ON DELETE RESTRICT,
    date DATE NOT NULL,
    status_id INTEGER NOT NULL REFERENCES work_status(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS book_services (
    booking_id INTEGER REFERENCES bookings(id) ON DELETE CASCADE,
    service_id INTEGER REFERENCES services(id) ON DELETE RESTRICT,
    PRIMARY KEY (booking_id, service_id)
);

-- Create types and domain
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'duration_unit') THEN
        CREATE TYPE duration_unit AS ENUM ('minutes', 'days');
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'service_duration') THEN
        CREATE TYPE service_duration AS (
            value INTEGER,
            unit duration_unit
        );
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'validated_duration') THEN
        CREATE DOMAIN validated_duration AS service_duration
            CONSTRAINT valid_duration_value CHECK (
                (((VALUE).unit = 'minutes' AND (VALUE).value BETWEEN 15 AND 480)) OR
                ((VALUE).unit = 'days' AND (VALUE).value BETWEEN 1 AND 30)
            );
    END IF;
END $$;

-- Удаляем тип car_part если он существует
DROP TYPE IF EXISTS car_part CASCADE;

-- Создаем таблицу связи для перекрашенных элементов
CREATE TABLE IF NOT EXISTS car_repaint_links (
    car_id TEXT REFERENCES cars(plate_number) ON DELETE CASCADE,
    repaint_id INTEGER REFERENCES car_repaints(id) ON DELETE RESTRICT,
    PRIMARY KEY (car_id, repaint_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_cars_user_id ON cars(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings(date);
CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_plate_number ON bookings(plate_number);
CREATE INDEX IF NOT EXISTS idx_car_models_brand_id ON car_models(brand_id);
