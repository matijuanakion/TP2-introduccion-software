#!/bin/sh
# Ejecuta los .sql con --default-character-set=utf8mb4 para no romper los acentos.
# El entrypoint de MySQL corre este script en la primer inicialización del volumen.

set -e

mysql --protocol=socket -uroot -hlocalhost \
    --password="${MYSQL_ROOT_PASSWORD}" \
    --default-character-set=utf8mb4 \
    --database="${MYSQL_DATABASE}" \
    < /sql/01-init_db.sql

mysql --protocol=socket -uroot -hlocalhost \
    --password="${MYSQL_ROOT_PASSWORD}" \
    --default-character-set=utf8mb4 \
    --database="${MYSQL_DATABASE}" \
    < /sql/02-seed.sql