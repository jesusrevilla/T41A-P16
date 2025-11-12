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

--Función
CREATE OR REPLACE FUNCTION calcular_valor_inventario()
RETURNS NUMERIC(10,2) AS $$
DECLARE
    v_total NUMERIC(10,2);
BEGIN
    SELECT SUM(stock * precio_unitario) INTO v_total FROM productos;
    RETURN v_total;
END;
$$ LANGUAGE plpgsql;

--Trigger
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
