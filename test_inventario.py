import uuid
import decimal
import psycopg2
import pytest

DEC = decimal.Decimal

def connect(autocommit=False):
    conn = psycopg2.connect(
        dbname="test_db",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    conn.autocommit = autocommit
    return conn

def unique_name(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def q2(x):
    return DEC(x).quantize(DEC("0.01"))

@pytest.fixture
def conn_cur():
    conn = connect()
    cur = conn.cursor()
    cur.execute("BEGIN;")
    try:
        yield conn, cur
    finally:
        cur.execute("ROLLBACK;")
        cur.close()
        conn.close()


def test_registrar_movimiento_entrada_auditoria(conn_cur):
    conn, cur = conn_cur
    nombre = unique_name("ProdEntrada")
    cur.execute(
        "INSERT INTO productos (nombre, stock, precio_unitario) VALUES (%s, %s, %s) RETURNING id, stock;",
        (nombre, 100, q2('0.50'))
    )
    pid, st0 = cur.fetchone()
    assert st0 == 100

    cur.execute("CALL registrar_movimiento(%s, %s, %s);", (pid, 'entrada', 25))

    cur.execute("SELECT stock FROM productos WHERE id = %s;", (pid,))
    st1 = cur.fetchone()[0]
    assert st1 == 125

    cur.execute("""SELECT tipo_movimiento, cantidad
                     FROM movimientos_inventario
                    WHERE producto_id = %s
                 ORDER BY id DESC LIMIT 1;""", (pid,))
    mov = cur.fetchone()
    assert mov == ('entrada', 25)

    cur.execute("""SELECT stock_anterior, stock_nuevo
                     FROM auditoria_stock
                    WHERE producto_id = %s
                 ORDER BY id DESC LIMIT 1;""", (pid,))
    aud = cur.fetchone()
    assert aud == (100, 125)


def test_registrar_movimiento_salida_ok(conn_cur):
    conn, cur = conn_cur
    nombre = unique_name("ProdSalidaOK")
    cur.execute(
        "INSERT INTO productos (nombre, stock, precio_unitario) VALUES (%s, %s, %s) RETURNING id;",
        (nombre, 20, q2('10.00'))
    )
    pid = cur.fetchone()[0]

    cur.execute("CALL registrar_movimiento(%s, %s, %s);", (pid, 'salida', 6))
    cur.execute("SELECT stock FROM productos WHERE id = %s;", (pid,))
    assert cur.fetchone()[0] == 14

    # Verifica movimiento y auditoría
    cur.execute("""SELECT tipo_movimiento, cantidad
                     FROM movimientos_inventario
                    WHERE producto_id = %s
                 ORDER BY id DESC LIMIT 1;""", (pid,))
    mov = cur.fetchone()
    assert mov == ('salida', 6)

    cur.execute("""SELECT stock_anterior, stock_nuevo
                     FROM auditoria_stock
                    WHERE producto_id = %s
                 ORDER BY id DESC LIMIT 1;""", (pid,))
    aud = cur.fetchone()
    assert aud == (20, 14)


def test_registrar_movimiento_salida_insuficiente_falla():
    # Para errores es mejor usar autocommit y conexión separada
    conn = connect(autocommit=True)
    cur = conn.cursor()
    try:
        nombre = unique_name("ProdFail")
        cur.execute(
            "INSERT INTO productos (nombre, stock, precio_unitario) VALUES (%s, %s, %s) RETURNING id;",
            (nombre, 4, q2('1.00'))
        )
        pid = cur.fetchone()[0]

        # Intento de salida mayor que stock debe fallar
        with pytest.raises(psycopg2.Error):
            cur.execute("CALL registrar_movimiento(%s, %s, %s);", (pid, 'salida', 5))

        # Stock permanece intacto
        cur.execute("SELECT stock FROM productos WHERE id = %s;", (pid,))
        assert cur.fetchone()[0] == 4
    finally:
        cur.close()
        conn.close()


def test_calcular_valor_inventario(conn_cur):
    conn, cur = conn_cur
    # Limpiar para no depender de datos previos del runner
    cur.execute("DELETE FROM productos;")

    cur.execute("INSERT INTO productos (nombre, stock, precio_unitario) VALUES (%s, %s, %s);",
                (unique_name('A'), 10, q2('2.50')))   # 25.00
    cur.execute("INSERT INTO productos (nombre, stock, precio_unitario) VALUES (%s, %s, %s);",
                (unique_name('B'),  3, q2('100.00')))  # 300.00

    cur.execute("SELECT calcular_valor_inventario();")
    total = cur.fetchone()[0]
    assert q2(total) == q2('325.00')
