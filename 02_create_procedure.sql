CREATE OR REPLACE PROCEDURE registrar_movimiento(
    p_producto_id INT,
    p_tipo TEXT,
    p_cantidad INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO movimientos_inventario(producto_id, tipo_movimiento, cantidad)
    VALUES (p_producto_id, p_tipo, p_cantidad);

    IF p_tipo = 'entrada' THEN
        UPDATE productos SET stock = stock + p_cantidad WHERE id = p_producto_id;
    ELSIF p_tipo = 'salida' THEN
        UPDATE productos SET stock = stock - p_cantidad WHERE id = p_producto_id;
    ELSE
        RAISE EXCEPTION 'Tipo de movimiento inválido: %', p_tipo;
    END IF;
END;
$$;
