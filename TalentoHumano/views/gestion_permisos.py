import json
import re

from django.contrib import messages, auth
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect
from django.urls import reverse

from EVA.views.index import AbstractEvaLoggedView
from Administracion.models import PermisosFuncionalidad

VER = 1
CREAR = 2
EDITAR = 3
ELIMINAR = 4
TODOS = 0
GRUPOS = 1


class AsignacionPermisosView(AbstractEvaLoggedView):
    def get(self, request, id, id_filtro):
        usuario = User.objects.get(id=id)
        if usuario.is_superuser or usuario == request.user:
            messages.error(request, 'No tiene permisos para acceder a esta funcionalidad.')
            return redirect(reverse('TalentoHumano:colaboradores-index', args=[0]))

        return render(request, 'TalentoHumano/GestionPermisos/asignacion_permisos.html',
                      construir_permisos(request, usuario=usuario, id_filtro=id_filtro))

    def post(self, request, id, id_filtro):
        valores_permisos = json.loads(request.POST.get('valores_permisos', ''))
        datos_permisos = json.loads(request.POST.get('datos_permisos', ''))
        valores_funcionalidades = []
        valores_grupos = []

        datos_funcionalidades = []

        for vp in valores_permisos:
            if vp['tipo_funcionalidad']:
                valores_funcionalidades.append(vp)
            else:
                valores_grupos.append(vp)

        for dp in datos_permisos:
            if dp['tipo_funcionalidad']:
                datos_funcionalidades.append(dp)

        usuario = User.objects.get(id=id)
        if valores_funcionalidades:
            funcionalidades = PermisosFuncionalidad.objects.filter(estado=True, grupo=None)
            limpiar_permisos(usuario, id_filtro)

            for func in funcionalidades:
                coincidencias = False
                for datos in valores_funcionalidades:
                    if func.content_type_id == datos['funcionalidad']:
                        coincidencias = True
                        for perm in datos['permiso']:
                            if perm == VER:
                                consultar_permiso(func, VER, datos_funcionalidades, usuario)
                            elif perm == CREAR:
                                consultar_permiso(func, CREAR, datos_funcionalidades, usuario)
                            elif perm == EDITAR:
                                consultar_permiso(func, EDITAR, datos_funcionalidades, usuario)
                            elif perm == ELIMINAR:
                                consultar_permiso(func, ELIMINAR, datos_funcionalidades, usuario)
                if not coincidencias:
                    limpiar_permisos(usuario, id_filtro, modulo=func.content_type.app_label)
        else:
            limpiar_permisos(usuario, id_filtro)

        if valores_grupos:
            grupos = PermisosFuncionalidad.objects.filter(estado=True, content_type=None)
            limpiar_grupos(usuario)

            for grp in grupos:
                coincidencias = False
                for datos in valores_grupos:
                    if grp.id == datos['grupo']:
                        coincidencias = True
                        usuario.groups.add(grp.grupo)

                if not coincidencias:
                    limpiar_grupos(usuario, grp.grupo)
        else:
            limpiar_grupos(usuario)

        messages.success(request, 'Se actualizado los permisos para {0} correctamente'.format(usuario.get_full_name()))
        return redirect(reverse('TalentoHumano:colaboradores-permisos', args=[id, id_filtro]))


def obtener_permisos(user, obj=None):
    permissions = set()
    name = 'get_%s_permissions' % 'user'
    for backend in auth.get_backends():
        if hasattr(backend, name):
            permissions.update(getattr(backend, name)(user, obj))
    return permissions


def limpiar_grupos(usuario, grupo=None):
    if grupo:
        usuario.groups.remove(grupo)
    else:
        for grp in Group.objects.all():
            usuario.groups.remove(grp)


def limpiar_permisos(usuario, id_filtro, modulo=None):
    if id_filtro == TODOS:
        if modulo:
            poner_quitar_permiso_menu(usuario, modulo, quitar=True)
        else:
            for perm in usuario.user_permissions.all():
                usuario.user_permissions.remove(perm)
    else:
        ct = ContentType.objects.get(id=id_filtro)
        for perm in usuario.user_permissions.filter(content_type__app_label=ct.app_label):
            usuario.user_permissions.remove(perm)


def consultar_permiso(funcionalidad, accion, datos_permisos, usuario):
    poner_quitar_permiso_menu(usuario, funcionalidad.content_type.app_label, poner=True)
    permiso = ''
    for func in datos_permisos:
        if func['funcionalidad'] == funcionalidad.content_type_id:
            for perm in func['permisos']:
                if perm['orden'] == accion:
                    permiso = Permission.objects.get(id=perm['id'])
                    break
    usuario.user_permissions.add(permiso)


def construir_lista_notificaciones(objeto, permisos):
    nueva_lista = []
    for perm in permisos:
        if 'view' in perm['nombre']:
            nueva_lista.append({'orden': 1, 'id': perm['id'], 'nombre': 'Ver'})
        elif 'add' in perm['nombre']:
            nueva_lista.append({'orden': 2, 'id': perm['id'], 'nombre': 'Crear'})
        elif 'change' in perm['nombre']:
            nueva_lista.append({'orden': 3, 'id': perm['id'], 'nombre': 'Editar'})
        elif 'delete' in perm['nombre']:
            nueva_lista.append({'orden': 4, 'id': perm['id'], 'nombre': 'Eliminar'})

    return {'funcionalidad': objeto.content_type_id, 'nombre': objeto.nombre, 'descripcion': objeto.descripcion,
            'permisos': sorted(nueva_lista, key=lambda p: p['orden']), 'tipo_funcionalidad': True, 'id': objeto.id,
            'app_label': objeto.content_type.app_label}


def poner_quitar_permiso_menu(usuario, modulo, poner=False, quitar=False):
    permiso_menu = 'can_menu_{0}'.format(modulo.lower())
    if usuario.has_perm('TalentoHumano.{0}'.format(permiso_menu)):
        if quitar:
            usuario.user_permissions.remove(Permission.objects.get(codename=permiso_menu))
    else:
        if poner:
            usuario.user_permissions.add(Permission.objects.get(codename=permiso_menu))


def obtener_content_type(request, funcionalidades, xa_select=None):
    lista = []
    if xa_select:
        lista.append({'campo_valor': 1, 'campo_texto': 'Grupos'})
    if request.user.has_perms(['auth.add_group', 'auth.change_group']):
        for fun in funcionalidades:
            nombre = construir_nombre_funcionalidad(fun.content_type.app_label)
            if xa_select:
                lista.append({'campo_valor': fun.content_type.id, 'campo_texto': nombre})
            else:
                lista.append({'label': fun.content_type.app_label, 'nombre': nombre})
    else:
        permisos_asignados = request.user.user_permissions.distinct('content_type__app_label')
        for pa in permisos_asignados:
            for fun in funcionalidades:
                nombre = construir_nombre_funcionalidad(fun.content_type.app_label)
                if pa.content_type == fun.content_type:
                    if xa_select:
                        lista.append({'campo_valor': fun.content_type.id, 'campo_texto': nombre})
                    else:
                        lista.append({'label': fun.content_type.app_label, 'nombre': nombre})
    return lista


def consultar_permisos_usuario(usuario, grupo_permiso):
    lista = []
    if grupo_permiso:
        permisos = Group.objects.get(id=grupo_permiso).permissions.all()
    elif usuario:
        permisos = usuario.user_permissions.all()
    else:
        permisos = Permission.objects.none()

    for perm in permisos:
        if not perm.codename.startswith('can_menu'):
            lista.append({'id': perm.id, 'content_type_id': perm.content_type_id})
    return lista


def construir_nombre_funcionalidad(nombre):
    nombre = re.findall('[A-Z][^A-Z]*', nombre)
    nombre_final = ''
    contador = 0

    while len(nombre) != contador:
        nombre_final = '{0} {1}'.format(nombre_final, nombre[contador])
        contador += 1
    return nombre_final


def construir_permisos(request, id_filtro, usuario=None, grupo_permiso=None, ):
    permisos_usuario = consultar_permisos_usuario(usuario, grupo_permiso)
    if usuario:
        grupos_usuario = usuario.groups.all()
    else:
        grupos_usuario = Group.objects.none()

    per_funcionalidad = PermisosFuncionalidad.objects.filter(estado=True, grupo=None)
    per_grupos = PermisosFuncionalidad.objects.filter(estado=True, content_type=None)
    funcionalidades_selecciones = per_funcionalidad.distinct('content_type__app_label')

    if id_filtro and id_filtro != TODOS:
        temp = PermisosFuncionalidad.objects.filter(content_type_id=id_filtro).first()
        if temp:
            per_funcionalidad = per_funcionalidad.filter(content_type__app_label=temp.content_type.app_label)

    permisos_db = Permission.objects.all()
    funcionalidades = request.user.user_permissions.order_by('content_type_id').distinct('content_type_id')

    lista_content_type = obtener_content_type(request, per_funcionalidad.distinct('content_type__app_label'))
    lista_completa = []
    lista_grupos = []

    if not usuario or request.user.is_superuser:
        for pf in per_funcionalidad:
            lista_permisos = []
            for perm in permisos_db:
                if pf.content_type == perm.content_type:
                    if perm.codename.split('_')[1] == perm.content_type.model:
                        lista_permisos.append({'id': perm.id, 'nombre': perm.codename})
            lista_completa.append(construir_lista_notificaciones(pf, lista_permisos))
        if per_grupos and id_filtro == TODOS or id_filtro == GRUPOS:
            for grp in per_grupos:
                lista = {'tipo_funcionalidad': False, 'grupo': grp.id, 'id_grupo': grp.grupo_id,
                         'nombre': grp.nombre, 'descripcion': grp.descripcion}
                lista_completa.append(lista)
                lista_grupos.append(lista)
    else:
        permisos_asignados = request.user.user_permissions.all()
        grupos_asignados = request.user.groups.all()

        for mod in funcionalidades:
            lista_permisos = []
            for perm in permisos_asignados:
                if mod.content_type == perm.content_type:
                    if perm.codename.split('_')[1] == perm.content_type.model:
                        lista_permisos.append({'id': perm.id, 'nombre': perm.codename})

            for pf in per_funcionalidad:
                if mod.content_type == pf.content_type:
                    lista_completa.append(construir_lista_notificaciones(pf, lista_permisos))

        per_grupos = per_grupos.exclude(solo_admin=True)
        if per_grupos and grupos_asignados and id_filtro == TODOS or id_filtro == GRUPOS:
            for grp_asignado in grupos_asignados:
                for grp in per_grupos:
                    if grp_asignado == grp.grupo:
                        lista = {'tipo_funcionalidad': False, 'grupo': grp.id, 'nombre': grp.nombre,
                                 'descripcion': grp.descripcion}
                        lista_completa.append(lista)
                        lista_grupos.append(lista)

    return {'permisos': lista_completa,
            'lista_grupos': lista_grupos,
            'permisos_usuario': permisos_usuario,
            'grupos_usuario': grupos_usuario,
            'usuario': usuario,
            'id_filtro': id_filtro,
            'funcionalidades': funcionalidades,
            'lista_content_type': lista_content_type,
            'funcionalidad_selecciones': obtener_content_type(request, funcionalidades_selecciones, True),
            'datos_permisos': json.dumps(lista_completa)}
