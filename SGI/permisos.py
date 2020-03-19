from EVA.permisos import Permiso

app_name = 'SGI'

permisos = [Permiso('index', None),
            Permiso('documentos-index', ['SGI.view_documento'])]
