from django.contrib.auth.models import User
from django.template.defaultfilters import lower
from django.contrib import messages

from EVA.permisos import get_permisos_eva


def validar_permisos(usuario: User, aplicacion: str, nombre_url: str) -> bool:
    """
    Valida si el usuario tiene permisos para una vista a través del nombre de la url y de la aplicación.
    Los permisos necesarios para cada vista deben ser cargados en cada aplicación para que puedan ser validados.
    :param usuario: Usuario al cual se le van a validar los permisos.
    :param aplicacion: Nombre de la aplicación para la cual se validaran los permisos.
    :param nombre_url: Nombre de la url que corresponde a la vista a la cual se le validaran los permisos.
    :return: True si el usuario tiene permisos o False sino los tiene  para la aplicación y vista asociada al nombre de
    la url.
    """
    if aplicacion == '' and nombre_url == 'eva-index':
        return True

    permisos = get_permisos_eva()
    permiso_menu = 'TalentoHumano.can_menu_' + lower(aplicacion)
    if usuario.has_perm(permiso_menu):
        if aplicacion in permisos:
            for permiso in permisos[aplicacion]:
                if nombre_url == permiso.nombre_url:
                    return permiso.permisos is None or usuario.has_perms(permiso.permisos)
    else:
        return False
    return True


def tiene_permisos(request, aplicacion: str, permisos: [], permisos_compuestos: []):
    """
    Consulta si el usuario tiene permiso para acceder a la funcion a la que intenta ingresar.
    :param request: request del usuario.
    :param aplicacion: nombre de la aplicacion en la que se encuentra el usuario.
    :param permisos: lista de permisos a consultar.
    :param permisos_compuestos: lista de permisos que pertenecen a una aplicacion distinta.
    (deben ser enviados completos. ej: SGI.view_usuarios).
    :return: retorna True si el usuario tiene permiso o falso cuando no los tiene.
    """
    permiso_menu = 'TalentoHumano.can_menu_' + lower(aplicacion)

    permisos_usuario = []
    permisos_usuario.append(permiso_menu)
    if permisos:
        for permiso in permisos:
            permiso_vista = aplicacion + '.' + permiso
            permisos_usuario.append(permiso_vista)
    if permisos_compuestos:
        for permiso_compuesto in permisos_compuestos:
            permisos_usuario.append(permiso_compuesto)

    if not request.user.has_perms(permisos_usuario):
        messages.error(request, 'No tiene permisos para acceder a esta funcionalidad')
        return False
    else:
        return True



