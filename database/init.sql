-- Создание последовательностей для SERIAL полей (если их нет)
CREATE SEQUENCE IF NOT EXISTS services_id_seq;
CREATE SEQUENCE IF NOT EXISTS work_status_id_seq;
CREATE SEQUENCE IF NOT EXISTS car_brands_id_seq;
CREATE SEQUENCE IF NOT EXISTS car_models_id_seq;
CREATE SEQUENCE IF NOT EXISTS car_colors_id_seq;
CREATE SEQUENCE IF NOT EXISTS car_wraps_id_seq;
CREATE SEQUENCE IF NOT EXISTS appointments_id_seq;
CREATE SEQUENCE IF NOT EXISTS car_repaints_id_seq;
CREATE SEQUENCE IF NOT EXISTS users_id_seq;
CREATE SEQUENCE IF NOT EXISTS service_boxes_id_seq;

-- Создание таблиц (без удаления существующих)
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY DEFAULT nextval('services_id_seq'),
    name TEXT NOT NULL UNIQUE
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
    username VARCHAR(100) NOT NULL CHECK (LENGTH(TRIM(username)) > 0),
    phone_number VARCHAR(12) NOT NULL 
        CHECK (phone_number ~ '^\+7[0-9]{10}$'),
    CONSTRAINT users_phone_unique UNIQUE (phone_number)
);

CREATE TABLE IF NOT EXISTS service_boxes (
    id INTEGER PRIMARY KEY DEFAULT nextval('service_boxes_id_seq'),
    type TEXT NOT NULL UNIQUE
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

CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY DEFAULT nextval('appointments_id_seq'),
    box_id INTEGER NOT NULL REFERENCES service_boxes(id) ON DELETE RESTRICT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    plate_number TEXT NOT NULL REFERENCES cars(plate_number) ON DELETE RESTRICT,
    date DATE NOT NULL,
    status_id INTEGER NOT NULL REFERENCES work_status(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS appointment_services (
    appointment_id INTEGER REFERENCES appointments(id) ON DELETE CASCADE,
    service_id INTEGER REFERENCES services(id) ON DELETE RESTRICT,
    PRIMARY KEY (appointment_id, service_id)
);

-- Создание индексов для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_cars_user_id ON cars(user_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(date);
CREATE INDEX IF NOT EXISTS idx_appointments_user_id ON appointments(user_id);
CREATE INDEX IF NOT EXISTS idx_appointments_plate_number ON appointments(plate_number);
CREATE INDEX IF NOT EXISTS idx_car_models_brand_id ON car_models(brand_id);

-- Начальные данные для справочников
INSERT INTO work_status (status) VALUES
    ('Pending'),
    ('In Progress'),
    ('Completed'),
    ('Cancelled')
ON CONFLICT DO NOTHING;

INSERT INTO car_wraps (status) VALUES
    ('None'),
    ('Partial'),
    ('Full')
ON CONFLICT DO NOTHING;

INSERT INTO car_repaints (status) VALUES
    ('None'),
    ('Partial'),
    ('Full')
ON CONFLICT DO NOTHING;