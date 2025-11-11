import psycopg2
import pytest
from pathlib import Path

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

def run_query_from_file(conn, filename):
    sql_path = Path(filename)
    with open(sql_path, "r") as file:
        query = file.read()
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

def test_function_procedure(db_connection):
    with db_connection.cursor() as cur:
        cur.execute("CALL registrar_movimiento(1, 'salida', 20);")
        cur.execute("SELECT stock FROM productos WHERE id=1;")
        result = cur.fetchone()[0]
        cur.execute("CALL registrar_movimiento(2, 'entrada', 50);")
        cur.execute("SELECT stock FROM productos WHERE id=2;")
        result2 = cur.fetchone()[0]
    assert result == 80
    assert result2 == 250

def test_function(db_connection):
    expected=115.00
    with db_connection.cursor() as cur:
        cur.execute("SELECT calcular_valor_inventario();")
        result = cur.fetchone()[0]
    assert float(result) == pytest.approx(expected)

def test_trigger(db_connection):
    with db_connection.cursor() as cur:
        cur.execute("SELECT * FROM auditoria_stock;")
        result = cur.fetchall()
    assert len(result) == 2
