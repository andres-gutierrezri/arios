-- ------------------------
-- Base de Datos PostgreSQL
-- ------------------------

-- Consultas en la Base de Datos de PostgreSQL

-- Consultar la versión de PostgreSQL
SELECT version() AS "Version PostgreSQL";

-- Mostrar información sobre la conexión actual
\conninfo

-- Consultar la zona horaria
SHOW timezone;

-- Consultar las extensiones instaladas
SELECT * FROM pg_extension;

-- Recuperar información detallada de las bases de datos
SELECT datname AS "Database Name", 
       pg_size_pretty(pg_database_size(datname)) AS "Size", 
       datallowconn AS "Allow Connections", 
       datconnlimit AS "Connection Limit", 
       encoding AS "Encoding", 
       datcollate AS "Datcollate", 
       datctype  AS "Datctype" 
FROM pg_catalog.pg_database;

-- Consultar las bases de datos (\l o \list)
-- SELECT datname AS "Database" FROM pg_database;

-- Mostrar todas las tablas públicas de las bases de datos
-- SELECT * FROM pg_catalog.pg_tables;

-- Mostrar las tablas de la base de datos
-- \connect "DB_Name"
-- \dt

-- Listado de roles y permisos
-- \du

-- Listado de información de espacios de tabla
-- \db
