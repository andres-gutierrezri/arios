from EVA.permisos import Permiso

app_name = 'TalentoHumano'

permisos = [Permiso('index', None),
            Permiso('entidades-cafe-index', ['TalentoHumano.view_entidadescafe']),
            Permiso('entidades-cafe-crear', ['TalentoHumano.add_entidadescafe']),
            Permiso('entidades-cafe-editar', ['TalentoHumano.change_entidadescafe']),
            Permiso('entidades-cafe-eliminar', ['TalentoHumano.delete_entidadescafe']),
            Permiso('colaboradores-index', ['TalentoHumano.view_colaborador']),
            Permiso('colaboradores-crear', ['TalentoHumano.add_colaborador']),
            Permiso('colaboradores-editar', ['TalentoHumano.change_colaborador']),
            Permiso('colaboradores-eliminar', ['TalentoHumano.delete_colaborador']),
            Permiso('colaboradores-permisos', ['auth.change_permission']),
            ]
