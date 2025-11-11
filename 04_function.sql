CREATE OR REPLACE FUNCTION calcular_valor_inventario()
RETURNS NUMERIC AS $$
BEGIN 
  RETURN (SELECT SUM(stock*precio_unitario) FROM productos);
END;
$$ LANGUAGE plpgsql;
