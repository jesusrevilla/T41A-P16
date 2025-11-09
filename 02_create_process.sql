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
  SELECT stock INTO cantidad_base FROM productos WHERE id=id_prod
  IF tipo='SALIDA' and cantidad_mov>cantidad_base THEN
    RAISE NOTICE 'STOCK INSUFICIENTE'
    RETURN
  ELSE
    INSERT INTO movimientos_inventario(producto_id,tipo_movimiento,cantidad) VALUES (id_prod,tipo,cantidad_mov);
    IF tipo='SALIDA' THEN
      UPDATE productos SET stock=cantidad_base-cantidad_mov WHERE productos.id=id_prod
    ELSIF tipo='ENTRADA' THEN
      UPDATE productos SET stock=cantidad_base+cantidad_mov WHERE id=id_prod
    END IF;
  END IF;    
END;
$$;

CREATE OR REPLACE FUNCTION calcular_desc(monto NUMERIC, descuento NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
    IF descuento<=0 or descuento>=1 THEN
      RAISE NOTICE 'FORMATO DE DESCUENTO INCORRECTO( DEBE SER FORMATO DECIMAL 50%%=>0.5)';
      RETURN Null;
    ELSE 
      RETURN monto*(1-descuento);
    END IF;
END;
$$ LANGUAGE plpgsql;
