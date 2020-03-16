from django.template.defaultfilters import lower
from django.contrib import messages


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
