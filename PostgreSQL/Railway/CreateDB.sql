-- ------------------------
-- Base de Datos PostgreSQL
-- ------------------------

-- CREAR LA BASE DE DATOS (railway)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

CREATE DATABASE "railway"
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LOCALE_PROVIDER = icu
    ICU_LOCALE = 'es-CO'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    TEMPLATE = template0;

-- SELECCIONAR LA BASE DE DATOS
\connect "railway"
SHOW TIMEZONE;
