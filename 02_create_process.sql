CREATE OR REPLACE PROCEDURE registrar_movimiento(
  IN id_prod INT,
  IN tipo TEXT,
  IN cantidad_mov INT
)
LANGUAGE plpgsql
AS $$
DECLARE
  cantidad_base INT;
BEGIN
  -- Validar existencia del producto
  SELECT stock INTO cantidad_base FROM productos WHERE id = id_prod;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Producto con ID % no existe.', id_prod;
  END IF;

  -- Validar stock suficiente en caso de salida
  IF tipo = 'salida' AND cantidad_mov > cantidad_base THEN
    RAISE EXCEPTION 'STOCK INSUFICIENTE: disponible %, solicitado %', cantidad_base, cantidad_mov;
  END IF;

  -- Registrar movimiento
  INSERT INTO movimientos_inventario(producto_id, tipo_movimiento, cantidad)
  VALUES (id_prod, tipo, cantidad_mov);

  -- Actualizar stock
  IF tipo = 'salida' THEN
    UPDATE productos SET stock = stock - cantidad_mov WHERE id = id_prod;
  ELSIF tipo = 'entrada' THEN
    UPDATE productos SET stock = stock + cantidad_mov WHERE id = id_prod;
  ELSE
    RAISE EXCEPTION 'Tipo de movimiento inválido: %', tipo;
  END IF;
END;
$$;

CREATE OR REPLACE FUNCTION calcular_valor_inventario()
RETURNS NUMERIC AS $$
BEGIN
    --Suma del inventario total
    RETURN (SELECT SUM(stock * precio_unitario) FROM productos);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION registrar_auditoria_stock()
RETURNS TRIGGER AS $$
BEGIN
    --Insertar en tabla de auditoria
    INSERT INTO auditoria_stock (producto_id, stock_anterior, stock_nuevo)
    VALUES (OLD.id, OLD.stock, NEW.stock);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

--Creación del Trigger
CREATE TRIGGER trigger_auditoria_stock
AFTER UPDATE OF stock ON productos
FOR EACH ROW
WHEN (OLD.stock IS DISTINCT FROM NEW.stock)
EXECUTE FUNCTION registrar_auditoria_stock();
