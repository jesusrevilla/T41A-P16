CREATE OR REPLACE PROCEDURE registrar_movimiento(
    p_producto_id INT,
    p_tipo_movimiento TEXT,
    p_cantidad INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    stock_actual INT;
BEGIN
    SELECT stock INTO stock_actual FROM productos WHERE id = p_producto_id;
    
    IF p_tipo_movimiento = 'salida' AND p_cantidad > stock_actual THEN
        RAISE EXCEPTION 'No hay suficiente stock. Stock disponible: %, cantidad solicitada: %', 
                        stock_actual, p_cantidad;
    END IF;
    
    IF p_cantidad <= 0 THEN
        RAISE EXCEPTION 'La cantidad debe ser mayor a 0';
    END IF;
    
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
    END IF;
    
END;
$$;

-- Función para calcular el valor total del inventario
CREATE OR REPLACE FUNCTION calcular_valor_inventario()
RETURNS NUMERIC(10,2)
LANGUAGE plpgsql
AS $$
DECLARE
    total_valor NUMERIC(10,2);
BEGIN
    SELECT SUM(stock * precio_unitario) INTO total_valor
    FROM productos;
    
    RETURN COALESCE(total_valor, 0);
END;
$$;

-- Función para el trigger de auditoría
CREATE OR REPLACE FUNCTION registrar_auditoria_stock()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.stock IS DISTINCT FROM NEW.stock THEN
        INSERT INTO auditoria_stock (producto_id, stock_anterior, stock_nuevo)
        VALUES (OLD.id, OLD.stock, NEW.stock);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crear el trigger
CREATE TRIGGER trigger_auditoria_stock
AFTER UPDATE OF stock ON productos
FOR EACH ROW
EXECUTE FUNCTION registrar_auditoria_stock();
