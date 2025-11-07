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

def test_call_register_movements(db_connection):
    fetch_scalar(db_connection, "CALL registrar_movimiento(%s,%s,%s)", (1,'salida'),(20,))
    fetch_scalar(db_connection, "CALL registrar_movimiento(%s,%s,%s)", (2,'entrada'),(50,))
    assert True

def test_validar_correo(db_connection):
    assert fetch_scalar(db_connection, "SELECT validar_correo('test@example.com')") == True
    assert fetch_scalar(db_connection, "SELECT validar_correo('invalido')") == False

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
