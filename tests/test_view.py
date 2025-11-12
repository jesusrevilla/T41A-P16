import psycopg2
import pytest

@pytest.fixture(scope="module")
def conexion():
    conn = psycopg2.connect(
        dbname="test_db",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    yield conn
    conn.close()


def test_registrar_movimiento_y_auditoria(conexion):
    cur = conexion.cursor()

    cur.execute("TRUNCATE auditoria_stock, movimientos_inventario, productos RESTART IDENTITY CASCADE;")

    cur.execute("INSERT INTO productos (nombre, stock, precio_unitario) VALUES ('Tornillo', 100, 0.50);")
    cur.execute("INSERT INTO productos (nombre, stock, precio_unitario) VALUES ('Tuerca', 200, 0.30);")
    conexion.commit()

    cur.execute("CALL registrar_movimiento(1, 'salida', 20);")  
    cur.execute("CALL registrar_movimiento(2, 'entrada', 50);")  
    conexion.commit()

    cur.execute("SELECT id, stock FROM productos ORDER BY id;")
    resultados = cur.fetchall()
    assert resultados[0][1] == 80   # Tornillo
    assert resultados[1][1] == 250  # Tuerca

    cur.execute("SELECT COUNT(*) FROM movimientos_inventario;")
    assert cur.fetchone()[0] == 2

    cur.execute("SELECT producto_id, stock_anterior, stock_nuevo FROM auditoria_stock ORDER BY producto_id;")
    auditorias = cur.fetchall()
    assert (1, 100, 80) in auditorias
    assert (2, 200, 250) in auditorias
    cur.close()

def test_calcular_valor_inventario(conexion):
    cur = conexion.cursor()
    cur.execute("SELECT calcular_valor_inventario();")
    valor_total = cur.fetchone()[0]
    assert float(valor_total) == 115.00
    cur.close()

