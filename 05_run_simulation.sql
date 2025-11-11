-- Insertar productos 
INSERT INTO productos (nombre, stock, precio_unitario) VALUES ('Tornillo', 100, 0.50);
INSERT INTO productos (nombre, stock, precio_unitario) VALUES ('Tuerca', 200, 0.30);

-- Registrar movimientos (Llama al Procedimiento)
CALL registrar_movimiento(1, 'salida', 20);  -- Tornillo: 100 -> 80
CALL registrar_movimiento(2, 'entrada', 50); -- Tuerca: 200 -> 250

-- Calcular valor del inventario (Llama a la Función)
-- (80 * 0.50) + (250 * 0.30) = 40 + 75 = 115
SELECT calcular_valor_inventario();

-- Ver auditoría (Comprueba el Trigger)
SELECT * FROM auditoria_stock;
