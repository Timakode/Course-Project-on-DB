CREATE OR REPLACE PROCEDURE add_car_with_repaint(
    p_plate_number TEXT,
    p_user_id INTEGER,
    p_model_id INTEGER,
    p_year INTEGER,
    p_color_id INTEGER,
    p_wrap_id INTEGER,
    p_repaint_ids INTEGER[]  -- теперь только массив id статусов
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Добавляем автомобиль (без repaint_id)
    INSERT INTO cars (
        plate_number,
        user_id,
        model_id,
        year,
        color_id,
        wrap_id
    ) VALUES (
        UPPER(TRIM(p_plate_number)),
        p_user_id,
        p_model_id,
        p_year,
        p_color_id,
        p_wrap_id
    );

    -- Добавляем все связи с перекрасками
    INSERT INTO car_repaint_links (car_id, repaint_id)
    SELECT UPPER(TRIM(p_plate_number)), unnest(p_repaint_ids);
END;
$$;