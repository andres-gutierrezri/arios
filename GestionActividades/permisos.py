from EVA.permisos import Permiso

app_name = 'GestionActividades'

permisos = [Permiso('index', None),
            Permiso('grupo-actividades-index', ['GestionActividades.view_grupoactividades']),
            Permiso('grupo-actividades-crear', ['GestionActividades.add_grupoactividades']),
            Permiso('grupo-actividades-editar', ['GestionActividades.change_grupoactividades']),
            Permiso('actividades-index', ['GestionActividades.view_actividades']),
            Permiso('actividades-crear', ['GestionActividades.add_actividades']),
            Permiso('actividades-editar', ['GestionActividades.change_actividades']),
            ]
