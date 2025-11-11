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
    -- Verificar que el producto exista
    SELECT stock INTO v_stock_actual
    FROM productos
    WHERE id = p_producto_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'El producto con ID % no existe.', p_producto_id;
    END IF;

    -- Validar tipo de movimiento
    IF p_tipo_movimiento NOT IN ('entrada', 'salida') THEN
        RAISE EXCEPTION 'Tipo de movimiento inválido: %. Debe ser entrada o salida.', p_tipo_movimiento;
    END IF;

    -- Validar stock suficiente
    IF p_tipo_movimiento = 'salida' AND v_stock_actual < p_cantidad THEN
        RAISE EXCEPTION 'Stock insuficiente para la salida del producto con ID %.', p_producto_id;
    END IF;

    -- Registrar movimiento
    INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad)
    VALUES (p_producto_id, p_tipo_movimiento, p_cantidad);

    -- Actualizar stock del producto
    IF p_tipo_movimiento = 'entrada' THEN
        UPDATE productos
        SET stock = stock + p_cantidad
        WHERE id = p_producto_id;
    ELSE
        UPDATE productos
        SET stock = stock - p_cantidad
        WHERE id = p_producto_id;
    END IF;

    RAISE NOTICE 'Movimiento registrado exitosamente para el producto con ID %.', p_producto_id;
END;
$$;

-- 🧪 Ejemplo de uso:
-- CALL registrar_movimiento(1, 'salida', 20);
-- CALL registrar_movimiento(2, 'entrada', 50);