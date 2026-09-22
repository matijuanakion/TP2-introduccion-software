-- Socios de ejemplo
INSERT INTO socios (nombre, email, activo)
SELECT 'Ana García', 'ana.garcia@example.com', 1
WHERE NOT EXISTS (SELECT 1 FROM socios WHERE email = 'ana.garcia@example.com');

INSERT INTO socios (nombre, email, activo)
SELECT 'Luis Pérez', 'luis.perez@example.com', 1
WHERE NOT EXISTS (SELECT 1 FROM socios WHERE email = 'luis.perez@example.com');

INSERT INTO socios (nombre, email, activo)
SELECT 'María Rodríguez', 'maria.rodriguez@example.com', 1
WHERE NOT EXISTS (SELECT 1 FROM socios WHERE email = 'maria.rodriguez@example.com');

-- Canchas extra
INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
SELECT 'Cancha de Futbol dop', 1, 55000, 0, 1
WHERE NOT EXISTS (SELECT 1 FROM canchas WHERE nombre = 'Cancha de Futbol dop');

INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
SELECT 'Cancha de Tenis Dop', 2, 55000, 0, 1
WHERE NOT EXISTS (SELECT 1 FROM canchas WHERE nombre = 'Cancha de Tenis Dop');

INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
SELECT 'Cancha de Pádel Cubierta', 3, 90000, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM canchas WHERE nombre = 'Cancha de Pádel Cubierta');

-- Bloqueos por mantenimiento
INSERT INTO bloqueos (id_cancha, fecha, hora_inicio, hora_fin, motivo)
SELECT c.id, '2026-10-01', '09:00:00', '12:00:00', 'Mantenimiento de césped'
FROM canchas c
WHERE c.nombre = 'Cancha Central'
  AND NOT EXISTS (SELECT 1 FROM bloqueos WHERE fecha = '2026-10-01' AND hora_inicio = '09:00:00');

-- Reservas de ejemplo
INSERT INTO reservas (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total)
SELECT s.id, c.id, '2026-09-25 10:00:00', '2026-09-25 11:00:00', 'confirmada', c.precio_hora, c.precio_hora
FROM socios s JOIN canchas c ON c.nombre = 'Cancha Central'
WHERE s.email = 'ana.garcia@example.com'
  AND NOT EXISTS (SELECT 1 FROM reservas WHERE fecha_hora_inicio = '2026-09-25 10:00:00');

INSERT INTO reservas (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total)
SELECT s.id, c.id, '2026-09-25 18:00:00', '2026-09-25 19:00:00', 'confirmada', c.precio_hora, c.precio_hora
FROM socios s JOIN canchas c ON c.nombre = 'Cancha Auxiliar'
WHERE s.email = 'luis.perez@example.com'
  AND NOT EXISTS (SELECT 1 FROM reservas WHERE fecha_hora_inicio = '2026-09-25 18:00:00');

INSERT INTO reservas (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total)
SELECT s.id, c.id, '2026-09-26 10:00:00', '2026-09-26 11:30:00', 'confirmada', c.precio_hora, c.precio_hora * 1.5
FROM socios s JOIN canchas c ON c.nombre = 'Cancha de Pádel Cubierta'
WHERE s.email = 'maria.rodriguez@example.com'
  AND NOT EXISTS (SELECT 1 FROM reservas WHERE fecha_hora_inicio = '2026-09-26 10:00:00');