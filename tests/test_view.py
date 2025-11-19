import psycopg2
import pytest
from psycopg2.extras import RealDictCursor
from decimal import Decimal

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

def ejecutar_query(conn, query, params=None, fetch=False):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, params)
        if fetch:
            return cur.fetchall()
        conn.commit()

def test_inventario(db_connection):
    conn = db_connection 

    # Limpiar tablas
    ejecutar_query(conn, "DELETE FROM auditoria_stock;")
    ejecutar_query(conn, "DELETE FROM movimientos_inventario;")
    ejecutar_query(conn, "DELETE FROM productos;")

    # Insertar productos
    tornillo_id = ejecutar_query(
        conn,
        "INSERT INTO productos (nombre, stock, precio_unitario) VALUES ('Tornillo', 100, 0.50) RETURNING id;",
        fetch=True
    )[0]['id']

    tuerca_id = ejecutar_query(
        conn,
        "INSERT INTO productos (nombre, stock, precio_unitario) VALUES ('Tuerca', 200, 0.30) RETURNING id;",
        fetch=True
    )[0]['id']

    # Movimientos
    ejecutar_query(conn, f"CALL registrar_movimiento({tornillo_id}, 'salida', 20);")
    ejecutar_query(conn, f"CALL registrar_movimiento({tuerca_id}, 'entrada', 50);")

    # Valor inventario
    valor = ejecutar_query(
        conn,
        "SELECT calcular_valor_inventario() AS total;",
        fetch=True
    )[0]['total']

    print(f"Valor total del inventario: {valor}")

    # Auditoría
    auditoria = ejecutar_query(
        conn,
        "SELECT * FROM auditoria_stock ORDER BY id;",
        fetch=True
    )

    print(f"Registros de auditoría: {len(auditoria)} encontrados")

    assert len(auditoria) == 2, "Debe haber dos registros de auditoría"
    assert float(valor) == 115.00, " El valor total del inventario debe ser 115.00"
