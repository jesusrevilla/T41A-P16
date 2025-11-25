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

def execute(conn, query, params=()):
    with conn.cursor() as cur:
        cur.execute(query, params)
    conn.commit()


# ============================================================
# TESTS
# ============================================================

def test_setup_initial_data(db_connection):
    """ Limpia tablas e inserta datos base """
    execute(db_connection, "DELETE FROM auditoria_stock")
    execute(db_connection, "DELETE FROM movimientos_inventario")
    execute(db_connection, "DELETE FROM productos")

    execute(db_connection,
        "INSERT INTO productos (nombre, stock, precio_unitario) VALUES "
        "('Tornillo', 100, 0.50),"
        "('Tuerca', 200, 0.30)"
    )

    count = fetch_scalar(db_connection, "SELECT COUNT(*) FROM productos")
    assert count == 2


def test_registrar_movimiento_entrada(db_connection):
    """ Verifica que una entrada aumente el stock """
    execute(db_connection, "CALL registrar_movimiento(%s, %s, %s)", (1, 'entrada', 50))

    new_stock = fetch_scalar(db_connection, "SELECT stock FROM productos WHERE id = 1")
    assert new_stock == 150  # 100 + 50

    movs = fetch_scalar(db_connection, "SELECT COUNT(*) FROM movimientos_inventario WHERE producto_id = 1")
    assert movs == 1


def test_registrar_movimiento_salida(db_connection):
    """ Verifica que una salida disminuya el stock """
    execute(db_connection, "CALL registrar_movimiento(%s, %s, %s)", (1, 'salida', 30))

    new_stock = fetch_scalar(db_connection, "SELECT stock FROM productos WHERE id = 1")
    assert new_stock == 120  # 150 - 30

    movs = fetch_scalar(db_connection, "SELECT COUNT(*) FROM movimientos_inventario WHERE producto_id = 1")
    assert movs == 2


def test_trigger_auditoria(db_connection):
    """ Verifica que el trigger registre cambios de stock """
    # Cambiar stock manualmente para activar trigger
    execute(db_connection, "UPDATE productos SET stock = stock + 10 WHERE id = 1")

    rows = fetch_all(db_connection,
        "SELECT producto_id, stock_anterior, stock_nuevo FROM auditoria_stock WHERE producto_id = 1"
    )

    assert len(rows) >= 1

    # Se toma el último registro insertado por el trigger
    last = rows[-1]
    producto_id, stock_anterior, stock_nuevo = last

    assert producto_id == 1
    assert stock_nuevo == stock_anterior + 10


def test_calcular_valor_inventario(db_connection):
    """ Verifica que la función calcule bien el valor total """
    total = fetch_scalar(db_connection, "SELECT calcular_valor_inventario()")

    # Tornillo: stock ~120, precio 0.50  → 60
    # Tuerca:  stock 200, precio 0.30 → 60
    assert total == pytest.approx(120.00)
