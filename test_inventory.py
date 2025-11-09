import pytest
import psycopg2
import os

# Configuración de la base de datos de prueba
DB_CONFIG = {
    'host': 'localhost',
    'database': 'test_db',
    'user': 'postgres',
    'password': 'postgres',
    'port': 5432
}

def get_connection():
    """Obtener conexión a la base de datos"""
    return psycopg2.connect(**DB_CONFIG)

def test_initial_data():
    """Verificar que los datos iniciales se insertaron correctamente"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Verificar productos insertados
    cur.execute("SELECT COUNT(*) FROM productos")
    count = cur.fetchone()[0]
    assert count == 5, f"Se esperaban 5 productos, se encontraron {count}"
    
    # Verificar datos específicos
    cur.execute("SELECT nombre, stock, precio_unitario FROM productos WHERE nombre = 'Tornillo'")
    producto = cur.fetchone()
    assert producto is not None
    assert producto[0] == 'Tornillo'
    assert producto[1] == 100
    assert producto[2] == 0.50
    
    cur.close()
    conn.close()

def test_registrar_movimiento_entrada():
    """Probar el procedimiento de registrar movimiento de entrada"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Stock inicial
    cur.execute("SELECT stock FROM productos WHERE id = 1")
    stock_inicial = cur.fetchone()[0]
    
    # Registrar entrada
    cur.execute("CALL registrar_movimiento(1, 'entrada', 50)")
    conn.commit()
    
    # Verificar stock actualizado
    cur.execute("SELECT stock FROM productos WHERE id = 1")
    stock_final = cur.fetchone()[0]
    assert stock_final == stock_inicial + 50
    
    # Verificar movimiento registrado
    cur.execute("SELECT cantidad, tipo_movimiento FROM movimientos_inventario WHERE producto_id = 1 ORDER BY id DESC LIMIT 1")
    movimiento = cur.fetchone()
    assert movimiento is not None
    assert movimiento[0] == 50
    assert movimiento[1] == 'entrada'
    
    cur.close()
    conn.close()

def test_registrar_movimiento_salida():
    """Probar el procedimiento de registrar movimiento de salida"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Stock inicial
    cur.execute("SELECT stock FROM productos WHERE id = 2")
    stock_inicial = cur.fetchone()[0]
    
    # Registrar salida
    cur.execute("CALL registrar_movimiento(2, 'salida', 30)")
    conn.commit()
    
    # Verificar stock actualizado
    cur.execute("SELECT stock FROM productos WHERE id = 2")
    stock_final = cur.fetchone()[0]
    assert stock_final == stock_inicial - 30
    
    # Verificar movimiento registrado
    cur.execute("SELECT cantidad, tipo_movimiento FROM movimientos_inventario WHERE producto_id = 2 ORDER BY id DESC LIMIT 1")
    movimiento = cur.fetchone()
    assert movimiento is not None
    assert movimiento[0] == 30
    assert movimiento[1] == 'salida'
    
    cur.close()
    conn.close()

def test_calcular_valor_inventario():
    """Probar la función de calcular valor del inventario"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT calcular_valor_inventario()")
    valor_total = cur.fetchone()[0]
    
    # Verificar que el valor es positivo
    assert valor_total > 0
    
    # Calcular manualmente para verificar
    cur.execute("SELECT SUM(stock * precio_unitario) FROM productos")
    valor_manual = cur.fetchone()[0]
    
    assert valor_total == valor_manual
    
    cur.close()
    conn.close()

def test_trigger_auditoria_stock():
    """Probar que el trigger registra cambios en el stock"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Contar registros de auditoría iniciales
    cur.execute("SELECT COUNT(*) FROM auditoria_stock")
    count_inicial = cur.fetchone()[0]
    
    # Actualizar stock directamente para activar el trigger
    cur.execute("SELECT stock FROM productos WHERE id = 3")
    stock_anterior = cur.fetchone()[0]
    nuevo_stock = stock_anterior + 25
    
    cur.execute("UPDATE productos SET stock = %s WHERE id = 3", (nuevo_stock,))
    conn.commit()
    
    # Verificar que se creó un registro de auditoría
    cur.execute("SELECT COUNT(*) FROM auditoria_stock")
    count_final = cur.fetchone()[0]
    assert count_final == count_inicial + 1
    
    # Verificar datos del registro de auditoría
    cur.execute("SELECT producto_id, stock_anterior, stock_nuevo FROM auditoria_stock ORDER BY id DESC LIMIT 1")
    auditoria = cur.fetchone()
    assert auditoria is not None
    assert auditoria[0] == 3
    assert auditoria[1] == stock_anterior
    assert auditoria[2] == nuevo_stock
    
    cur.close()
    conn.close()

def test_movimiento_stock_negativo():
    """Probar que no se permite stock negativo"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Obtener stock actual
    cur.execute("SELECT stock FROM productos WHERE id = 4")
    stock_actual = cur.fetchone()[0]
    
    # Intentar sacar más de lo disponible
    try:
        cur.execute("CALL registrar_movimiento(4, 'salida', %s)", (stock_actual + 100,))
        conn.commit()
        # Si llega aquí, el test falla porque debería haber generado error
        assert False, "Se permitió stock negativo"
    except Exception as e:
        # Verificar que el stock no cambió
        cur.execute("SELECT stock FROM productos WHERE id = 4")
        stock_despues = cur.fetchone()[0]
        assert stock_despues == stock_actual
        print(f"Error esperado: {e}")
    
    cur.close()
    conn.close()

def test_integracion_completa():
    """Prueba de integración completa del sistema"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Datos iniciales
    cur.execute("SELECT calcular_valor_inventario()")
    valor_inicial = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM movimientos_inventario")
    movimientos_inicial = cur.fetchone()[0]
    
    # Realizar varias operaciones
    operaciones = [
        (1, 'entrada', 100),
        (2, 'salida', 50),
        (3, 'entrada', 75),
        (1, 'salida', 30)
    ]
    
    for producto_id, tipo, cantidad in operaciones:
        cur.execute("CALL registrar_movimiento(%s, %s, %s)", (producto_id, tipo, cantidad))
    
    conn.commit()
    
    # Verificar estado final
    cur.execute("SELECT calcular_valor_inventario()")
    valor_final = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM movimientos_inventario")
    movimientos_final = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM auditoria_stock")
    auditorias_count = cur.fetchone()[0]
    
    # Verificaciones
    assert movimientos_final == movimientos_inicial + len(operaciones)
    assert auditorias_count >= len(operaciones)  # Al menos una auditoría por movimiento que cambió stock
    
    print(f"Valor inicial del inventario: ${valor_inicial:.2f}")
    print(f"Valor final del inventario: ${valor_final:.2f}")
    print(f"Movimientos realizados: {movimientos_final - movimientos_inicial}")
    print(f"Registros de auditoría: {auditorias_count}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
