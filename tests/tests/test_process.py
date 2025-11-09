import psycopg2

def test_process():
  conn = psycopg2.connect(
      dbname='test_db',
      user='postgres',
      password='postgres',
      host='localhost',
      port='5432'
  )
  conn.autocommit = False
  try:
      cur = conn.cursor()
      query= "INSERT INTO productos (nombre, stock, precio_unitario) VALUES (%s,%s,%s);"
      cur.execute(query,('Tornillo', 100, 0.50))
      cur.execute(query,('Tuerca', 200, 0.30))
      conn.commit()
      query= "SELECT * FROM productos;"
      cur.execute(query)
      resultados=cur.fetchall();
      assert len(resultados)==2
      query= "CALL registrar_movimiento(%s,%s,%s);"
      cur.execute(query,(1, 'salida', 20))
      conn.commit()
      cur.execute("SELECT stock FROM productos WHERE id=1")
      resultado=cur.fetchone()[0]
      assert resultado == 80
      cur.execute(query,(2, 'entrada', 50))
      conn.commit()
      cur.execute("SELECT stock FROM productos WHERE id=2")
      resultado=cur.fetchone()[0]
      assert resultado == 250
      cur.execute("SELECT calcular_valor_inventario();")
      resultado=cur.fetchone()[0]
      assert resultado==115.0
      cur.execute("SELECT * FROM auditoria_stock;")
      resultados=cur.fetchall();
      assert len(resultados)==2
  except Exception as e:
      raise e
  finally:
      #En caso de cualquier fallo en el try, el finally hará la limpieza.
      conn.rollback()
      cur.close()
      conn.close()
