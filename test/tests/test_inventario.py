import os
import psycopg2
import psycopg2.extras
import pytest

def connect(autocommit=False):
    conn = psycopg2.connect(
        dbname=os.environ.get("PGDATABASE", "test_db"),
        user=os.environ.get("PGUSER", "runner"),
        password=os.environ.get("PGPASSWORD", "runner_password"),
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5432")
    )
    conn.autocommit = autocommit
    return conn

@pytest.fixture
def conn_cur():
    conn = connect()
    psycopg2.extras.register_hstore(conn)
    cur = conn.cursor()
    cur.execute("BEGIN;") 
    try:
        yield conn, cur
    finally:
        cur.execute("ROLLBACK;")
        cur.close()
        conn.close()

def test_jsonb_usuario_ana(conn_cur):
    conn, cur = conn_cur
    cur.execute("SELECT data FROM usuarios WHERE id = 1;")
    record = cur.fetchone()
    
    assert record is not None, "No se encontró el usuario con id=1"
    
    data = record[0] 
    
    assert isinstance(data, dict)
    assert data['nombre'] == 'Ana'
    assert data['activo'] is True
    assert data['edad'] == 30

def test_jsonb_usuario_juan(conn_cur):
    conn, cur = conn_cur
    cur.execute("SELECT data FROM usuarios WHERE id = 2;")
    data = cur.fetchone()[0]
    
    assert isinstance(data, dict)
    assert data['nombre'] == 'Juan'
    assert data['activo'] is False
    assert data['edad'] == 25

def test_hstore_producto_laptop(conn_cur):
    conn, cur = conn_cur
    cur.execute("SELECT atributos FROM productos WHERE id = 1;")
    record = cur.fetchone()
    
    assert record is not None, "No se encontró el producto con id=1"
    
    atributos = record[0] 
    
    assert isinstance(atributos, dict)
    assert atributos['marca'] == 'Dell'
    assert atributos['ram'] == '16GB'
    assert atributos['peso'] == '2.2kg' 
    assert '2.5kg' not in atributos.values(), "El peso no se actualizó"

def test_hstore_producto_teclado(conn_cur):
    conn, cur = conn_cur
    cur.execute("SELECT atributos FROM productos WHERE id = 4;")
    atributos = cur.fetchone()[0]
    
    assert isinstance(atributos, dict)
    assert atributos['tipo'] == 'mecanico'
    assert 'color' not in atributos, "La clave 'color' no fue eliminada"

def test_hstore_agrupacion_avanzada(conn_cur):
    conn, cur = conn_cur
    
    cur.execute("""
        SELECT atributos -> 'marca' AS marca, count(*) AS cantidad
        FROM productos
        WHERE atributos ? 'marca'
        GROUP BY marca
        ORDER BY marca;
    """)
    resultados = cur.fetchall()
    
    conteo_marcas = {marca: count for marca, count in resultados}
    
    assert conteo_marcas['Dell'] == 1
    assert conteo_marcas['Logitech'] == 1
    assert conteo_marcas['Samsung'] == 1
    assert conteo_marcas['Sony'] == 1
