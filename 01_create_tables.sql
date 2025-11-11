-- Tabla principal de productos
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    stock INT NOT NULL,
    precio_unitario NUMERIC(10,2) NOT NULL
);

-- Tabla para registrar los movimientos de inventario
CREATE TABLE movimientos_inventario (
    id SERIAL PRIMARY KEY,
    producto_id INT REFERENCES productos(id),
    tipo_movimiento TEXT CHECK (tipo_movimiento IN ('entrada', 'salida')),
    cantidad INT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de auditoría para registrar cambios en el stock
CREATE TABLE auditoria_stock (
    id SERIAL PRIMARY KEY,
    producto_id INT,
    stock_anterior INT,
    stock_nuevo INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);