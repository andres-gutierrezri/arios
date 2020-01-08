from Administracion.models import Empresa


def get_empresa_global(request):

    empresa = request.session.get('empresa', None)

    if empresa is None:
        empresa = Empresa.get_default().to_json()

    return empresa


def get_id_empresa_global(request):
    return int(get_empresa_global(request)['id'])


def get_id_ppal_subempresa_global(request):
    sub = (get_empresa_global(request)['subempresa'])

    if sub:
        return int(get_empresa_global(request)['empresa_ppal_id'])
    else:
        return int(get_empresa_global(request)['id'])
