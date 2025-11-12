-- Procedimiento para registrar movimientos de inventario

CREATE OR REPLACE PROCEDURE registrar_movimiento(pid INT, tipo TEXT, cantidad INT)
LANGUAGE plpgsql AS $$
BEGIN
    IF tipo = 'entrada' THEN
        UPDATE productos SET stock = stock + cantidad WHERE id = pid;
    ELSIF tipo = 'salida' THEN
        UPDATE productos SET stock = stock - cantidad WHERE id = pid;
    END IF;

    INSERT INTO movimientos_inventario (producto_id, tipo_movimiento, cantidad)
    VALUES (pid, tipo, cantidad);
END;
$$;
