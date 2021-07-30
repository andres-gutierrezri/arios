from EVA.permisos import Permiso

app_name = 'GestionActividades'

permisos = [Permiso('index', None),
            Permiso('grupos-actividades-index', ['GestionActividades.view_grupoactividad']),
            Permiso('grupos-actividades-crear', ['GestionActividades.add_grupoactividad']),
            Permiso('grupos-actividades-editar', ['GestionActividades.change_grupoactividad']),
            Permiso('grupos-actividades-eliminar', ['GestionActividades.delete_grupoactividad']),
            Permiso('actividades-index', ['GestionActividades.view_actividad']),
            Permiso('actividades-crear', ['GestionActividades.add_actividad']),
            Permiso('actividades-editar', ['GestionActividades.change_actividad']),
            Permiso('actividades-actualizar', ['GestionActividades.add_avanceactividad']),
            Permiso('actividades-eliminar', ['GestionActividades.delete_actividad']),
            Permiso('actividades-cerrar-reabrir', ['GestionActividades.change_actividad']),
            Permiso('actividades-ver', ['GestionActividades.view_avanceactividad']),
            Permiso('soportes-cargar', ['GestionActividades.add_soporteactividad']),
            Permiso('soportes-ver', ['GestionActividades.view_soporteactividad']),
            Permiso('solicitudes-aprobacion-index', ['GestionActividades.view_modificacionactividad']),
            Permiso('accion-modificaciones-actividad', ['GestionActividades.change_modificacionactividad']),
            Permiso('ver-modificaciones-actividad', ['GestionActividades.view_modificacionactividad'])
            ]
