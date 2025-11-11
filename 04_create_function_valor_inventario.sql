CREATE FUNCTION calcular_valor_inventario()
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    valor_total NUMERIC;
BEGIN
    -- Suma el (stock * precio_unitario) para todos los productos
    SELECT SUM(stock * precio_unitario)
    INTO valor_total
    FROM productos;
    
    -- Devuelve el valor calculado
    RETURN valor_total;
END;
$$;
