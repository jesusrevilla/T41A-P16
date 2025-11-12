import psycopg2
import pytest

DB_CONFIG = {
    "dbname": "test_db",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}

@pytest.fixture(scope="module")
def db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    yield conn
    conn.close()

def fetch_scalar(conn, query, params=()):
    with conn.cursor() as cur:
        cur.execute(query, params)
        row = cur.fetchone()
        return row[0] if row else None

def fetch_all(conn, query, params=()):
    with conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()

def execute_query(conn, query, params=None):
    with conn.cursor() as cur:
        cur.execute(query, params or ())
    conn.commit()

def test_call_register_movements(db_connection):
    execute_query(db_connection, "CALL registrar_movimiento(%s,%s,%s)", (1, 'salida', 20))
    execute_query(db_connection, "CALL registrar_movimiento(%s,%s,%s)", (2, 'entrada', 50))

    stock_p1 = fetch_scalar(db_connection, "SELECT stock FROM productos WHERE id = %s", (1,))
    stock_p2 = fetch_scalar(db_connection, "SELECT stock FROM productos WHERE id = %s", (2,))
    assert stock_p1 == 80
    assert stock_p2 == 250

def test_calcular_valor_inventario(db_connection):
    result = fetch_scalar(db_connection, "SELECT calcular_valor_inventario();")
    assert float(result) == 115.00

def test_auditoria_stock(db_connection):
    resultados = fetch_all(
        db_connection,
        "SELECT id, producto_id, stock_anterior, stock_nuevo FROM auditoria_stock ORDER BY id ASC;"
    )
    resultados_esperados = [
        (1, 1, 100, 80),
        (2, 2, 200, 250),
    ]
    assert resultados == resultados_esperados
