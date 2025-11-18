import pytest
import psycopg2

# Configuración de la base de datos de prueba
DB_CONFIG = {
    'host': 'localhost',
    'database': 'test_db',
    'user': 'postgres',
    'password': 'postgres',
    'port': 5432
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def test_procedimiento_registrar_movimiento():
    """Test para verificar el procedimiento registrar_movimiento"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Obtener stock inicial del producto 1
        cur.execute("SELECT stock FROM productos WHERE id = 1")
        stock_inicial = cur.fetchone()[0]
        
        # Registrar una salida de 10 unidades
        cur.execute("CALL registrar_movimiento(1, 'salida', 10)")
        conn.commit()
        
        # Verificar que el stock se actualizó correctamente
        cur.execute("SELECT stock FROM productos WHERE id = 1")
        stock_final = cur.fetchone()[0]
        
        assert stock_final == stock_inicial - 10
        
        # Verificar que se registró el movimiento
        cur.execute("SELECT COUNT(*) FROM movimientos_inventario WHERE producto_id = 1 AND tipo_movimiento = 'salida'")
        count_movimientos = cur.fetchone()[0]
        assert count_movimientos > 0
        
        print(" Test procedimiento registrar_movimiento: PASÓ")
        
    except Exception as e:
        print(f" Test procedimiento registrar_movimiento: FALLÓ - {e}")
        raise e
    finally:
        cur.close()
        conn.close()

def test_funcion_calcular_valor_inventario():
    """Test para verificar la función calcular_valor_inventario"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Ejecutar la función
        cur.execute("SELECT calcular_valor_inventario()")
        valor_inventario = cur.fetchone()[0]
        
        # Verificar que devuelve un valor numérico positivo
        assert valor_inventario is not None
        assert valor_inventario >= 0
        
        print(" Test función calcular_valor_inventario: PASÓ")
        
    except Exception as e:
        print(f" Test función calcular_valor_inventario: FALLÓ - {e}")
        raise e
    finally:
        cur.close()
        conn.close()

def test_trigger_auditoria_stock():
    """Test para verificar el trigger de auditoría de stock"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Obtener stock actual del producto 2
        cur.execute("SELECT stock FROM productos WHERE id = 2")
        stock_actual = cur.fetchone()[0]
        
        # Contar registros de auditoría antes de la actualización
        cur.execute("SELECT COUNT(*) FROM auditoria_stock WHERE producto_id = 2")
        count_auditoria_antes = cur.fetchone()[0]
        
        # Actualizar el stock para activar el trigger
        nuevo_stock = stock_actual + 5
        cur.execute("UPDATE productos SET stock = %s WHERE id = 2", (nuevo_stock,))
        conn.commit()
        
        # Contar registros de auditoría después de la actualización
        cur.execute("SELECT COUNT(*) FROM auditoria_stock WHERE producto_id = 2")
        count_auditoria_despues = cur.fetchone()[0]
        
        # Verificar que se creó un nuevo registro de auditoría
        assert count_auditoria_despues == count_auditoria_antes + 1
        
        # Verificar los datos del último registro de auditoría
        cur.execute("""
            SELECT stock_anterior, stock_nuevo 
            FROM auditoria_stock 
            WHERE producto_id = 2 
            ORDER BY id DESC 
            LIMIT 1
        """)
        auditoria = cur.fetchone()
        assert auditoria[0] == stock_actual
        assert auditoria[1] == nuevo_stock
        
        print(" Test trigger auditoría stock: PASÓ")
        
    except Exception as e:
        print(f" Test trigger auditoría stock: FALLÓ - {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    test_procedimiento_registrar_movimiento()
    test_funcion_calcular_valor_inventario()
    test_trigger_auditoria_stock()
    print("¡Todos los tests pasaron correctamente!")
