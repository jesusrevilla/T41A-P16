import psycopg2
import pytest

# Configuración de conexión a la base de datos
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


def test_calcular_descuento(conexion):
    cur = conexion.cursor()
    cur.execute("SELECT calcular_descuento(100, 0.2);")
    resultado = cur.fetchone()[0]
    assert resultado == 80
    cur.close()


def test_contiene_correo(conexion):
    cur = conexion.cursor()
    cur.execute("SELECT contiene_correo('usuario@gmail.com');")
    assert cur.fetchone()[0] is True

    cur.execute("SELECT contiene_correo('usuariogmail.com');")
    assert cur.fetchone()[0] is False
    cur.close()


def test_dia_semanal(conexion):
    cur = conexion.cursor()
    # 2024-05-06 fue lunes
    cur.execute("SELECT dia_semanal('2024-05-06');")
    resultado = cur.fetchone()[0]
    assert resultado == 'Lunes'
    cur.close()


def test_num_empleados(conexion):
    cur = conexion.cursor()
    cur.execute("SELECT num_empleados(2);")  #Hay 3 empleados con departamento 2
    resultado = cur.fetchone()[0]
    assert resultado == 3
    cur.close()


def test_stock_minimo(conexion):
    cur = conexion.cursor()
    cur.execute("SELECT * FROM stock_minimo(10);")
    resultados = cur.fetchall()
    # Deben estar los productos con stock menor a 10 (Impresora HP, Silla Ergonómica)
    nombres = [r[1] for r in resultados]
    assert 'Impresora HP' in nombres
    assert 'Silla Ergonómica' in nombres
    assert all(isinstance(r[0], int) for r in resultados) 
    cur.close()
