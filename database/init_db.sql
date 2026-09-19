-- ---------------------------------------------------------------------------
-- Deportes precargados (solo lectura via API)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS deportes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
) DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO deportes (nombre) VALUES ('fútbol'), ('tenis'), ('pádel');

-- ---------------------------------------------------------------------------
-- Canchas
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS canchas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_deporte INT NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    precio_hora INT NOT NULL,
    techada TINYINT(1) NOT NULL DEFAULT 0,
    activa TINYINT(1) NOT NULL DEFAULT 1,
    CONSTRAINT fk_canchas_deporte FOREIGN KEY (id_deporte) REFERENCES deportes (id)
) DEFAULT CHARSET=utf8mb4;

-- canchas de prueba (solo si la tabla está vacía) --
INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
SELECT 'Cancha Central', 1, 1000000, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM canchas);
INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
SELECT 'Cancha Auxiliar', 1, 800000, 0, 1
WHERE NOT EXISTS (SELECT 1 FROM canchas);

-- ---------------------------------------------------------------------------
-- Socios
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS socios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    activo TINYINT(1) NOT NULL DEFAULT 1
) DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------------
-- Reservas
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_socio INT NOT NULL,
    id_cancha INT NOT NULL,
    fecha_hora_inicio VARCHAR(35) NOT NULL,
    fecha_hora_fin VARCHAR(35) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'confirmada',
    precio_hora INT NOT NULL,
    precio_total INT NOT NULL,
    CONSTRAINT fk_reservas_socio FOREIGN KEY (id_socio) REFERENCES socios (id),
    CONSTRAINT fk_reservas_cancha FOREIGN KEY (id_cancha) REFERENCES canchas (id)
) DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------------
-- Bloqueos por mantenimiento (extension opcional)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bloqueos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_cancha INT NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    motivo VARCHAR(255) NOT NULL,
    CONSTRAINT fk_bloqueos_cancha FOREIGN KEY (id_cancha) REFERENCES canchas (id)
) DEFAULT CHARSET=utf8mb4;