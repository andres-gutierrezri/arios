import json

from django.contrib import messages, auth
from django.contrib.auth.models import User, Permission
from django.shortcuts import render, redirect
from django.urls import reverse

from EVA.views.index import AbstractEvaLoggedView
from TalentoHumano.models import PermisosFuncionalidad, Colaborador


class AsignacionPermisosView(AbstractEvaLoggedView):
    def get(self, request, id):
        colaborador = Colaborador.objects.get(id=id)
        user_permisos = obtener_permisos(User.objects.get(id=request.user.id))
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
                       'acciones_permisos': acciones_permisos,
                       'user_permisos': user_permisos})

    def post(self, request, id):
        datos_permisos = json.loads(request.POST.get('valores_permisos', ''))

        funcionalidades = PermisosFuncionalidad.objects.filter(estado=True)

        for func in funcionalidades:
            for datos in datos_permisos:
                if func.content_type_id == datos['funcionalidad']:
                    for perm in datos['permiso']:
                        if perm == 1:
                            permiso = Permission.objects.get(content_type_id=func.content_type_id,
                                                             codename='view_' + func.content_type.model)
                            User.objects.get(id=id).user_permissions.add(permiso)
                        elif perm == 2:
                            permiso = Permission.objects.get(content_type_id=func.content_type_id,
                                                             codename='add_' + func.content_type.model)
                            User.objects.get(id=id).user_permissions.add(permiso)
                        elif perm == 3:
                            permiso = Permission.objects.get(content_type_id=func.content_type_id,
                                                             codename='change_' + func.content_type.model)
                            User.objects.get(id=id).user_permissions.add(permiso)
                        elif perm == 4:
                            permiso = Permission.objects.get(content_type_id=func.content_type_id,
                                                             codename='delete_' + func.content_type.model)
                            User.objects.get(id=id).user_permissions.add(permiso)

        messages.success(request, 'Se han guardado las selecciones correctamente')
        return redirect(reverse('TalentoHumano:colaboradores-index', args=[0]))


def obtener_permisos(user, obj=None):
    permissions = set()
    name = 'get_%s_permissions' % 'user'
    for backend in auth.get_backends():
        if hasattr(backend, name):
            permissions.update(getattr(backend, name)(user, obj))
    return permissions
