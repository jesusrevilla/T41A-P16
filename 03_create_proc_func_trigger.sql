CREATE OR REPLACE PROCEDURE registrar_movimiento(
    p_producto_id INT,
    p_tipo_movimiento TEXT,
    p_cantidad INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_stock_actual INT;
BEGIN
    SELECT stock INTO v_stock_actual FROM productos WHERE id = p_producto_id;

    IF p_tipo_movimiento = 'entrada' THEN
        UPDATE productos SET stock = stock + p_cantidad WHERE id = p_producto_id;
    ELSIF p_tipo_movimiento = 'salida' THEN
        IF v_stock_actual < p_cantidad THEN
            RAISE EXCEPTION 'Stock insuficiente para salida';
        END IF;
        UPDATE productos SET stock = stock - p_cantidad WHERE id = p_producto_id;
    ELSE
        RAISE EXCEPTION 'Tipo de movimiento inválido';
    END IF;

    INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad)
    VALUES (p_producto_id, p_tipo_movimiento, p_cantidad);
END;
$$;
