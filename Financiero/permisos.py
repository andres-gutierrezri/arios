from EVA.permisos import Permiso

app_name = 'Financiero'

permisos = [Permiso('index', None),
            Permiso('factura-index', ['Financiero.view_facturaencabezado']),
            Permiso('factura-crear', ['Financiero.add_facturaencabezado']),
            Permiso('factura-editar', ['Financiero.change_facturaencabezado']),
            Permiso('factura-detalle', ['Financiero.view_facturaencabezado']),
            Permiso('factura-imprimir', ['Financiero.view_facturaencabezado']),
            ]