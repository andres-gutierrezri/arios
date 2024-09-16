-- ------------------------
-- Base de Datos PostgreSQL
-- ------------------------

-- CREAR LA BASE DE DATOS (EVA)

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

CREATE DATABASE "EVA"
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
 -- Deploy (EVA)
 -- LOCALE_PROVIDER = icu
 -- ICU_LOCALE = 'es-CO'
 -- Local (PostgreSQL)
 -- LC_COLLATE = 'Spanish_Colombia.1252'
 -- LC_CTYPE = 'Spanish_Colombia.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    TEMPLATE = template0;

-- SELECCIONAR LA BASE DE DATOS
\connect "EVA"
SHOW TIMEZONE;
