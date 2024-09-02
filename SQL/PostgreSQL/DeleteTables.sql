-- BORRAR DATOS DE LAS TABLAS

-- SELECCIONAR BASE DE DATOS
\! cls
SET client_encoding = 'UTF8';
\connect "railway"

-- BORRAR TABLAS
DELETE FROM "TalentoHumano_colaborador";
DELETE FROM "Administracion_cargo";
DELETE FROM "SGI_gruposdocumentosprocesos";
DELETE FROM "Administracion_proceso";
DELETE FROM "Administracion_tercero";
DELETE FROM "Administracion_rango";
DELETE FROM "SGI_grupodocumento";
DELETE FROM "Administracion_empresa";
DELETE FROM "Administracion_centropoblado";
DELETE FROM "Administracion_municipio";
DELETE FROM "Administracion_departamento";
DELETE FROM "Administracion_pais";
DELETE FROM "Administracion_tipocontrato";
DELETE FROM "TalentoHumano_entidadescafe";
DELETE FROM "TalentoHumano_tipoentidadescafe";
DELETE FROM "Administracion_tipoidentificacion";
DELETE FROM "Administracion_tipotercero";
DELETE FROM "Administracion_tipodocumento";
DELETE FROM "Administracion_tipodocumentotercero";
DELETE FROM "Administracion_unidadmedida";
DELETE FROM "SGI_estadoarchivo";
DELETE FROM "Notificaciones_textonotificaciondelsistema";
DELETE FROM "Notificaciones_selecciondenotificacionarecibir";
DELETE FROM "Notificaciones_eventodesencadenador";
DELETE FROM "Administracion_subproductosubservicio";
DELETE FROM "Administracion_productoservicio";
DELETE FROM "Financiero_actividadeconomica";
DELETE FROM "Financiero_subtipomovimiento";
DELETE FROM "Financiero_categoriamovimiento";
DELETE FROM "Financiero_entidadbancaria";
DELETE FROM "Financiero_estadofcdetalle";
DELETE FROM "Financiero_estadoflujocaja";
DELETE FROM "Financiero_tipomovimiento";
DELETE FROM "Notificaciones_tiponotificacion";
DELETE FROM "Proyectos_tipogarantia";
DELETE FROM "Administracion_permisosfuncionalidad";
DELETE FROM "auth_group_permissions";
DELETE FROM "auth_group";
DELETE FROM "TalentoHumano_nivelriesgoarl";
DELETE FROM "Administracion_parametro";
DELETE FROM "TalentoHumano_tipopermiso";

-- RESTABLECER LA SECUENCIA
ALTER SEQUENCE "TalentoHumano_colaborador_id_seq" RESTART WITH 1;
UPDATE "TalentoHumano_colaborador" SET id = DEFAULT;

ALTER SEQUENCE "Administracion_cargo_id_seq" RESTART WITH 1;
UPDATE "Administracion_cargo" SET id = DEFAULT;

ALTER SEQUENCE "SGI_gruposdocumentosprocesos_id_seq" RESTART WITH 1;
UPDATE "SGI_gruposdocumentosprocesos" SET id = DEFAULT;

ALTER SEQUENCE "Administracion_proceso_id_seq" RESTART WITH 1;
UPDATE "Administracion_proceso" SET id = DEFAULT;

ALTER SEQUENCE "Administracion_tercero_id_seq" RESTART WITH 1;
UPDATE "Administracion_tercero" SET id = DEFAULT;

ALTER SEQUENCE "Administracion_rango_id_seq" RESTART WITH 1;
UPDATE "Administracion_rango" SET id = DEFAULT;

ALTER SEQUENCE "SGI_grupodocumento_id_seq" RESTART WITH 1;
UPDATE "SGI_grupodocumento" SET id = DEFAULT;

ALTER SEQUENCE "Administracion_empresa_id_seq" RESTART WITH 1;
UPDATE "Administracion_empresa" SET id = DEFAULT;

ALTER SEQUENCE "Administracion_centropoblado_id_seq" RESTART WITH 1;
UPDATE "Administracion_centropoblado" SET id = DEFAULT;

ALTER SEQUENCE "Administracion_municipio_id_seq" RESTART WITH 1;
UPDATE "Administracion_municipio" SET id = DEFAULT;

ALTER SEQUENCE "Administracion_departamento_id_seq" RESTART WITH 1;
UPDATE "Administracion_departamento" SET id = DEFAULT;

ALTER SEQUENCE "Administracion_pais_id_seq" RESTART WITH 1;
UPDATE "Administracion_pais" SET id = DEFAULT;

ALTER SEQUENCE "Administracion_tipocontrato_id_seq" RESTART WITH 1;
UPDATE "Administracion_tipocontrato" SET id = DEFAULT;

ALTER SEQUENCE "TalentoHumano_entidadescafe_id_seq" RESTART WITH 1;
UPDATE "TalentoHumano_entidadescafe" SET id = DEFAULT;

ALTER SEQUENCE "TalentoHumano_tipoentidadescafe_id_seq" RESTART WITH 1;
UPDATE "TalentoHumano_tipoentidadescafe" SET id = DEFAULT;

ALTER SEQUENCE "Administracion_tipoidentificacion_id_seq" RESTART WITH 1;
UPDATE "Administracion_tipoidentificacion" SET id = DEFAULT;

ALTER SEQUENCE "Administracion_tipotercero_id_seq" RESTART WITH 1;
UPDATE "Administracion_tipotercero" SET id = DEFAULT;

ALTER SEQUENCE "Administracion_tipodocumento_id_seq" RESTART WITH 1;
UPDATE "Administracion_tipodocumento" SET id = DEFAULT;

ALTER SEQUENCE "Administracion_tipodocumentotercero_id_seq" RESTART WITH 1;
UPDATE "Administracion_tipodocumentotercero" SET id = DEFAULT;

UPDATE "Administracion_unidadmedida" SET id = DEFAULT;

ALTER SEQUENCE "SGI_estadoarchivo_id_seq" RESTART WITH 1;
UPDATE "SGI_estadoarchivo" SET id = DEFAULT;

ALTER SEQUENCE "Notificaciones_textonotificaciondelsistema_id_seq" RESTART WITH 1;
UPDATE "Notificaciones_textonotificaciondelsistema" SET id = DEFAULT;

ALTER SEQUENCE "Notificaciones_selecciondenotificacionarecibir_id_seq" RESTART WITH 1;
UPDATE "Notificaciones_selecciondenotificacionarecibir" SET id = DEFAULT;

ALTER SEQUENCE "Notificaciones_eventodesencadenador_id_seq" RESTART WITH 1;
UPDATE "Notificaciones_eventodesencadenador" SET id = DEFAULT;

ALTER SEQUENCE "Administracion_subproductosubservicio_id_seq" RESTART WITH 1;
UPDATE "Administracion_subproductosubservicio" SET id = DEFAULT;

ALTER SEQUENCE "Administracion_productoservicio_id_seq" RESTART WITH 1;
UPDATE "Administracion_productoservicio" SET id = DEFAULT;

ALTER SEQUENCE "Financiero_actividadeconomica_id_seq" RESTART WITH 1;
UPDATE "Financiero_actividadeconomica" SET id = DEFAULT;

ALTER SEQUENCE "Financiero_subtipomovimiento_id_seq" RESTART WITH 1;
UPDATE "Financiero_subtipomovimiento" SET id = DEFAULT;

ALTER SEQUENCE "Financiero_categoriamovimiento_id_seq" RESTART WITH 1;
UPDATE "Financiero_categoriamovimiento" SET id = DEFAULT;

ALTER SEQUENCE "Financiero_entidadbancaria_id_seq" RESTART WITH 1;
UPDATE "Financiero_entidadbancaria" SET id = DEFAULT;

ALTER SEQUENCE "Financiero_estadofcdetalle_id_seq" RESTART WITH 1;
UPDATE "Financiero_estadofcdetalle" SET id = DEFAULT;

ALTER SEQUENCE "Financiero_estadoflujocaja_id_seq" RESTART WITH 1;
UPDATE "Financiero_estadoflujocaja" SET id = DEFAULT;

ALTER SEQUENCE "Financiero_tipomovimiento_id_seq" RESTART WITH 1;
UPDATE "Financiero_tipomovimiento" SET id = DEFAULT;

ALTER SEQUENCE "Notificaciones_tiponotificacion_id_seq" RESTART WITH 1;
UPDATE "Notificaciones_tiponotificacion" SET id = DEFAULT;

ALTER SEQUENCE "Proyectos_tipogarantia_id_seq" RESTART WITH 1;
UPDATE "Proyectos_tipogarantia" SET id = DEFAULT;

ALTER SEQUENCE "Administracion_permisosfuncionalidad_id_seq" RESTART WITH 1;
UPDATE "Administracion_permisosfuncionalidad" SET id = DEFAULT;

ALTER SEQUENCE "auth_group_permissions_id_seq" RESTART WITH 1;
UPDATE "auth_group_permissions" SET id = DEFAULT;

ALTER SEQUENCE "auth_group_id_seq" RESTART WITH 1;
UPDATE "auth_group" SET id = DEFAULT;

ALTER SEQUENCE "TalentoHumano_nivelriesgoarl_id_seq" RESTART WITH 1;
UPDATE "TalentoHumano_nivelriesgoarl" SET id = DEFAULT;

ALTER SEQUENCE "Administracion_parametro_id_seq" RESTART WITH 1;
UPDATE "Administracion_parametro" SET id = DEFAULT;

ALTER SEQUENCE "TalentoHumano_tipopermiso_id_seq" RESTART WITH 1;
UPDATE "TalentoHumano_tipopermiso" SET id = DEFAULT;