import psycopg2
import pytest
from decimal import Decimal

def test_inventory_logic_flow():
    conn = None
    try:
        conn = psycopg2.connect(
            dbname='test_db',
            user='postgres',
            password='postgres',
            host='localhost',
            port='5432'
        )
        cur = conn.cursor()

        cur.execute("SELECT stock FROM productos WHERE id = 1;")
        stock_tornillo = cur.fetchone()[0]
        assert stock_tornillo == 80, f"Stock de Tornillo incorrecto. Esperado: 80, Obtenido: {stock_tornillo}"

        cur.execute("SELECT stock FROM productos WHERE id = 2;")
        stock_tuerca = cur.fetchone()[0]
        assert stock_tuerca == 250, f"Stock de Tuerca incorrecto. Esperado: 250, Obtenido: {stock_tuerca}"

        cur.execute("SELECT COUNT(*) FROM movimientos_inventario;")
        conteo_movimientos = cur.fetchone()[0]
        assert conteo_movimientos == 2, "La tabla 'movimientos_inventario' no registró los 2 movimientos."

        cur.execute("SELECT calcular_valor_inventario();")
        valor_total = cur.fetchone()[0]
        
        valor_esperado = Decimal('115.00')
        assert valor_total == valor_esperado, \
            f"El valor total del inventario es incorrecto. Esperado: {valor_esperado}, Obtenido: {valor_total}"

        cur.execute("SELECT COUNT(*) FROM auditoria_stock;")
        conteo_auditoria = cur.fetchone()[0]
        assert conteo_auditoria == 2, "La tabla 'auditoria_stock' no registró los 2 cambios (¡FALTA EL TRIGGER!)."
      
        cur.execute("SELECT stock_anterior, stock_nuevo FROM auditoria_stock WHERE producto_id = 1;")
        auditoria_tornillo = cur.fetchone()
        assert auditoria_tornillo == (100, 80), \
            f"Registro de auditoría incorrecto para Tornillo. Esperado: (100, 80), Obtenido: {auditoria_tornillo}"

    finally:
        if conn:
            conn.rollback() 
            cur.close()
            conn.close()
