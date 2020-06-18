import json

from django.contrib import messages, auth
from django.contrib.auth.models import User, Permission
from django.shortcuts import render, redirect
from django.urls import reverse

from EVA.views.index import AbstractEvaLoggedView
from TalentoHumano.models import PermisosFuncionalidad

VER = 1
CREAR = 2
EDITAR = 3
ELIMINAR = 4


class AsignacionPermisosView(AbstractEvaLoggedView):
    def get(self, request, id):
        usuario = User.objects.get(id=id)
        permisos_usuario = usuario.user_permissions.all()
        per_funcionalidad = PermisosFuncionalidad.objects.filter(estado=True)
        permisos_db = Permission.objects.all()
        funcionalidades = request.user.user_permissions.order_by('content_type_id').distinct('content_type_id')

        lista_completa = []

        if request.user.is_superuser:
            for pf in per_funcionalidad:
                lista_permisos = []
                for perm in permisos_db:
                    if pf.content_type == perm.content_type:
                        lista_permisos.append({'id': perm.id, 'nombre': perm.codename})
                lista_completa.append(construir_lista_notificaciones(pf, lista_permisos))

        else:
            permisos_asignados = request.user.user_permissions.all()

            for mod in funcionalidades:
                lista_permisos = []
                for perm in permisos_asignados:
                    if mod.content_type == perm.content_type:
                        lista_permisos.append({'id': perm.id, 'nombre': perm.codename})

                for pf in per_funcionalidad:
                    if mod.content_type == pf.content_type:
                        lista_completa.append(construir_lista_notificaciones(pf, lista_permisos))

        return render(request, 'TalentoHumano/GestionPermisos/asignacion_permisos.html',
                      {'permisos': lista_completa,
                       'permisos_usuario': permisos_usuario,
                       'usuario': usuario,
                       'funcionalidades': funcionalidades,
                       'datos_permisos': json.dumps(lista_completa)})

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


def consultar_permiso(funcionalidad, accion, datos_permisos):
    permiso = ''
    for func in datos_permisos:
        if func['funcionalidad'] == funcionalidad.content_type_id:
            for perm in func['permisos']:
                if perm['orden'] == accion:
                    permiso = Permission.objects.get(id=perm['id'])
                    break
    return permiso


def construir_lista_notificaciones(objeto, permisos):
    nueva_lista = []
    for perm in permisos:
        if 'view' in perm['nombre']:
            nueva_lista.append({'orden': 1, 'id': perm['id'], 'nombre': 'Puede Ver'})
        elif 'add' in perm['nombre']:
            nueva_lista.append({'orden': 2, 'id': perm['id'], 'nombre': 'Puede Crear'})
        elif 'change' in perm['nombre']:
            nueva_lista.append({'orden': 3, 'id': perm['id'], 'nombre': 'Puede Editar'})
        elif 'delete' in perm['nombre']:
            nueva_lista.append({'orden': 4, 'id': perm['id'], 'nombre': 'Puede Eliminar'})

    return {'funcionalidad': objeto.id, 'nombre': objeto.nombre, 'descripcion': objeto.descripcion,
            'permisos': sorted(nueva_lista, key=lambda p: p['orden'])}
