-- Drop existing triggers first
DROP TRIGGER IF EXISTS before_insert_phone_number ON users;
DROP TRIGGER IF EXISTS after_insert_log ON appointments;
DROP TRIGGER IF EXISTS before_update_appointment_date ON appointments;
DROP TRIGGER IF EXISTS after_update_status ON appointments;
DROP TRIGGER IF EXISTS before_delete_appointment ON appointments;
DROP TRIGGER IF EXISTS after_delete_appointment ON appointments;

-- Trigger functions

-- 1. BEFORE INSERT trigger to check phone number
CREATE OR REPLACE FUNCTION check_phone_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT NEW.phone_number ~ '^\+7[0-9]{10}$' THEN
        RAISE EXCEPTION 'Invalid phone number format. Use format: +7XXXXXXXXXX';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_insert_phone_number
    BEFORE INSERT ON users
    FOR EACH ROW
    EXECUTE FUNCTION check_phone_number();

-- 2. AFTER INSERT trigger to log new records
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    record_id TEXT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION log_new_record()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, operation, record_id)
    VALUES (TG_TABLE_NAME, TG_OP, NEW.id::TEXT);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_insert_log
    AFTER INSERT ON appointments
    FOR EACH ROW
    EXECUTE FUNCTION log_new_record();

-- 3. BEFORE UPDATE trigger to check appointment date
CREATE OR REPLACE FUNCTION check_appointment_date()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.date < CURRENT_DATE THEN
        RAISE EXCEPTION 'Cannot set appointment date in the past';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_update_appointment_date
    BEFORE UPDATE ON appointments
    FOR EACH ROW
    EXECUTE FUNCTION check_appointment_date();

-- 4. AFTER UPDATE trigger to track status changes
CREATE TABLE IF NOT EXISTS status_changes (
    id SERIAL PRIMARY KEY,
    appointment_id INTEGER NOT NULL,
    old_status INTEGER,
    new_status INTEGER,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION track_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status_id != NEW.status_id THEN
        INSERT INTO status_changes (appointment_id, old_status, new_status)
        VALUES (NEW.id, OLD.status_id, NEW.status_id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_update_status
    AFTER UPDATE ON appointments
    FOR EACH ROW
    EXECUTE FUNCTION track_status_change();

-- 5. BEFORE DELETE trigger to prevent deletion of active appointments
CREATE OR REPLACE FUNCTION prevent_delete_active_appointment()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status_id IN (
        SELECT id FROM work_status WHERE status IN ('In Progress', 'Pending')
    ) THEN
        RAISE EXCEPTION 'Cannot delete active appointment';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_delete_appointment
    BEFORE DELETE ON appointments
    FOR EACH ROW
    EXECUTE FUNCTION prevent_delete_active_appointment();

-- 6. AFTER DELETE trigger to clean up unused cars
CREATE OR REPLACE FUNCTION cleanup_unused_cars()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM cars
    WHERE plate_number NOT IN (SELECT DISTINCT plate_number FROM appointments);
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_delete_appointment
    AFTER DELETE ON appointments
    FOR EACH ROW
    EXECUTE FUNCTION cleanup_unused_cars();