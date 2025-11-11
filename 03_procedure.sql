CREATE OR REPLACE PROCEDURE registrar_movimiento(
  IN id_p INT,
  IN tipo TEXT,
  IN cant INT
)
LANGUAGE plpgsql
AS $$
DECLARE
  stock_anterior INT;
  stock_nuevo INT;
BEGIN
  SELECT stock INTO stock_anterior FROM productos WHERE id = id_p;
  IF tipo = 'salida' THEN
    IF stock_anterior >= cant THEN
      INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad)
      VALUES (id_p, tipo, cant);
      UPDATE productos SET stock = stock - cant WHERE id = id_p;
    ELSE
      RAISE NOTICE 'No hay suficiente stock para realizar la salida.';
      RETURN;
    END IF;

  ELSIF tipo = 'entrada' THEN
    INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad)
    VALUES (id_p, tipo, cant);
    UPDATE productos SET stock = stock + cant WHERE id = id_p;
  ELSE
    RAISE NOTICE 'Tipo de movimiento inválido. Use "entrada" o "salida".';
    RETURN;
  END IF;
END;
$$;
