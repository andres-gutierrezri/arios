import datetime
import json
import logging

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.transaction import atomic, rollback
from django.shortcuts import render, redirect
from django.urls import reverse
from EVA.General.modeljson import RespuestaJson
from Administracion.models import ConsecutivoDocumento, TipoDocumento
from Administracion.utils import get_id_empresa_global
from EVA.General.utilidades import paginar, app_datetime_now
from EVA.views.index import AbstractEvaLoggedView
from GestionDocumental.models.models import ConsecutivoReunion
from TalentoHumano.models import Colaborador

LOGGER = logging.getLogger(__name__)

class ConsecutivoReunionView(AbstractEvaLoggedView):
    def get(self, request, id):
        if id == 0:
            consecutivos = ConsecutivoReunion.objects.filter(empresa_id=get_id_empresa_global(request))
            colaborador = Colaborador.objects.values('usuario_crea_id')
        else:
            colaborador = Colaborador.objects.filter(usuario=request.user).values('usuario_crea_id')
            consecutivos = ConsecutivoReunion.objects.filter(usuario_crea_id=request.user.id,
                                                             empresa_id=get_id_empresa_global(request))

        opciones_filtro = [{'campo_valor': 0, 'campo_texto': 'Todos'},
                           {'campo_valor': 1, 'campo_texto': 'Mis consecutivos'}]

        page = request.GET.get('page', 1)
        search = request.GET.get('search', '')
        total = len(consecutivos)

        if search:
            consecutivos = consecutivos.filter(Q(codigo__icontains=search) |
                                               Q(fecha__icontains=search))
        coincidencias = len(consecutivos)
        consecutivos = paginar(consecutivos.order_by('-id'), page, 10)
        return render(request, 'GestionDocumental/ConsecutivosReuniones/index.html',
                      {'consecutivos': consecutivos,
                       'opciones_filtro': opciones_filtro,
                       'colaborador': colaborador,
                       'fecha': datetime.datetime.now(),
                       'buscar': search,
                       'coincidencias': coincidencias,
                       'total': total,
                       'menu_actual': 'consecutivos-reunion',
                       'id_filtro': id})


class ConsecutivoReunionesCrearView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'GestionDocumental/ConsecutivosReuniones/modal_crear_editar_reuniones.html',
                      {'fecha': datetime.datetime.now(),
                       'menu_actual': 'consecutivos-reunion'})

    def post(self, request):
        consecutivo = ConsecutivoReunion.from_dictionary(request.POST, request)
        consecutivo.usuario_crea = request.user
        consecutivo.empresa_id = get_id_empresa_global(request)

        try:
            consecutivo.full_clean(exclude=['consecutivo', 'codigo'])
        except ValidationError as errores:
            return RespuestaJson.error('Falló generación del consecutivo. '
                                       'Valide los datos ingresados al editar el consecutivo')
        try:
            with atomic():
                consecutivo.consecutivo = ConsecutivoDocumento\
                    .get_consecutivo_documento(tipo_documento_id=TipoDocumento.REUNIONES,
                                               empresa_id=get_id_empresa_global(request))
                consecutivo.actualizar_codigo()
                consecutivo.save()
                messages.success(request, 'Se ha creado el consecutivo <br> {0}'.format(consecutivo.codigo))
                return redirect(reverse('GestionDocumental:consecutivo-reuniones-index', args=[0]))
        except:
            rollback()
            LOGGER.exception('Falló la generación del consecutivo de reunión.')
            return RespuestaJson.error('Ha ocurrido un error al crear el consecutivo.')


class ConsecutivoReunionesEditarView(AbstractEvaLoggedView):
    def get(self, request, id_reunion):
        consecutivo = ConsecutivoReunion.objects.get(id=id_reunion)

        return render(request, 'GestionDocumental/ConsecutivosReuniones/modal_crear_editar_reuniones.html',
                      datos_xa_render(request, consecutivo))

    def post(self, request, id_reunion):
        update_fields = ['fecha', 'fecha_modificacion',
                         'tema', 'codigo', 'descripcion', 'justificacion']

        consecutivo = ConsecutivoReunion.from_dictionary(request.POST, request, True)
        consecutivo_db = ConsecutivoReunion.objects.get(id=id_reunion)

        consecutivo.fecha_creacion = consecutivo_db.fecha_creacion
        consecutivo.id = consecutivo_db.id
        consecutivo.consecutivo = consecutivo_db.consecutivo
        consecutivo.empresa = consecutivo_db.empresa
        consecutivo.usuario_modifica = request.user

        consecutivo.actualizar_codigo(consecutivo_db.consecutivo)
        try:
            consecutivo.full_clean(validate_unique=False, exclude=['usuario_crea'])
        except ValidationError as errores:
            messages.error(request, 'Falló editar. Valide los datos ingresados al editar el consecutivo')
            return redirect(reverse('GestionDocumental:consecutivo-reuniones-index', args=[0]))

        if consecutivo_db.comparar(consecutivo, excluir=['usuario_crea', 'fecha_creacion', 'fecha_modificacion',
                                                         'usuario_modifica', 'justificacion']):
            messages.error(request, 'No se hicieron cambios en el consecutivo {0}'.format(consecutivo.codigo))
            return redirect(reverse('GestionDocumental:consecutivo-reuniones-index', args=[0]))
        else:
            try:
                with atomic():
                    consecutivo.save(update_fields=update_fields)
                    messages.success(request, 'Se ha editado el consecutivo {0}'.format(consecutivo.codigo))
                    return redirect(reverse('GestionDocumental:consecutivo-reuniones-index', args=[0]))
            except:
                rollback()
                LOGGER.exception('Falló la edición del consecutivo de requerimiento interno.')
            RespuestaJson.error('Falló la edición del consecutivo de requerimiento interno.')


class ConsecutivoReunionesEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        consecutivo = ConsecutivoReunion.objects.get(id=id)
        body_unicode = request.body.decode('utf-8')
        datos_registro = json.loads(body_unicode)

        justificacion = datos_registro['justificacion']
        if not consecutivo.estado:
            return RespuestaJson.error("Este consecutivo ya ha sido anulado.")
        try:
            with atomic():
                consecutivo.estado = False
                consecutivo.justificacion = justificacion
                consecutivo.usuario_modifica = request.user
                consecutivo.fecha_modificacion = app_datetime_now()
                consecutivo.save(update_fields=['estado', 'justificacion', 'fecha_modificacion', 'usuario_modifica'])
                messages.success(request, 'Consecutivo {0} anulado'.format(consecutivo.codigo))
                return RespuestaJson.exitosa()
        except:
            rollback()
            LOGGER.exception('Error anulando el consecutivo de reunión')
            return RespuestaJson.error('Ha ocurrido un error al realizar la acción')


def datos_xa_render(request, consecutivo: ConsecutivoReunion = None) -> dict:
    if consecutivo:
        datos = {}
        datos['consecutivo'] = consecutivo
        datos['editar'] = True

    return datos
