/* ============================================
   PROCEDIMIENTO registrar_movimiento
   ============================================ */
CREATE OR REPLACE PROCEDURE registrar_movimiento(
    p_producto_id INT,
    p_tipo TEXT,
    p_cantidad INT
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Registrar el movimiento en la tabla
    INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad)
    VALUES (p_producto_id, p_tipo, p_cantidad);

    -- Actualizar stock según tipo de movimiento
    IF p_tipo = 'entrada' THEN
        UPDATE productos
        SET stock = stock + p_cantidad
        WHERE id = p_producto_id;

    ELSIF p_tipo = 'salida' THEN
        UPDATE productos
        SET stock = stock - p_cantidad
        WHERE id = p_producto_id;
    END IF;
END;
$$;




/* ============================================
   FUNCIÓN calcular_valor_inventario
   ============================================ */
CREATE OR REPLACE FUNCTION calcular_valor_inventario()
RETURNS NUMERIC AS $$
DECLARE
    total NUMERIC := 0;
BEGIN
    SELECT SUM(stock * precio_unitario)
    INTO total
    FROM productos;

    RETURN COALESCE(total, 0);
END;
$$ LANGUAGE plpgsql;




/* ============================================
   FUNCIÓN DEL TRIGGER: registrar auditoría
   ============================================ */
CREATE OR REPLACE FUNCTION registrar_auditoria_stock()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO auditoria_stock (producto_id, stock_anterior, stock_nuevo)
    VALUES (OLD.id, OLD.stock, NEW.stock);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;




/* ============================================
   TRIGGER DE AUDITORÍA
   ============================================ */
CREATE TRIGGER trigger_auditoria_stock
AFTER UPDATE OF stock ON productos
FOR EACH ROW
WHEN (OLD.stock IS DISTINCT FROM NEW.stock)
EXECUTE FUNCTION registrar_auditoria_stock();

