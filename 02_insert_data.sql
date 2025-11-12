INSERT INTO productos (nombre, stock, precio_unitario) VALUES ('Tornillo', 100, 0.50);
INSERT INTO productos (nombre, stock, precio_unitario) VALUES ('Tuerca', 200, 0.30);



03_create_proc_func_trigger.sql
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
