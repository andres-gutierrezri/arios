import json

from django.contrib import messages, auth
from django.contrib.auth.models import User, Permission
from django.shortcuts import render, redirect
from django.urls import reverse

from EVA.views.index import AbstractEvaLoggedView
from TalentoHumano.models import PermisosFuncionalidad, Colaborador

VER = 1
CREAR = 2
EDITAR = 3
ELIMINAR = 4


class AsignacionPermisosView(AbstractEvaLoggedView):
    def get(self, request, id):
        colaborador = Colaborador.objects.get(id=id)
        permisos = PermisosFuncionalidad.objects.all()
        permisos_json = []
        for prm in permisos:
            permisos_json.append({'id': prm.content_type_id})
        acciones_permisos = [{'id': 1, 'nombre': 'Puede Ver'}, {'id': 2, 'nombre': 'Puede Crear'},
                             {'id': 3, 'nombre': 'Puede Editar'}, {'id': 4, 'nombre': 'Puede Borrar'}]
        return render(request, 'TalentoHumano/GestionPermisos/asignacion_permisos.html',
                      {'permisos': permisos,
                       'id_permisos': json.dumps(permisos_json),
                       'colaborador': colaborador,
                       'acciones_permisos': acciones_permisos})

    def post(self, request, id):
        datos_permisos = json.loads(request.POST.get('valores_permisos', ''))
        usuario = User.objects.get(id=id)
        if datos_permisos:
            funcionalidades = PermisosFuncionalidad.objects.filter(estado=True)
            limpiar_permisos(usuario)

            for func in funcionalidades:
                for datos in datos_permisos:
                    if func.content_type_id == datos['funcionalidad']:
                        for perm in datos['permiso']:
                            if perm == VER:
                                usuario.user_permissions.add(consultar_permiso(func, 'view'))
                            elif perm == CREAR:
                                usuario.user_permissions.add(consultar_permiso(func, 'add'))
                            elif perm == EDITAR:
                                usuario.user_permissions.add(consultar_permiso(func, 'change'))
                            elif perm == ELIMINAR:
                                usuario.user_permissions.add(consultar_permiso(func, 'delete'))
        else:
            limpiar_permisos(usuario)

        messages.success(request, 'Se han guardado las selecciones correctamente')
        return redirect(reverse('TalentoHumano:colaboradores-index', args=[0]))


def obtener_permisos(user, obj=None):
    permissions = set()
    name = 'get_%s_permissions' % 'user'
    for backend in auth.get_backends():
        if hasattr(backend, name):
            permissions.update(getattr(backend, name)(user, obj))
    return permissions


def limpiar_permisos(usuario):
    for perm in usuario.user_permissions.all():
        usuario.user_permissions.remove(perm)


def consultar_permiso(funcionalidad, accion):
    return Permission.objects.get(content_type_id=funcionalidad.content_type_id,
                                  codename=accion + '_' + funcionalidad.content_type.model)
