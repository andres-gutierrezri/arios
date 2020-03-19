from EVA.permisos import Permiso

app_name = 'Administracion'

permisos = [Permiso('index', None),
            Permiso('terceros', ['Administracion.view_tercero']),
            Permiso('terceros-crear', ['Administracion.add_tercero']),
            Permiso('terceros-editar', ['Administracion.change_tercero']),
            Permiso('terceros-detalle', ['Administracion.view_tercero']),
            Permiso('terceros-eliminar', ['Administracion.delete_tercero']),
            Permiso('empresas', ['Administracion.view_empresa']),
            Permiso('empresas-crear', ['Administracion.add_empresa']),
            Permiso('empresas-editar', ['Administracion.change_empresa']),
            Permiso('empresas-eliminar', ['Administracion.delete_empresa']),
            Permiso('sub-empresas', ['Administracion.view_empresa']),
            Permiso('sub-empresas-crear', ['Administracion.add_empresa']),
            Permiso('sub-empresas-editar', ['Administracion.change_empresa']),
            Permiso('sub-empresas-eliminar', ['Administracion.delete_empresa']),
            ]