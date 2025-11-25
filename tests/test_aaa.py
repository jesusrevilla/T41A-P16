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

    # Obtener IDs reales para evitar fallos en GitHub Actions
    global ID_TORNILLO, ID_TUERCA
    ID_TORNILLO = fetch_scalar(db_connection, "SELECT id FROM productos WHERE nombre='Tornillo'")
    ID_TUERCA   = fetch_scalar(db_connection, "SELECT id FROM productos WHERE nombre='Tuerca'")


def test_registrar_movimiento_entrada(db_connection):
    """ Verifica que una entrada aumente el stock """
    execute(db_connection, "CALL registrar_movimiento(%s, %s, %s)", (ID_TORNILLO, 'entrada', 50))

    new_stock = fetch_scalar(db_connection, "SELECT stock FROM productos WHERE id = %s", (ID_TORNILLO,))
    assert new_stock == 150  # 100 + 50

    movs = fetch_scalar(db_connection, "SELECT COUNT(*) FROM movimientos_inventario WHERE producto_id = %s", (ID_TORNILLO,))
    assert movs == 1


def test_registrar_movimiento_salida(db_connection):
    """ Verifica que una salida disminuya el stock """
    execute(db_connection, "CALL registrar_movimiento(%s, %s, %s)", (ID_TORNILLO, 'salida', 30))

    new_stock = fetch_scalar(db_connection, "SELECT stock FROM productos WHERE id = %s", (ID_TORNILLO,))
    assert new_stock == 120  # 150 - 30

    movs = fetch_scalar(db_connection, "SELECT COUNT(*) FROM movimientos_inventario WHERE producto_id = %s", (ID_TORNILLO,))
    assert movs == 2


def test_trigger_auditoria(db_connection):
    """ Verifica que el trigger registre cambios de stock """
    execute(db_connection, "UPDATE productos SET stock = stock + 10 WHERE id = %s", (ID_TORNILLO,))

    rows = fetch_all(db_connection,
        "SELECT producto_id, stock_anterior, stock_nuevo FROM auditoria_stock WHERE producto_id = %s",
        (ID_TORNILLO,)
    )

    assert len(rows) >= 1

    # Último registro insertado
    last = rows[-1]
    producto_id, stock_anterior, stock_nuevo = last

    assert producto_id == ID_TORNILLO
    assert stock_nuevo == stock_anterior + 10


def test_calcular_valor_inventario(db_connection):
    """ Verifica que la función calcule bien el valor total """

    # Stocks reales después de los movimientos
    stock_tornillo = fetch_scalar(db_connection, "SELECT stock FROM productos WHERE id = %s", (ID_TORNILLO,))
    stock_tuerca   = fetch_scalar(db_connection, "SELECT stock FROM productos WHERE id = %s", (ID_TUERCA,))

    precio_tornillo = fetch_scalar(db_connection, "SELECT precio_unitario FROM productos WHERE id = %s", (ID_TORNILLO,))
    precio_tuerca   = fetch_scalar(db_connection, "SELECT precio_unitario FROM productos WHERE id = %s", (ID_TUERCA,))

    total_esperado = stock_tornillo * precio_tornillo + stock_tuerca * precio_tuerca

    total = fetch_scalar(db_connection, "SELECT calcular_valor_inventario()")

    assert total == pytest.approx(total_esperado)
