-- Drop existing triggers first
DROP TRIGGER IF EXISTS user_view_trigger ON управление_пользователями;

-- Drop existing views
DROP VIEW IF EXISTS car_full_info;
DROP VIEW IF EXISTS active_appointments;
DROP VIEW IF EXISTS service_statistics;
DROP VIEW IF EXISTS box_workload;
DROP VIEW IF EXISTS user_management;

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

-- Active appointments view
CREATE OR REPLACE VIEW active_appointments AS
SELECT 
    a.id,
    a.date,
    u.username,
    u.phone_number,
    c.plate_number,
    sb.type as box_type,
    ws.status as work_status
FROM appointments a
JOIN users u ON a.user_id = u.id
JOIN cars c ON a.plate_number = c.plate_number
JOIN service_boxes sb ON a.box_id = sb.id
JOIN work_status ws ON a.status_id = ws.id
WHERE ws.status IN ('Pending', 'In Progress');

-- Service statistics view
CREATE OR REPLACE VIEW service_statistics AS
SELECT 
    s.name,
    COUNT(aps.appointment_id) as orders_count,
    COUNT(DISTINCT a.user_id) as clients_count
FROM services s
LEFT JOIN appointment_services aps ON s.id = aps.service_id
LEFT JOIN appointments a ON aps.appointment_id = a.id
GROUP BY s.id, s.name;

-- Box workload view
CREATE OR REPLACE VIEW box_workload AS
SELECT 
    sb.type as box_type,
    COUNT(a.id) as total_appointments,
    COUNT(CASE WHEN ws.status = 'In Progress' THEN 1 END) as active_appointments,
    COUNT(CASE WHEN ws.status = 'Completed' THEN 1 END) as completed_appointments
FROM service_boxes sb
LEFT JOIN appointments a ON sb.id = a.box_id
LEFT JOIN work_status ws ON a.status_id = ws.id
GROUP BY sb.id, sb.type;

-- User management view
CREATE OR REPLACE VIEW user_management AS
SELECT 
    id,
    username,
    phone_number,
    (SELECT COUNT(*) FROM cars WHERE user_id = u.id) as cars_count,
    (SELECT COUNT(*) FROM appointments WHERE user_id = u.id) as appointments_count
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