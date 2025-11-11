CREATE OR REPLACE PROCEDURE registrar_movimiento(p_producto_id INT, p_tipo TEXT, p_cantidad INT)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad)
    VALUES (p_producto_id, p_tipo, p_cantidad);

    IF p_tipo = 'entrada' THEN
        UPDATE productos
        SET stock = stock + p_cantidad
        WHERE id = p_producto_id;
    ELSIF p_tipo = 'salida' THEN
        UPDATE productos
        SET stock = stock - p_cantidad
        WHERE id = p_producto_id;
    ELSE
        RAISE EXCEPTION 'Movimiento no valido';
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION registrar_auditoria_stock()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO auditoria_stock (producto_id, stock_anterior, stock_nuevo) VALUES (OLD.id, OLD.stock, NEW.stock);
    RETURN NEW;
END;
$$;


CREATE TRIGGER trigger_registrar_auditoria_stock
AFTER UPDATE OF stock ON productos
FOR EACH ROW
EXECUTE PROCEDURE registrar_auditoria_stock();

CALL registrar_movimiento(1, 'salida', 20);

CREATE OR REPLACE FUNCTION calcular_valor_inventario()
RETURNS NUMERIC (12,2) 
LANGUAGE plpgsql 
AS $$ 
DECLARE
    total NUMERIC(12,2);
BEGIN
    SELECT SUM(stock * precio_unitario) INTO total FROM productos;
    
    IF total IS NULL THEN
        RETURN 0;
    ELSE
        RETURN total;
    END IF; 
END;
$$;

SELECT calcular_valor_inventario();
