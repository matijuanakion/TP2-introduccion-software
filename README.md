# TP2 - API de reservas de un club deportivo

## Integrantes

- Santino Nicolás Andreatta - 116024
- nombre y apellido - padron
- nombre y apellido - padron
- nombre y apellido - padron
- nombre y apellido - padron
- nombre y apellido - padron
- nombre y apellido - padron
- nombre y apellido - padron
- nombre y apellido - padron

## Descripción

API REST para gestionar deportes, canchas, socios, reservas y disponibilidad horaria de un club deportivo.

## Tecnologías y versiones

- Python: 3.12 (imagen de Docker `python:3.12-slim`)
- Librerías de Python en `requirements.txt`
- MySQL: 8.4
- Docker y Docker Compose
- Ubuntu

## Requisitos previos

- Utilizar Ubuntu o algún sistema operativo basado en Linux o macOS.
- Docker Engine y Docker Compose instalados.

## Instalación

Desde la raíz del repositorio, Docker construye la imagen de la API e instala
las dependencias dentro del contenedor:

```bash
docker compose up --build -d
```

## Configuración

La aplicación lee variables de entorno desde un archivo `.env` opcional.
Crear ese archivo en la raíz del proyecto si se necesita cambiar los valores
predeterminados:

```dotenv
DB_HOST=db
DB_PORT=3306
DB_NAME=club_deportivo
DB_USER=app_user
DB_PASSWORD=app_password
DB_ROOT_PASSWORD=root_password
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=true
SECRET_KEY=clave-de-desarrollo
```

## Base de datos y API

Levantar MySQL y Flask con Docker Compose:

```bash
docker compose up --build -d
```

El servicio ejecuta automáticamente los scripts de inicialización cuando el volumen está vacío:

- `database/init_db.sql`: crea tablas y carga los deportes iniciales.
- `database/seed.sql`: carga datos ficticios de socios, canchas, reservas y bloqueos.
- `database/initdb.sh`: ejecuta ambos scripts con codificación UTF-8.

Comprobar el estado del servicio:

```bash
docker compose ps
```

La API queda disponible en `http://127.0.0.1:5000` (o en el puerto que se haya asignado desde el `.env`). El servicio `api` espera automáticamente a que MySQL informe un healthcheck saludable.

Para borrar la base y volver a ejecutar el esquema y el seed desde cero:

```bash
docker compose down -v
docker compose up --build -d
```

## Endpoints

### Deportes

- `GET /deportes`

### Canchas

- `GET /canchas`
- `POST /canchas`
- `GET /canchas/{id}`
- `PATCH /canchas/{id}`
- `DELETE /canchas/{id}`
- `GET /canchas/disponibles`

Filtros de `/canchas`: `id_deporte`, `nombre`, `techada`, `activa`.

Filtros de `/canchas/disponibles`: `fecha`, `hora_inicio`, `hora_fin`, `id_deporte` y `techada`.
Los parámetros `fecha`, `hora_inicio` y `hora_fin` son obligatorios.

### Socios

- `GET /socios`
- `POST /socios`
- `GET /socios/{id}`
- `PATCH /socios/{id}`

Filtros de `/socios`: `nombre` y `activo`.

### Reservas

- `GET /reservas`
- `POST /reservas`
- `GET /reservas/{id}`
- `PUT /reservas/{id}/estado`

Filtros de `/reservas`: `id_cancha`, `id_socio`, `estado`, `fecha_desde` y `fecha_hasta`.

### Extensiones opcionales

- `GET /bloqueos`
- `POST /bloqueos`
- `DELETE /bloqueos/{id}`
- `POST /reservas/recurrentes`

Todos los endpoints de listado aceptan `_limit` y `_offset`. Por defecto, `_limit=10` y `_offset=0`; el límite permitido es de 1 a 100.

## Ejemplos

Crear una cancha:

```bash
curl -X POST http://127.0.0.1:5000/canchas \
	-H 'Content-Type: application/json' \
	-d '{
		"nombre": "Cancha de fútbol 5",
		"id_deporte": 1,
		"precio_hora": 1000000,
		"techada": false,
		"activa": true
	}'
```

Consultar canchas disponibles:

```bash
curl 'http://127.0.0.1:5000/canchas/disponibles?fecha=2027-01-10&hora_inicio=18:00:00&hora_fin=20:00:00&_limit=10&_offset=0'
```

Crear una reserva:

```bash
curl -X POST http://127.0.0.1:5000/reservas \
	-H 'Content-Type: application/json' \
	-d '{
		"id_socio": 1,
		"id_cancha": 1,
		"fecha_hora_inicio": "2027-01-10T18:00:00.000000-03:00",
		"fecha_hora_fin": "2027-01-10T20:00:00.000000-03:00"
	}'
```

Actualizar el estado de una reserva:

```bash
curl -X PUT http://127.0.0.1:5000/reservas/1/estado \
	-H 'Content-Type: application/json' \
	-d '{"estado": "cancelada"}'
```

etc.

## Arquitectura

La aplicación está organizada por responsabilidades:

- `src/routes`: recibe requests, valida parámetros básicos y arma respuestas.
- `src/services`: concentra reglas de negocio y casos de uso.
- `src/repositories`: ejecuta consultas y operaciones sobre MySQL.
- `src/validators`: valida cuerpos, filtros y reglas de formato.
- `src/db.py`: administra conexiones y cursores.
- `database`: contiene el esquema, el seed y el script de inicialización.

## Supuestos adoptados

- Los precios se almacenan como enteros en centavos.
- Las reservas usan el formato ISO 8601 con desplazamiento fijo `-03:00`.
- El horario del club es de 08:00 a 23:00 todos los días.
- Las reservas duran entre una y tres horas completas.
- Las reservas nuevas se crean inicialmente como `confirmada`.
- Una cancha o socio inactivo no admite nuevas reservas, pero deja vigentes las reservas existentes.
- Una cancha con reservas asociadas no puede eliminarse.
