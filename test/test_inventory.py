import psycopg2
import pytest

@pytest.fixture
def db():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost"
    )
    conn.autocommit = True
    cur = conn.cursor()
    yield cur
    conn.close()

def test_inventario(db):
    # Insert initial data
    db.execute("INSERT INTO productos (nombre, stock, precio_unitario) VALUES ('Tornillo', 100, 0.50);")
    db.execute("INSERT INTO productos (nombre, stock, precio_unitario) VALUES ('Tuerca', 200, 0.30);")

    # Register movement (salida)
    db.execute("CALL registrar_movimiento(1, 'salida', 20);")
    db.execute("SELECT stock FROM productos WHERE id = 1;")
    stock = db.fetchone()[0]

    assert stock == 80, "El stock después de salida debe ser 80"

    # Register movement (entrada)
    db.execute("CALL registrar_movimiento(2, 'entrada', 50);")
    db.execute("SELECT stock FROM productos WHERE id = 2;")
    stock2 = db.fetchone()[0]

    assert stock2 == 250, "El stock después de entrada debe ser 250"

    # Check trigger
    db.execute("SELECT COUNT(*) FROM auditoria_stock;")
    auditorias = db.fetchone()[0]

    assert auditorias >= 2, "Debe haber al menos 2 registros de auditoría"

    # Test inventory value
    db.execute("SELECT calcular_valor_inventario();")
    total = db.fetchone()[0]

    assert total > 0, "El valor del inventario debe ser mayor a 0"
