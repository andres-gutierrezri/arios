-- BORRAR TABLAS
-- SELECCIONAR BASE DE DATOS
USE railway;
SET NAMES utf8mb4;

-- VER VARIABLE GLOBAL
SHOW VARIABLES LIKE "SQL_SAFE_UPDATES";
-- DESHABILITAR ACTUALIZACION SEGURA
SET SQL_SAFE_UPDATES = 0;

-- TABLE DELETE
DELETE FROM TalentoHumano_colaborador;
DELETE FROM Administracion_cargo;
DELETE FROM SGI_gruposdocumentosprocesos;
DELETE FROM Administracion_proceso;
DELETE FROM Administracion_tercero;
DELETE FROM Administracion_rango;
DELETE FROM SGI_grupodocumento;
DELETE FROM Administracion_empresa;
DELETE FROM Administracion_centropoblado;
DELETE FROM Administracion_municipio;
DELETE FROM Administracion_departamento;
DELETE FROM Administracion_pais;
DELETE FROM Administracion_tipocontrato;
DELETE FROM TalentoHumano_entidadescafe;
DELETE FROM TalentoHumano_tipoentidadescafe;
DELETE FROM Administracion_tipoidentificacion;
DELETE FROM Administracion_tipotercero;
DELETE FROM Administracion_tipodocumento;
DELETE FROM Administracion_tipodocumentotercero;
DELETE FROM Administracion_unidadmedida;
DELETE FROM SGI_estadoarchivo;
DELETE FROM Notificaciones_textonotificaciondelsistema;
DELETE FROM Notificaciones_selecciondenotificacionarecibir;
DELETE FROM Notificaciones_eventodesencadenador;
DELETE FROM Administracion_subproductosubservicio;
DELETE FROM Administracion_productoservicio;
DELETE FROM Financiero_actividadeconomica;
DELETE FROM Financiero_subtipomovimiento;
DELETE FROM Financiero_categoriamovimiento;
DELETE FROM Financiero_entidadbancaria;
DELETE FROM Financiero_estadofcdetalle;
DELETE FROM Financiero_estadoflujocaja;
DELETE FROM Financiero_tipomovimiento;
DELETE FROM Notificaciones_tiponotificacion;
DELETE FROM Proyectos_tipogarantia;
DELETE FROM Administracion_permisosfuncionalidad;
DELETE FROM auth_group_permissions;
DELETE FROM auth_group;
DELETE FROM TalentoHumano_nivelriesgoarl;
DELETE FROM Administracion_parametro;
DELETE FROM TalentoHumano_tipopermiso;

-- HABILITAR ACTUALIZACION SEGURA
SET SQL_SAFE_UPDATES = 1;
-- VER VARIABLE GLOBAL
SHOW VARIABLES LIKE "SQL_SAFE_UPDATES";