CREATE OR REPLACE PROCEDURE registrar_movimiento(producto_id INTEGER, tipo_movimiento TEXT, cantidad INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    valor_stock INTEGER;
BEGIN
    SELECT stock INTO valor_stock FROM productos WHERE id = producto_id;
    IF tipo_movimiento = 'entrada' THEN
        valor_stock := valor_stock + cantidad;
    ELSIF tipo_movimiento = 'salida' THEN
        valor_stock := valor_stock - cantidad;
    END IF;
    UPDATE productos SET stock = valor_stock WHERE id = producto_id;
    INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad)
    VALUES (producto_id, tipo_movimiento, cantidad);
END;
$$;

CREATE OR REPLACE FUNCTION calcular_valor_inventario()
RETURNS NUMERIC(10, 2)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN (SELECT SUM(stock * precio_unitario) FROM productos);
END;
$$;

CREATE OR REPLACE FUNCTION registrar_auditoria_stock()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO auditoria_stock (producto_id, stock_anterior, stock_nuevo)
    VALUES (OLD.id, OLD.stock, NEW.stock);
    RETURN NEW;
END;
$$;

CREATE TRIGGER trigger_auditoria_stock
AFTER UPDATE OF stock ON productos
FOR EACH ROW
WHEN (OLD.stock IS DISTINCT FROM NEW.stock)
EXECUTE FUNCTION registrar_auditoria_stock();
