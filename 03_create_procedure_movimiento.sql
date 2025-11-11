CREATE PROCEDURE registrar_movimiento(
    IN p_producto_id INT,
    IN p_tipo_movimiento TEXT,
    IN p_cantidad INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 1. Actualizar el stock en la tabla de productos
    -- Esto disparará el trigger de auditoría automáticamente
    IF p_tipo_movimiento = 'entrada' THEN
        UPDATE productos
        SET stock = stock + p_cantidad
        WHERE id = p_producto_id;
    ELSIF p_tipo_movimiento = 'salida' THEN
        UPDATE productos
        SET stock = stock - p_cantidad
        WHERE id = p_producto_id;
    END IF;

    -- 2. Registrar el movimiento en la tabla de movimientos
    INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad)
    VALUES (p_producto_id, p_tipo_movimiento, p_cantidad);
END;
$$;
