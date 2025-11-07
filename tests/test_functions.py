import psycopg2
import pytest

DB_CONFIG = {
    "dbname": "test_db",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432
}

@pytest.fixture(scope="module")
def db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    yield conn
    conn.close()

def fetch_scalar(conn, query, params=()):
    with conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchone()[0]

def fetch_all(conn, query, params=()):
    with conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()

def execute_query(connection, query, params=None):
    """Ejecuta un comando que no devuelve filas (CALL, INSERT, UPDATE)."""
    with connection.cursor() as cursor:
        cursor.execute(query, params or ())
    # ¡Commit es crucial para que los cambios sean visibles en otros tests!
    connection.commit()

def test_call_register_movements(db_connection):
    execute_query(db_connection, "CALL registrar_movimiento(%s,%s,%s)", (1,'salida',20))
    execute_query(db_connection, "CALL registrar_movimiento(%s,%s,%s)", (2,'entrada',50))
    assert True

def test_calcular_valor_inventario(db_connection):
    query = "SELECT calcular_valor_inventario();"
    result = fetch_all(db_connection, query)
    productos = {row[0] for row in result}
    assert productos == {115.00}

def test_auditoria_stock(db_connection):
    query = "SELECT id,producto_id,stock_anterior,stock_nuevo FROM auditoria_stock;"
    resultados = fetch_all(db_connection, query)
    resultados_esperados = [
          (1,1, 100, 80),  # Fila 1: (producto_id 1, de 100 -> 80)
          (2,2, 200, 250)  # Fila 2: (producto_id 2, de 200 -> 250)
      ]
    assert resultados == resultados_esperados
