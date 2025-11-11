CREATE OR REPLACE FUNCTION registrar_auditoria_stock()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.stock IS DISTINCT FROM OLD.stock THEN
        INSERT INTO auditoria_stock (producto_id, stock_anterior, stock_nuevo)
        VALUES (OLD.id, OLD.stock, NEW.stock);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auditoria_stock
AFTER UPDATE OF stock ON productos
FOR EACH ROW
EXECUTE FUNCTION registrar_auditoria_stock();