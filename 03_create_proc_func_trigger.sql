-- Función y trigger para auditoría de cambios en el stock

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

-- Función para calcular el valor total del inventario

CREATE OR REPLACE FUNCTION calcular_valor_inventario()
RETURNS NUMERIC AS $$
DECLARE
    total NUMERIC := 0;
BEGIN
    SELECT SUM(stock * precio_unitario) INTO total FROM productos;
    RETURN total;
END;
$$ LANGUAGE plpgsql;
     
-- Procedimiento para registrar movimientos de inventario

CREATE OR REPLACE PROCEDURE registrar_movimiento(pid INT, tipo TEXT, cantidad INT)
LANGUAGE plpgsql AS $$
BEGIN
    IF tipo = 'entrada' THEN
        UPDATE productos SET stock = stock + cantidad WHERE id = pid;
    ELSIF tipo = 'salida' THEN
        UPDATE productos SET stock = stock - cantidad WHERE id = pid;
    END IF;

    INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad)
    VALUES (pid, tipo, cantidad);
END;
$$;
