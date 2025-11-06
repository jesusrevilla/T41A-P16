CREATE OR REPLACE FUNCTION calcular_valor_inventario()
RETURNS NUMERIC AS $$
DECLARE
    valor_total NUMERIC := 0;
BEGIN
    SELECT SUM(stock * precio_unitario) INTO valor_total
    FROM productos;

    RETURN valor_total;
END;
$$ LANGUAGE plpgsql;

-- 🧪 Ejemplo de uso:
-- SELECT calcular_valor_inventario();
