CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    stock INT NOT NULL,
    precio_unitario NUMERIC(10,2) NOT NULL
);

CREATE TABLE movimientos_inventario (
    id SERIAL PRIMARY KEY,
    producto_id INT REFERENCES productos(id),
    tipo_movimiento TEXT CHECK (tipo_movimiento IN ('entrada', 'salida')),
    cantidad INT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE auditoria_stock (
    id SERIAL PRIMARY KEY,
    producto_id INT,
    stock_anterior INT,
    stock_nuevo INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
