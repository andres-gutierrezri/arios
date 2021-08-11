import json
import datetime
import logging
import os

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.transaction import atomic, rollback
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_sameorigin

from EVA.General.modeljson import RespuestaJson
from EVA.General.utilidades import paginar, app_datetime_now
from EVA.views.index import AbstractEvaLoggedView

from TalentoHumano.models import PermisoLaboral, TipoPermiso


LOGGER = logging.getLogger(__name__)


class PermisosLaboralesIndexView(AbstractEvaLoggedView):
    def get(self, request, id_tipo_permiso):
        if id_tipo_permiso == 0:
            permisos = PermisoLaboral.objects.filter(usuario_crea_id=request.user.id)
        else:
            permisos = PermisoLaboral.objects.filter(tipo_permiso_id=id_tipo_permiso, usuario_crea_id=request.user.id)

        search = request.GET.get('search', '')
        page = request.GET.get('page', 1)
        total = len(permisos)

        if search:
            permisos = permisos.filter(Q(fecha_creacion__icontains=search) |
                                       Q(fecha_inicio__icontains=search) |
                                       Q(fecha_fin__icontains=search) |
                                       Q(motivo_permiso__icontains=search) |
                                       Q(tipo_permiso__nombre__icontains=search))

        coincidencias = len(permisos)
        permisos = paginar(permisos.order_by('-id'), page, 10)

        datos = {'permisos': permisos,
                 'id_tipo_permiso': id_tipo_permiso,
                 'tipos_permiso': self.tipos_permiso_filtro(),
                 'buscar': search,
                 'coincidencias': coincidencias,
                 'total': total,
                 'fecha': datetime.datetime.now(),
                 'menu_actual': 'permisos-laborales'}

        return render(request, 'TalentoHumano/PermisosLaborales/index.html', datos)

    @staticmethod
    def tipos_permiso_filtro() -> list:
        tipos_permiso = TipoPermiso.objects.filter(estado=True)
        lista_tipo_permiso = [{'campo_valor': 0, 'campo_texto': 'Todos'}]

        for tipo_permiso in tipos_permiso:
            lista_tipo_permiso.append({'campo_valor': tipo_permiso.id, 'campo_texto': tipo_permiso.nombre})
        return lista_tipo_permiso


class PermisoLaboralCrearView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'TalentoHumano/PermisosLaborales/_modal_crear_editar_permiso.html',
                      datos_xa_render(request))

    def post(self, request):
        permiso = PermisoLaboral.from_dictionary(request.POST)
        permiso.usuario_crea = request.user
        permiso.fecha_creacion = app_datetime_now()
        permiso.soporte = request.FILES.get('archivo', None)

        try:
            permiso.full_clean(exclude=['motivo_editar', 'soporte'])
        except ValidationError as errores:
            messages.error(request, "Falló la creación del permiso laboral. Valide los datos ingresados")
            return redirect(reverse('TalentoHumano:permisos-laborales-index', args=[0]))

        try:
            with atomic():
                permiso.save()
                messages.success(request, "Se ha creado la solicitud del permiso laboral")
                return redirect(reverse('TalentoHumano:permisos-laborales-index', args=[0]))
        except:
            rollback()
            LOGGER.exception("Error en el permiso laboral")
            return RespuestaJson.error("Ha ocurrido un error al guardar la información")


class PermisoLaboralEditarView(AbstractEvaLoggedView):
    def get(self, request, id_permiso):
        permiso = PermisoLaboral.objects.get(id=id_permiso)

        return render(request, 'TalentoHumano/PermisosLaborales/_modal_crear_editar_permiso.html',
                      datos_xa_render(request, permiso))

    def post(self, request, id_permiso):
        update_fields = ['tipo_permiso', 'fecha_inicio', 'fecha_fin', 'motivo_permiso', 'soporte', 'motivo_editar',
                         'fecha_modificacion', 'usuario_modifica']

        permiso_db = PermisoLaboral.objects.get(id=id_permiso)
        permiso = PermisoLaboral.from_dictionary(request.POST)

        permiso.id = permiso_db.id
        permiso.fecha_creacion = permiso_db.fecha_creacion
        permiso.usuario_crea = permiso_db.usuario_crea
        permiso.usuario_modifica = request.user
        permiso.soporte = request.FILES.get('archivo', None)

        if not permiso.soporte:
            permiso.soporte = permiso_db.soporte

        try:
            permiso.full_clean(validate_unique=False)
        except ValidationError as errores:
            messages.error(request, "Falló la edición. Valide los datos ingresados al editar el permiso laboral")
            return redirect(reverse('TalentoHumano:permisos-laborales-index', args=[0]))

        if permiso_db.comparar(permiso, excluir=['fecha_modificacion', 'usuario_modifica', 'motivo_editar']):
            messages.success(request, "No se hicieron cambios en la solicitud del permiso laboral")
            return redirect(reverse('TalentoHumano:permisos-laborales-index', args=[0]))
        else:
            try:
                with atomic():
                    permiso.save(update_fields=update_fields)
                    messages.success(request, "Se ha editado la reserva para la sala de juntas")
                    return redirect(reverse('TalentoHumano:permisos-laborales-index', args=[0]))
            except:
                rollback()
                LOGGER.exception("Error al editar la solicitud del permiso laboral")
                return RespuestaJson.error("Se presentó un error al editar la solicitud del permiso laboral")


class PermisoLaboralEliminarView(AbstractEvaLoggedView):
    def post(self, request, id_permiso):
        permiso_db = PermisoLaboral.objects.get(id=id_permiso)
        body_unicode = request.body.decode('utf-8')
        datos_registro = json.loads(body_unicode)
        motivo_eliminar = datos_registro['justificacion']

        if not permiso_db.estado_empleado:
            return RespuestaJson.error("La solicitud del permiso laboral ya ha sido eliminada")
        try:
            with atomic():
                permiso_db.usuario_modifica = request.user
                permiso_db.estado_empleado = False
                permiso_db.motivo_editar = motivo_eliminar
                permiso_db.save(update_fields=['estado_empleado', 'motivo_editar',
                                               'usuario_modifica', 'fecha_modificacion'])
                return RespuestaJson.exitosa()
        except:
            rollback()
            LOGGER.exception("Error al eliminar la solicitud del permiso laboral")
            return RespuestaJson.error("Ha ocurrido un error al eliminar la solicitud del permiso laboral")


class VerSoporteView(AbstractEvaLoggedView):
    @xframe_options_sameorigin
    def get(self, request, id_permiso):
        permiso = PermisoLaboral.objects.get(id=id_permiso)
        if permiso.soporte:
            extension = os.path.splitext(permiso.soporte.url)[1]
            mime_types = {".jpeg": "image/jpeg",
                          ".jpg": "image/jpeg",
                          ".gif": "image/gif",
                          ".png": "image/png",
                          ".doc": "application/msword",
                          ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
            mime_type = mime_types.get(extension, 'application/pdf')
            response = HttpResponse(permiso.soporte, content_type=mime_type)
            response['Content-Disposition'] = f'inline; filename="Soporte Permiso Laboral{extension}"'
        else:
            response = redirect(reverse('TalentoHumano:permisos-laborales-index', args=[0]))
        return response


def datos_xa_render(request, permiso: PermisoLaboral = None) -> dict:
    tipos_permiso = TipoPermiso.objects.get_xa_select_activos()

    datos = {'tipos_permiso': tipos_permiso,
             'fecha': datetime.datetime.now(),
             'menu_actual': 'permisos-laborales'}

    if permiso:
        datos['permiso'] = permiso
        datos['editar'] = True

    return datos
