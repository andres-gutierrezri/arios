from EVA.permisos import Permiso

app_name = 'SGI'

permisos = [Permiso('index', None),
            Permiso('documentos-index', ['SGI.view_documento']),
            Permiso('documentos-crear', ['SGI.add_documento']),
            Permiso('documentos-editar', ['SGI.change_documento']),
            Permiso('documentos-eliminar', ['SGI.delete_documento']),
            Permiso('documentos-cargar', ['SGI.add_archivo']),
            Permiso('documentos-ver', ['SGI.view_archivo']),
            Permiso('cadenas-aprobacion-ver', ['SGI.view_cadenaaprobacionencabezado']),
            Permiso('cadenas-aprobacion-crear', ['SGI.add_cadenaaprobacionencabezado']),
            Permiso('cadenas-aprobacion-editar', ['SGI.change_cadenaaprobacionencabezado']),
            Permiso('cadenas-aprobacion-eliminar', ['SGI.delete_cadenaaprobacionencabezado']),
            Permiso('aprobacion-documentos-ver', ['SGI.view_resultadosaprobacion']),
            Permiso('solicitudes-aprobacion', ['SGI.add_archivo']),
            Permiso('documentos-buscar', ['SGI.view_documento']),
            ]
