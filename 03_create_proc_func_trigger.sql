CREATE OR REPLACE PROCEDURE registrar_movimiento(producto_id INTEGER, tipo_movimiento TEXT, cantidad INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    valor_stock INTEGER;
BEGIN
    IF cantidad IS NULL OR cantidad <= 0 THEN
        RAISE EXCEPTION 'Cantidad inválida: %', cantidad;
    END IF;

    IF tipo_movimiento NOT IN ('entrada', 'salida') THEN
        RAISE EXCEPTION 'Tipo de movimiento inválido: %', tipo_movimiento;
    END IF;

    SELECT stock INTO valor_stock
    FROM productos
    WHERE id = producto_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Producto no encontrado: %', producto_id;
    END IF;

    INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad, usuario)
    VALUES (producto_id, tipo_movimiento, cantidad, current_user);

    IF tipo_movimiento = 'entrada' THEN
        valor_stock := valor_stock + cantidad;
    ELSIF tipo_movimiento = 'salida' THEN
        IF valor_stock < cantidad THEN
            RAISE EXCEPTION 'Stock insuficiente: % solicitado, % disponible', cantidad, valor_stock;
        END IF;
        valor_stock := valor_stock - cantidad;
    END IF;

    UPDATE productos
    SET stock = valor_stock
    WHERE id = producto_id;
END;
$$;

CREATE OR REPLACE FUNCTION calcular_valor_inventario()
RETURNS NUMERIC(10, 2)
LANGUAGE plpgsql
AS $$
DECLARE
    total NUMERIC(12,2);
BEGIN
    SELECT COALESCE(SUM(stock * precio_unitario), 0.00) INTO total
    FROM productos;

    RETURN total;
END;
$$;

CREATE OR REPLACE FUNCTION registro_cambios_stock()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.stock IS DISTINCT FROM NEW.stock THEN
        INSERT INTO auditoria_stock (producto_id, stock_anterior, stock_nuevo, fecha_registro)
        VALUES (OLD.id, OLD.stock, NEW.stock, NOW());
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trigger_auditoria_stock ON productos;

CREATE TRIGGER trigger_auditoria_stock
AFTER UPDATE OF stock ON productos
FOR EACH ROW
WHEN (OLD.stock IS DISTINCT FROM NEW.stock)
EXECUTE FUNCTION registro_cambios_stock();
