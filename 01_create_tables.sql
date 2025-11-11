DROP TABLE IF EXISTS auditoria_stock CASCADE;
DROP TABLE IF EXISTS movimientos_inventario CASCADE;
DROP TABLE IF EXISTS productos CASCADE;

CREATE TABLE productos (
    id              SERIAL PRIMARY KEY,
    nombre          TEXT NOT NULL,
    stock           INT  NOT NULL CHECK (stock >= 0),
    precio_unitario NUMERIC(10,2) NOT NULL CHECK (precio_unitario >= 0)
);

CREATE TABLE movimientos_inventario (
    id              SERIAL PRIMARY KEY,
    producto_id     INT NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
    tipo_movimiento TEXT NOT NULL CHECK (tipo_movimiento IN ('entrada','salida')),
    cantidad        INT NOT NULL CHECK (cantidad > 0),
    fecha           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE auditoria_stock (
    id             SERIAL PRIMARY KEY,
    producto_id    INT REFERENCES productos(id) ON DELETE SET NULL,
    stock_anterior INT,
    stock_nuevo    INT,
    fecha          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
