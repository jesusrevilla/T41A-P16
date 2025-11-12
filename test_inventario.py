import psycopg2

def test_valor_inventario():
    conn = psycopg2.connect(
        dbname="test_db",
        user="postgres",
        password="postgres",
        host="localhost"
    )
    cur = conn.cursor()

    # Ejecutar movimientos
    cur.execute("CALL registrar_movimiento(1, 'salida', 20);")
    cur.execute("CALL registrar_movimiento(2, 'entrada', 50);")

    # Calcular valor
    cur.execute("SELECT calcular_valor_inventario();")
    valor = cur.fetchone()[0]

    # Verificar resultado esperado
    assert valor == 85.0  # Ajusta según tus datos de prueba

    cur.close()
    conn.close()
