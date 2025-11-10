CREATE PROCEDURE registrar_movimiento(
    p_producto_id INT,
    p_tipo_movimiento TEXT,
    p_cantidad INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_stock_actual INT;
BEGIN
    IF p_tipo_movimiento = 'salida' THEN

        SELECT stock INTO v_stock_actual FROM productos
        WHERE id = p_producto_id
        FOR UPDATE; 

        IF v_stock_actual < p_cantidad THEN
            RAISE EXCEPTION 'Stock insuficiente para el producto ID % (Stock actual: %, Solicitado: %)', 
                            p_producto_id, v_stock_actual, p_cantidad;
        END IF;

        UPDATE productos
        SET stock = stock - p_cantidad
        WHERE id = p_producto_id;

    ELSIF p_tipo_movimiento = 'entrada' THEN

        UPDATE productos
        SET stock = stock + p_cantidad
        WHERE id = p_producto_id;
        
    ELSE
        RAISE EXCEPTION 'Tipo de movimiento no válido: %', p_tipo_movimiento;
    END IF;

    INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad)
    VALUES (p_producto_id, p_tipo_movimiento, p_cantidad);
    
    RAISE NOTICE 'Movimiento registrado ID: %', p_producto_id;

END;
$$;





CREATE OR REPLACE FUNCTION calcular_valor_inventario()
RETURNS NUMERIC(10, 2)
LANGUAGE plpgsql
AS $$
DECLARE
    v_valor_total NUMERIC(10, 2);
BEGIN
    SELECT SUM(stock * precio_unitario)
    INTO v_valor_total
    FROM productos;
    
    RETURN v_valor_total;
END;
$$;



CREATE OR REPLACE FUNCTION auditar_cambio_stock()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO auditoria_stock (producto_id, stock_anterior, stock_nuevo)
    VALUES (NEW.id, OLD.stock, NEW.stock);
    
    RETURN NEW;
END;
$$;


DROP TRIGGER IF EXISTS trg_auditoria_stock ON productos;

CREATE TRIGGER trg_auditoria_stock
AFTER UPDATE ON productos
FOR EACH ROW
WHEN (OLD.stock IS DISTINCT FROM NEW.stock)
EXECUTE FUNCTION auditar_cambio_stock();



