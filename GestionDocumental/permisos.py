from EVA.permisos import Permiso

app_name = 'GestionDocumental'

permisos = [Permiso('index', None),
            Permiso('consecutivo-oficios-index', ['GestionDocumental.view_consecutivooficio']),
            Permiso('consecutivo-oficios-crear', ['GestionDocumental.add_consecutivooficio']),
            Permiso('consecutivo-contratos-index', ['GestionDocumental.view_consecutivocontrato']),
            Permiso('consecutivo-contratos-crear', ['GestionDocumental.add_consecutivocontrato']),
            ]