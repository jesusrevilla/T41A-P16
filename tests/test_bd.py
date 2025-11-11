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

def test_function_discount(db_connection):
    prod_org = 100.00
    descuento = 10.00
    expected = prod_org - (prod_org * (descuento / 100.00))
    with db_connection.cursor() as cur:
        cur.execute("SELECT desc_producto(%s, %s);", (prod_org, descuento))
        result = cur.fetchone()[0]
    assert float(result) == pytest.approx(expected)

def test_function_email(db_connection):
    with db_connection.cursor() as cur:
        cur.execute("SELECT valida_correo('corjagamil.com');")
        result = cur.fetchone()[0]
    assert result is False

def test_function_stock(db_connection):
    expected = [
        ('Camara', 5),
        ('Computadora', 8),
        ('Telefono', 15)
        ]
    with db_connection.cursor() as cur:
        cur.execute("SELECT * FROM stock_prod(20);")
        result = cur.fetchall()
    assert set(result) == set(expected)
