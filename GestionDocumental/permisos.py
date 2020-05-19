from EVA.permisos import Permiso

app_name = 'GestionDocumental'

permisos = [Permiso('index', None),
            Permiso('consecutivo-oficios-index', ['GestionDocumental.view_consecutivooficio']),
            Permiso('consecutivo-oficios-crear', ['GestionDocumental.add_consecutivooficio']),
            ]
