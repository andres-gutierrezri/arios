from EVA.permisos import Permiso

app_name = 'GestionDocumental'

permisos = [Permiso('index', None),
            Permiso('consecutivo-documento-crear', ['GestionDocumental.add_consecutivodocumento']),
            ]
