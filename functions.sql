-- Función para calcular el valor total del inventario

CREATE OR REPLACE FUNCTION calcular_valor_inventario()
RETURNS NUMERIC AS $$
DECLARE
    total NUMERIC := 0;
BEGIN
    SELECT SUM(stock * precio_unitario) INTO total FROM productos;
    RETURN total;
END;
$$ LANGUAGE plpgsql;
