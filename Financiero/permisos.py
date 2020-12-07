from EVA.permisos import Permiso

app_name = 'Financiero'

permisos = [Permiso('index', None),
            Permiso('factura-index', ['Financiero.view_facturaencabezado']),
            Permiso('factura-crear', ['Financiero.add_facturaencabezado']),
            Permiso('factura-editar', ['Financiero.change_facturaencabezado']),
            Permiso('factura-detalle', ['Financiero.view_facturaencabezado']),
            Permiso('factura-imprimir', ['Financiero.view_facturaencabezado']),
            Permiso('factura-enviar-correo', ['Financiero.add_facturaencabezado']),
            Permiso('subtipo-movimiento-index', ['Financiero.view_subtipomovimiento']),
            Permiso('subtipo-movimiento-crear', ['Financiero.add_subtipomovimiento']),
            Permiso('subtipo-movimiento-editar', ['Financiero.change_subtipomovimiento']),
            Permiso('subtipo-movimiento-eliminar', ['Financiero.delete_subtipomovimiento']),
            Permiso('categoria-movimiento-index', ['Financiero.view_categoriamovimiento']),
            Permiso('categoria-movimiento-crear', ['Financiero.add_categoriamovimiento']),
            Permiso('categoria-movimiento-editar', ['Financiero.change_categoriamovimiento']),
            Permiso('categoria-movimiento-eliminar', ['Financiero.delete_categoriamovimiento']),
            ]
