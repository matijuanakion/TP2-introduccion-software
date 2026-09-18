-- ---------------------------------------------------------------------------
-- Deportes precargados (solo lectura via API)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS deportes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
);

INSERT INTO deportes (nombre) VALUES ('fútbol'), ('tenis'), ('pádel');

-- ---------------------------------------------------------------------------
-- Canchas
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS canchas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_deporte INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    precio_hora INTEGER NOT NULL,
    techada BOOLEAN NOT NULL DEFAULT 0,
    activa BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (id_deporte) REFERENCES deportes (id)
);

-- canchas de prueba --
INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa) VALUES ('Cancha Central', 1, 1000000, 1, 1);
INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa) VALUES ('Cancha Auxiliar', 1, 800000, 0, 1);

-- ---------------------------------------------------------------------------
-- Socios
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS socios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    activo BOOLEAN NOT NULL DEFAULT 1
);

-- ---------------------------------------------------------------------------
-- Reservas
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reservas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_socio INTEGER NOT NULL,
    id_cancha INTEGER NOT NULL,
    fecha_hora_inicio TEXT NOT NULL,
    fecha_hora_fin TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'confirmada',
    precio_hora INTEGER NOT NULL,
    precio_total INTEGER NOT NULL,
    FOREIGN KEY (id_socio) REFERENCES socios (id),
    FOREIGN KEY (id_cancha) REFERENCES canchas (id)
);

-- En SQLite, los índices se crean por fuera de la tabla
CREATE INDEX idx_reservas_cancha_horario ON reservas (id_cancha, fecha_hora_inicio, fecha_hora_fin);
CREATE INDEX idx_reservas_socio_horario ON reservas (id_socio, fecha_hora_inicio, fecha_hora_fin);
CREATE INDEX idx_reservas_estado ON reservas (estado);

-- ---------------------------------------------------------------------------
-- Bloqueos por mantenimiento (extension opcional)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bloqueos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cancha INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    hora_inicio TEXT NOT NULL,
    hora_fin TEXT NOT NULL,
    motivo TEXT NOT NULL,
    FOREIGN KEY (id_cancha) REFERENCES canchas (id)
);

CREATE INDEX idx_bloqueos_cancha_fecha ON bloqueos (id_cancha, fecha);