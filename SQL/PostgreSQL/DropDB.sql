-- ------------------------
-- Base de Datos PostgreSQL
-- ------------------------

-- ELIMINAR LA BASE DE DATOS (EVA)
\! cls
\connect "postgres"
SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'EVA' AND pid <> pg_backend_pid();

DROP DATABASE IF EXISTS "EVA" WITH (FORCE);