--procedimiento
--Registra un movimiento de inventario y actualiza el stock del producto.
CREATE PROCEDURE registrar_movimiento(producto_id INTEGER, tipo_movimiento TEXT, cantidad INTEGER)
LANGUAGE plpgsql
AS $$
  DECLARE valor_stock INTEGER;
BEGIN
    INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad) VALUES (producto_id, tipo_movimiento, cantidad);
    SELECT stock INTO valor_stock FROM productos WHERE productos.id = producto_id;
    IF tipo_movimiento='entrada' THEN
      valor_stock = valor_stock + cantidad;
    ELSIF tipo_movimiento='salida' THEN
      valor_stock = valor_stock - cantidad;
    END IF;
    UPDATE productos SET stock = valor_stock WHERE productos.id = producto_id;
END;
$$;

--función
--Calcula el valor total del inventario actual.
CREATE OR REPLACE FUNCTION calcular_valor_inventario()
RETURNS NUMERIC(10, 2) AS $$
BEGIN
    RETURN( SELECT SUM(stock * precio_unitario) FROM productos);
END;
$$ LANGUAGE plpgsql;

--trigger
--Registra automáticamente los cambios en el stock de productos.
CREATE OR REPLACE FUNCTION registro_cambios_stock()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO auditoria_stock(producto_id,stock_anterior,stock_nuevo,fecha) VALUES (OLD.id,OLD.stock,NEW.stock,NOW());
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auditoria_stock
AFTER UPDATE OF stock ON productos
FOR EACH row 
WHEN (OLD.stock IS DISTINCT FROM NEW.stock)
EXECUTE FUNCTION registro_cambios_stock();
-------------------------------------------------------------------------------------
