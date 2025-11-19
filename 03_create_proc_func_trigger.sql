CREATE OR REPLACE PROCEDURE registrar_movimiento(
    p_producto_id INT,
    p_tipo_movimiento TEXT,
    p_cantidad INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad)
    VALUES (p_producto_id, p_tipo_movimiento, p_cantidad);

    IF p_tipo_movimiento = 'entrada' THEN
        UPDATE productos
        SET stock = stock + p_cantidad
        WHERE id = p_producto_id;
    ELSIF p_tipo_movimiento = 'salida' THEN
        UPDATE productos
        SET stock = stock - p_cantidad
        WHERE id = p_producto_id;
    ELSE
        RAISE EXCEPTION 'Tipo de movimiento inválido: %', p_tipo_movimiento;
    END IF;
END;
$$;


CREATE OR REPLACE FUNCTION calcular_valor_inventario()
RETURNS NUMERIC AS $$
DECLARE
    total NUMERIC(12,2);
BEGIN
    SELECT SUM(stock * precio_unitario)
    INTO total
    FROM productos;

    RETURN COALESCE(total, 0);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION registrar_auditoria_stock()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO auditoria_stock (producto_id, stock_anterior, stock_nuevo)
    VALUES (OLD.id, OLD.stock, NEW.stock);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auditoria_stock
AFTER UPDATE OF stock ON productos
FOR EACH ROW
WHEN (OLD.stock IS DISTINCT FROM NEW.stock)
EXECUTE FUNCTION registrar_auditoria_stock();
