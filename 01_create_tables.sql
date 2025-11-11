-- 1. Tabla principal de productos
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    stock INT NOT NULL,
    precio_unitario NUMERIC(10, 2) NOT NULL
);

-- 2. Tabla para registrar cada movimiento
CREATE TABLE movimientos_inventario (
    id SERIAL PRIMARY KEY,
    producto_id INT REFERENCES productos(id),
    tipo_movimiento TEXT CHECK (tipo_movimiento IN ('entrada', 'salida')),
    cantidad INT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabla para el trigger de auditoría
CREATE TABLE auditoria_stock (
    id SERIAL PRIMARY KEY,
    producto_id INT,
    stock_anterior INT,
    stock_nuevo INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
