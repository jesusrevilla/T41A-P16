CREATE OR REPLACE PROCEDURE registrar_movimiento(
    id_producto INT,
    tipo_movimiento TEXT,
    otra_cantidad INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    stock_actual INT;
BEGIN
    IF tipo_movimiento = 'salida' THEN
        
        SELECT stock INTO stock_actual FROM productos WHERE id = id_producto;
        
        IF stock_actual >= otra_cantidad THEN
            UPDATE productos 
            SET stock = stock - otra_cantidad
            WHERE id = id_producto;
            
            INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad)
            VALUES (id_producto, tipo_movimiento, otra_cantidad);
            
            RAISE NOTICE 'Venta registrada. Stock del producto % actualizado.', id_producto;
        END IF;

    ELSIF tipo_movimiento = 'entrada' THEN
        
        UPDATE productos
        SET stock = stock + otra_cantidad
        WHERE id = id_producto;
        
        INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad)
        VALUES (id_producto, tipo_movimiento, otra_cantidad);
        
        RAISE NOTICE 'Compra registrada. Stock del producto % actualizado.', id_producto;
    END IF;
    
END;
$$;
------------------------------------------------
-- Calcular valor del inventario
CREATE OR REPLACE FUNCTION calcular_valor_inventario()
RETURNS NUMERIC AS $$
DECLARE
    valor_total NUMERIC;
BEGIN
    SELECT COALESCE(SUM(stock * precio_unitario), 0)
    INTO valor_total
    FROM productos;
    
    RETURN valor_total;
END;
$$ LANGUAGE plpgsql;
-------------------------------------------------
-- Ver auditoría
CREATE OR REPLACE FUNCTION registrar_auditoria_stock()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO auditoria_stock (producto_id, stock_anterior, stock_nuevo)
    VALUES (OLD.id, OLD.stock, NEW.stock);
    
    RETURN NEW; 
END;
$$ LANGUAGE plpgsql;
SELECT * FROM auditoria_stock;

CREATE TRIGGER tr_auditoria_stock
AFTER UPDATE ON productos
FOR EACH ROW
WHEN (OLD.stock IS DISTINCT FROM NEW.stock)
EXECUTE FUNCTION registrar_auditoria_stock();
---------------------------------------------------------
-- Registrar movimientos
CALL registrar_movimiento(1, 'salida', 20);
CALL registrar_movimiento(2, 'entrada', 50);
SELECT * FROM productos;
SELECT calcular_valor_inventario();
SELECT * FROM auditoria_stock;



