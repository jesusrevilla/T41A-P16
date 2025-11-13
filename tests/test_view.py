import psycopg2
import pytest
from pathlib import Path
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

def ejecutar_query(query, params=None, fetch=False):
    """Ejecuta una consulta SQL con control de commit y retorno opcional."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, params)
        if fetch:
            return cur.fetchall()
        conn.commit()

def test_inventario():
    ejecutar_query("DELETE FROM auditoria_stock;")
    ejecutar_query("DELETE FROM movimientos_inventario;")
    ejecutar_query("DELETE FROM productos;")

    ejecutar_query("INSERT INTO productos (nombre, stock, precio_unitario) VALUES ('Tornillo', 100, 0.50);")
    ejecutar_query("INSERT INTO productos (nombre, stock, precio_unitario) VALUES ('Tuerca', 200, 0.30);")

    ejecutar_query("CALL registrar_movimiento(1, 'salida', 20);")
    ejecutar_query("CALL registrar_movimiento(2, 'entrada', 50);")

    valor = ejecutar_query("SELECT calcular_valor_inventario() AS total;", fetch=True)[0]['total']
    print(f"Valor total del inventario: {valor}")

    auditoria = ejecutar_query("SELECT * FROM auditoria_stock ORDER BY id;", fetch=True)
    print(f"Registros de auditoría: {len(auditoria)} encontrados\n")
    for registro in auditoria:
        print(f" - Producto {registro['producto_id']}: {registro['stock_anterior']} → {registro['stock_nuevo']}")

    assert len(auditoria) == 2, " Debe haber dos registros de auditoría"
    assert valor == 115.00, " El valor total del inventario debe ser 115.00"

    print("\n Todas las pruebas pasaron correctamente.")

if __name__ == "__main__":
    try:
        test_inventario()
    finally:
        conn.close()
