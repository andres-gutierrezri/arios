import json

from django.contrib import messages
from django.contrib.auth.models import Permission, Group, User
from django.http import JsonResponse
from django.urls import reverse

from EVA.General import app_datetime_now
from EVA.views.index import AbstractEvaLoggedView
from django.shortcuts import render, redirect

from TalentoHumano.models import PermisosFuncionalidad
from TalentoHumano.views.gestion_permisos import construir_permisos


class GruposPermisosView(AbstractEvaLoggedView):
    def get(self, request):
        grupos = PermisosFuncionalidad.objects.filter(estado=True, grupo__isnull=False)
        return render(request, 'Administracion/GruposPermisos/index.html', {'grupos': grupos,
                                                                            'fecha': app_datetime_now(),
                                                                            'menu_actual': 'grupos-permisos'})


class GruposPermisosCrearView(AbstractEvaLoggedView):
    def get(self, request):
        OPCION = 'crear'
        permisos = construir_permisos(request, id_filtro=None)
        return render(request, 'Administracion/GruposPermisos/crear-editar.html', datos_xa_render(OPCION, permisos))

    def post(self, request):
        nombre = request.POST.get('nombre', '')
        descripcion = request.POST.get('descripcion', '')
        valores_permisos = json.loads(request.POST.get('valores_permisos', ''))
        permisos = Permission.objects.all()

        if not Group.objects.filter(name=nombre):
            grupo = Group.objects.create(name=nombre)
            PermisosFuncionalidad.objects.create(nombre=nombre, descripcion=descripcion, estado=True,
                                                 grupo=grupo, solo_admin=False)

            guardar_selecciones_permisos(grupo, valores_permisos, permisos)
            messages.success(request, 'Se ha creado el grupo de producto {0} correctamente.'.format(nombre))
        else:
            messages.warning(request, 'Ya existe un grupo de permiso con el mismo nombre {0}'.format(nombre))

        return redirect(reverse('Administracion:grupos-permisos'))


class GruposPermisosEditarView(AbstractEvaLoggedView):

    def get(self, request, id):
        OPCION = 'editar'
        permisos = construir_permisos(request, id_filtro=None, grupo_permiso=id)
        return render(request, 'Administracion/GruposPermisos/crear-editar.html',
                      datos_xa_render(OPCION, permisos, id_grupo=id))

    def post(self, request, id):
        nombre = request.POST.get('nombre', '')
        descripcion = request.POST.get('descripcion', '')
        valores_permisos = json.loads(request.POST.get('valores_permisos', ''))
        permisos = Permission.objects.all()

        if not Group.objects.exclude(id=id).filter(name=nombre):
            grupo = Group(id=id)
            grupo.name = nombre
            grupo.save(update_fields=['name'])

            perm_fun = PermisosFuncionalidad.objects.get(grupo_id=id)
            perm_fun.nombre = nombre
            perm_fun.descripcion = descripcion
            perm_fun.save(update_fields=['nombre', 'descripcion'])

            grupo.permissions.all().delete()
            guardar_selecciones_permisos(grupo, valores_permisos, permisos)
            messages.success(request, 'Se ha editado el grupo de producto {0} correctamente.'.format(nombre))
        else:
            messages.warning(request, 'Ya existe un grupo de permiso con el mismo nombre {0}'.format(nombre))

        return redirect(reverse('Administracion:grupos-permisos'))


class GruposPermisosEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        grupo = Group.objects.get(id=id)
        usuarios = User.objects.all()
        coincidencias = False
        for us in usuarios:
            for grp in us.groups.all():
                if grp == grupo:
                    coincidencias = True
                    break
            if coincidencias:
                break

        if coincidencias:
            return JsonResponse({"estado": "error",
                                 "mensaje": "No puede eliminar este grupo de producto porque aún "
                                            "se encuentra asignado a los colaboradores"})
        else:
            PermisosFuncionalidad.objects.get(grupo=grupo).delete()
            grupo.delete()
            messages.success(request, 'Se ha eliminado el grupo de permiso {0}'.format(grupo.name))
            return JsonResponse({"estado": "OK",
                                 "mensaje": 'Se ha eliminado el grupo de producto correctamente.'})


VER = 1
CREAR = 2
EDITAR = 3
ELIMINAR = 4


def guardar_selecciones_permisos(grupo, valores_permisos, permisos):

    for valor in valores_permisos:
        for permiso in permisos:
            if valor['funcionalidad'] == permiso.content_type_id:
                for dato in valor['permiso']:
                    if dato == VER and permiso.codename.startswith('view'):
                        grupo.permissions.add(permiso)
                    elif dato == CREAR and permiso.codename.startswith('add'):
                        grupo.permissions.add(permiso)
                    elif dato == EDITAR and permiso.codename.startswith('change'):
                        grupo.permissions.add(permiso)
                    elif dato == ELIMINAR and permiso.codename.startswith('delete'):
                        grupo.permissions.add(permiso)
    return


def datos_xa_render(OPCION, permisos, id_grupo=None) -> dict:
    """
    Datos necesarios para la creación de los html de los Grupos de Permisos.
    :param permisos: Lista de permisos a mostrar
    :param id_grupo: id del grupo en caso de que la acción sea editar.
    :return: Un diccionario con los datos.
    """
    datos = {'opcion': OPCION, 'id_grupo': id_grupo, 'menu_actual': 'grupos-permisos'}
    datos.update(permisos)
    if id_grupo:
        datos.update({'grupo': PermisosFuncionalidad.objects.get(grupo_id=id_grupo).to_dict()})

    return datos
