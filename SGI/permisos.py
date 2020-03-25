from EVA.permisos import Permiso

app_name = 'SGI'

permisos = [Permiso('index', None),
            Permiso('documentos-index', ['SGI.view_documento']),
            Permiso('documentos-crear', ['SGI.add_documento']),
            Permiso('documentos-editar', ['SGI.change_documento']),
            Permiso('documentos-eliminar', ['SGI.delete_documento']),
            Permiso('documentos-cargar', ['SGI.add_archivo']),
            Permiso('documentos-ver', ['SGI.view_archivo']),
            ]
