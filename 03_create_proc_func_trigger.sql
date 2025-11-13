CREATE OR REPLACE FUNCTION tf_log_auditoria_stock()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  IF NEW.stock IS DISTINCT FROM OLD.stock THEN
    INSERT INTO auditoria_stock (producto_id, stock_anterior, stock_nuevo)
    VALUES (OLD.id, OLD.stock, NEW.stock);
  END IF;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS tr_auditar_stock ON productos;
CREATE TRIGGER tr_auditar_stock
AFTER UPDATE OF stock ON productos
FOR EACH ROW
EXECUTE FUNCTION tf_log_auditoria_stock();

CREATE OR REPLACE PROCEDURE registrar_movimiento(
  p_producto_id INT,
  p_tipo        TEXT,
  p_cantidad    INT
)
LANGUAGE plpgsql
AS $$
DECLARE
  v_stock_actual INT;
  v_nuevo_stock  INT;
BEGIN
  IF p_tipo NOT IN ('entrada','salida') THEN
    RAISE EXCEPTION 'Tipo de movimiento inválido: %', p_tipo;
  END IF;

  IF p_cantidad IS NULL OR p_cantidad <= 0 THEN
    RAISE EXCEPTION 'La cantidad debe ser > 0';
  END IF;

  SELECT stock
    INTO v_stock_actual
    FROM productos
   WHERE id = p_producto_id
   FOR UPDATE;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'Producto % no existe', p_producto_id;
  END IF;

  IF p_tipo = 'entrada' THEN
    v_nuevo_stock := v_stock_actual + p_cantidad;
  ELSE
    v_nuevo_stock := v_stock_actual - p_cantidad;
    IF v_nuevo_stock < 0 THEN
      RAISE EXCEPTION 'Stock insuficiente: actual %, salida %', v_stock_actual, p_cantidad;
    END IF;
  END IF;

  UPDATE productos
     SET stock = v_nuevo_stock
   WHERE id = p_producto_id;

  INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad)
  VALUES (p_producto_id, p_tipo, p_cantidad);
END;
$$;


CREATE OR REPLACE FUNCTION calcular_valor_inventario()
RETURNS NUMERIC(20,2)
LANGUAGE sql
AS $$
  SELECT COALESCE(SUM(stock * precio_unitario), 0)::NUMERIC(20,2)
    FROM productos;
$$;
