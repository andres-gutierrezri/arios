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
        return render(request, 'TalentoHumano/PermisosLaborales/_modal_crear_editar_permiso.html', datos_xa_render())

    def post(self, request):
        permiso = PermisoLaboral.from_dictionary(request.POST)
        permiso.usuario_crea = request.user
        permiso.fecha_creacion = app_datetime_now()
        permiso.soporte = request.FILES.get('archivo', None)

        try:
            permiso.full_clean(exclude=['motivo_editar'])
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


class VerSoporteView(AbstractEvaLoggedView):
    @xframe_options_sameorigin
    def get(self, request, id_permiso):
        permiso = PermisoLaboral.objects.get(id=id_permiso)
        if permiso.soporte:
            extension = os.path.splitext(permiso.soporte.url)[1]
            mime_types = {'.docx': 'application/msword'}
            mime_type = mime_types.get(extension, 'application/pdf')
            response = HttpResponse(permiso.soporte, content_type=mime_type)
            response['Content-Disposition'] = f'inline; filename="Soporte Permiso Laboral{extension}"'
        else:
            response = redirect(reverse('TalentoHumano:permisos-laborales-index', args=[0]))
        return response


def datos_xa_render(permiso: PermisoLaboral = None) -> dict:
    tipos_permiso = TipoPermiso.objects.get_xa_select_activos()

    datos = {'tipos_permiso': tipos_permiso,
             'fecha': datetime.datetime.now(),
             'menu_actual': 'permisos-laborales'}

    if permiso:
        datos['permiso'] = permiso
        datos['editar'] = True

    return datos
