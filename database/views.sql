-- Drop existing triggers first
DROP TRIGGER IF EXISTS user_view_trigger ON управление_пользователями;

-- Drop existing views
DROP VIEW IF EXISTS car_model_details CASCADE;
DROP VIEW IF EXISTS car_full_info CASCADE;
DROP VIEW IF EXISTS active_bookings CASCADE;
DROP VIEW IF EXISTS service_statistics CASCADE;
DROP VIEW IF EXISTS box_workload CASCADE;
DROP VIEW IF EXISTS user_management CASCADE;

-- Представление для отображения моделей с их брендами (перемещаем в начало)
CREATE OR REPLACE VIEW car_model_details AS
SELECT 
    m.id,
    m.model,
    m.brand_id,
    b.brand
FROM car_models m
JOIN car_brands b ON m.brand_id = b.id;

-- Full car information view
CREATE OR REPLACE VIEW car_full_info AS
SELECT 
    c.plate_number,
    u.username,
    u.phone_number,
    cb.brand,
    cm.model,
    c.year,
    cc.color,
    cw.status as wrap_status,
    cr.status as repaint_status
FROM cars c
JOIN users u ON c.user_id = u.id
JOIN car_models cm ON c.model_id = cm.id
JOIN car_brands cb ON cm.brand_id = cb.id
JOIN car_colors cc ON c.color_id = cc.id
JOIN car_wraps cw ON c.wrap_id = cw.id
JOIN car_repaints cr ON c.repaint_id = cr.id;

-- Active bookings view
CREATE OR REPLACE VIEW active_bookings AS
SELECT 
    b.id,
    b.date,
    u.username,
    u.phone_number,
    c.plate_number,
    bx.type as box_type,
    ws.status as work_status
FROM bookings b
JOIN users u ON b.user_id = u.id
JOIN cars c ON b.plate_number = c.plate_number
JOIN boxes bx ON b.box_id = bx.id
JOIN work_status ws ON b.status_id = ws.id
WHERE ws.status IN ('Pending', 'In Progress');

-- Service statistics view
CREATE OR REPLACE VIEW service_statistics AS
SELECT 
    s.name,
    COUNT(bs.booking_id) as orders_count,
    COUNT(DISTINCT b.user_id) as clients_count
FROM services s
LEFT JOIN book_services bs ON s.id = bs.service_id
LEFT JOIN bookings b ON bs.booking_id = b.id
GROUP BY s.id, s.name;

-- Box workload view
CREATE OR REPLACE VIEW box_workload AS
SELECT 
    bx.type as box_type,
    COUNT(b.id) as total_bookings,
    COUNT(CASE WHEN ws.status = 'In Progress' THEN 1 END) as active_bookings,
    COUNT(CASE WHEN ws.status = 'Completed' THEN 1 END) as completed_bookings
FROM boxes bx
LEFT JOIN bookings b ON bx.id = b.box_id
LEFT JOIN work_status ws ON b.status_id = ws.id
GROUP BY bx.id, bx.type;

-- User management view
CREATE OR REPLACE VIEW user_management AS
SELECT 
    id,
    username,
    phone_number,
    (SELECT COUNT(*) FROM cars WHERE user_id = u.id) as cars_count,
    (SELECT COUNT(*) FROM bookings WHERE user_id = u.id) as bookings_count
FROM users u;

-- Create trigger for user management view
CREATE OR REPLACE FUNCTION update_user_management()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO users (username, phone_number)
        VALUES (NEW.username, NEW.phone_number);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        UPDATE users
        SET username = NEW.username,
            phone_number = NEW.phone_number
        WHERE id = OLD.id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        DELETE FROM users WHERE id = OLD.id;
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER user_management_trigger
INSTEAD OF INSERT OR UPDATE OR DELETE ON user_management
FOR EACH ROW EXECUTE FUNCTION update_user_management();