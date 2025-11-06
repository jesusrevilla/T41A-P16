-- Ver estado inicial
SELECT * FROM productos;

-- Registrar movimientos
CALL registrar_movimiento(1, 'salida', 20);
CALL registrar_movimiento(2, 'entrada', 50);
CALL registrar_movimiento(3, 'salida', 10);

-- Consultar productos actualizados
SELECT * FROM productos;

-- Calcular el valor actual del inventario
SELECT calcular_valor_inventario();

-- Ver los movimientos registrados
SELECT * FROM movimientos_inventario;

-- Ver auditoría de cambios en stock
SELECT * FROM auditoria_stock;
