-- Insertar productos
INSERT INTO productos (nombre, stock, precio_unitario) VALUES ('Tornillo', 100, 0.50);
INSERT INTO productos (nombre, stock, precio_unitario) VALUES ('Tuerca', 200, 0.30);

-- Registrar movimientos
CALL registrar_movimiento(1, 'salida', 20);
CALL registrar_movimiento(2, 'entrada', 50);

-- Calcular valor del inventario
SELECT calcular_valor_inventario();

-- Ver auditoría
SELECT * FROM auditoria_stock;
