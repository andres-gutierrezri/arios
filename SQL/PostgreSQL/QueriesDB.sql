-- ------------------------
-- Base de Datos PostgreSQL
-- ------------------------

-- Consultas en la Base de Datos de PostgreSQL

-- Consultar la versión de PostgreSQL
SELECT version();

-- Consultar las bases de datos
\l -- \list
SELECT datname FROM pg_database;

-- Recuperación de información detallada de la base de datos
SELECT datname AS database_name, 
       pg_size_pretty(pg_database_size(datname)) AS size,
       datallowconn AS allow_connections,
       datconnlimit AS connection_limit,
       encoding, 
       datcollate, 
       datctype 
FROM pg_catalog.pg_database;

-- Listado de roles y permisos
\du

-- Listado de información de espacios de tabla
\db

-- Consultar las extensiones instaladas
SELECT * FROM pg_extension;

-- Consultar la zona horaria
SHOW timezone;
