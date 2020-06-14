from django.contrib import messages, auth
from django.contrib.auth.models import Permission, User
from django.shortcuts import render, redirect
from django.urls import reverse

from EVA.views.index import AbstractEvaLoggedView


class AsignacionPermisosView(AbstractEvaLoggedView):
    def get(self, request, id):
        user_permisos = obtener_permisos(User.objects.get(id=request.user.id))
        print(user_permisos)
        permisos = Permission.objects.all()
        return render(request, 'TalentoHumano/GestionPermisos/asignacion_permisos.html',
                      {'permisos': permisos,
                       'user_permisos': user_permisos,
                       'colaborador': {'id': id}})

    def post(self, request, id):
        print(id)
        messages.success(request, 'Se han guardado las selecciones correctamente')
        return redirect(reverse('TalentoHumano:colaboradores-index', args=[0]))


def obtener_permisos(user, obj=None):
    permissions = set()
    name = 'get_%s_permissions' % 'user'
    for backend in auth.get_backends():
        if hasattr(backend, name):
            permissions.update(getattr(backend, name)(user, obj))
    return permissions
