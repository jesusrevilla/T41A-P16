CREATE PROCEDURE registrar_movimiento(id_value INTEGER, tipo TEXT, cantidad INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
  stock_value INTEGER;
BEGIN
  INSERT INTO movimientos_inventario(producto_id, tipo_movimiento, cantidad) VALUES (id_value,tipo,cantidad);
  SELECT stock INTO stock_value FROM productos WHERE productos.id=id_value;

  IF tipo='entrada' THEN
    stock_value = stock_value + cantidad;
  ELSIF tipo='salida' THEN
    stock_value = stock_value - cantidad;
  END IF;

  UPDATE productos SET stock = stock_value WHERE productos.id = id_value;
END;
$$;


CREATE OR REPLACE FUNCTION registrar_cambios_stock()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO auditoria_stock(producto_id,stock_anterior,stock_nuevo,fecha) VALUES (OLD.id,OLD.stock,NEW.stock,NOW());
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION calcular_valor_inventario()
RETURNS NUMERIC(10,2) AS $$
DECLARE
  valor NUMERIC(10,2);
BEGIN
  SELECT SUM(stock*precio_unitario) INTO valor FROM productos;
  RETURN valor;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auditoria_stock
AFTER UPDATE OF stock ON productos
FOR EACH row 
WHEN (OLD.stock IS DISTINCT FROM NEW.stock)
EXECUTE FUNCTION registrar_cambios_stock();
