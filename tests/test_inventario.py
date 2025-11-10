import psycopg2
import pytest
from decimal import Decimal

DB_CONFIG = {
    "dbname": "test_db",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432
}

@pytest.fixture
def db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    yield conn
    conn.rollback()
    conn.close()

def test_registrar_movimiento_salida(db_connection):
    conn = db_connection
    with conn.cursor() as cur:
        cur.execute("CALL registrar_movimiento(1, 'salida', 20);")
        
        cur.execute("SELECT stock FROM productos WHERE id = 1;")
        stock_final = cur.fetchone()[0]
        assert stock_final == 80
        
        cur.execute("SELECT * FROM movimientos_inventario;")
        assert len(cur.fetchall()) == 1

def test_trigger_auditoria_con_salida(db_connection):
    conn = db_connection
    with conn.cursor() as cur:
        cur.execute("CALL registrar_movimiento(1, 'salida', 20);")
        
        cur.execute("SELECT producto_id, stock_anterior, stock_nuevo FROM auditoria_stock;")
        auditoria = cur.fetchall()
        assert len(auditoria) == 1
        assert auditoria[0] == (1, 100, 80)

def test_stock_insuficiente(db_connection):
    conn = db_connection
    with conn.cursor() as cur:
        with pytest.raises(psycopg2.errors.RaiseException, match="Stock insuficiente"):
            cur.execute("CALL registrar_movimiento(1, 'salida', 999);")

def test_simulacion_completa_y_valor_inventario(db_connection):
    conn = db_connection
    with conn.cursor() as cur:
        cur.execute("SELECT calcular_valor_inventario();")
        valor_inicial = cur.fetchone()[0]
        assert valor_inicial == Decimal('110.00')

        cur.execute("CALL registrar_movimiento(1, 'salida', 20);")
        cur.execute("CALL registrar_movimiento(2, 'entrada', 50);")
        cur.execute("SELECT calcular_valor_inventario();")
        valor_final = cur.fetchone()[0]
        assert valor_final == Decimal('115.00')

        cur.execute("SELECT producto_id, stock_anterior, stock_nuevo FROM auditoria_stock ORDER BY id;")
        auditoria = cur.fetchall()
        assert len(auditoria) == 2
        assert auditoria[0] == (1, 100, 80)
        assert auditoria[1] == (2, 200, 250)
