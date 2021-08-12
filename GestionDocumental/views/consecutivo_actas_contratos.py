import datetime
import json
import logging

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.transaction import atomic, rollback
from django.shortcuts import render
from Administracion.utils import get_id_empresa_global
from EVA.General.modeljson import RespuestaJson
from EVA.General.utilidades import paginar, app_datetime_now
from EVA.views.index import AbstractEvaLoggedView
from GestionDocumental.models.models import ConsecutivoActasContratos, ConsecutivoContrato
from Administracion.models import ConsecutivoDocumento, TipoDocumento
from GestionDocumental.Enumeraciones import TiposActas

LOGGER = logging.getLogger(__name__)


class ConsecutivoActasContratosView(AbstractEvaLoggedView):
    def get(self, request, id):

        if id == 0:
            consecutivos = ConsecutivoActasContratos.objects.filter(usuario_crea_id=request.user.id,
                                                                empresa_id=get_id_empresa_global(request))
        else:
            consecutivos = ConsecutivoActasContratos.objects.filter(usuario_crea_id=request.user.id,
                                                                empresa_id=get_id_empresa_global(request),
                                                                tipo_acta=id)

        page = request.GET.get('page', 1)
        search = request.GET.get('search', '')
        total = len(consecutivos)

        if search:
            consecutivos = consecutivos.filter(Q(codigo__icontains=search) |
                                               Q(fecha_creacion__icontains=search) |
                                               Q(descripcion__icontains=search) |
                                               Q(justificacion__icontains=search) |
                                               Q(usuario_crea__username__icontains=search) |
                                               Q(fecha_reinicio__icontains=search) |
                                               Q(fecha_suspension__icontains=search))
        coincidencias = len(consecutivos)
        consecutivos = paginar(consecutivos.order_by('-id'), page, 10)

        return render(request, 'GestionDocumental/ConsecutivoActasContratos/index.html', {
            'consecutivos': consecutivos,
            'opciones_filtro': TiposActas.choices,
            'fecha': datetime.datetime.now(),
            'buscar': search,
            'coincidencias': coincidencias,
            'total': total,
            'menu_actual': 'consecutivos-actas-contratos',
            'id_filtro': id,
            'editar': False})


class ConsecutivoActasContratosCrearView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'GestionDocumental/ConsecutivoActasContratos/_modal_crear_editar_consecutivo.html',
                      datos_xa_render(request))

    def post(self, request):
        consecutivo = ConsecutivoActasContratos.from_dictionary(request.POST)
        consecutivo.usuario_crea = request.user
        consecutivo.empresa_id = get_id_empresa_global(request)
        try:
            consecutivo.full_clean(exclude=['consecutivo', 'codigo'])
        except ValidationError as errores:
            return RespuestaJson.error('Falló generación del consecutivo. '
                                       'Valide los datos ingresados al editar el consecutivo')
        try:
            with atomic():
                consecutivo.consecutivo = ConsecutivoDocumento. \
                    get_consecutivo_por_anho(tipo_documento_id=TipoDocumento.ACTAS_CONTRATOS,
                                             empresa_id=get_id_empresa_global(request))
                consecutivo.actualizar_codigo()
                consecutivo.save()
                messages.success(request, 'Se ha creado el consecutivo {0}'.format(consecutivo.codigo))
                return RespuestaJson.exitosa()
        except:
            rollback()
            LOGGER.exception('Falló la generación del consecutivo de actas de contrato.')
            return RespuestaJson.error('Ha ocurrido un error al crear el consecutivo.')


class ConsecutivoActasContratosEditarView(AbstractEvaLoggedView):
    def get(self, request, id):
        consecutivo = ConsecutivoActasContratos.objects.get(id=id)
        return render(request, 'GestionDocumental/ConsecutivoActasContratos/_modal_crear_editar_consecutivo.html',
                      datos_xa_render(request, consecutivo))

    def post(self, request, id):
        update_fields = ['tipo_acta', 'consecutivo_contrato_id', 'usuario_modifica', 'fecha_suspension',
                         'fecha_reinicio', 'justificacion', 'fecha_modificacion', 'descripcion', 'codigo']

        consecutivo = ConsecutivoActasContratos.from_dictionary(request.POST)
        consecutivo_db = ConsecutivoActasContratos.objects.get(id=id)

        consecutivo.id = consecutivo_db.id
        consecutivo.codigo = consecutivo_db.codigo
        consecutivo.consecutivo = consecutivo_db.consecutivo
        consecutivo.usuario_modifica = request.user
        consecutivo.empresa_id = get_id_empresa_global(request)
        consecutivo.fecha_modificacion = app_datetime_now()

        try:
            consecutivo.full_clean(validate_unique=False, exclude=['usuario_crea'])
        except ValidationError as errores:
            return RespuestaJson.error('Falló editar. Valide los datos ingresados al editar el consecutivo')

        consecutivo.actualizar_codigo(consecutivo_db.consecutivo)

        if consecutivo_db.comparar(consecutivo, excluir=['usuario_crea', 'fecha_creacion', 'fecha_modificacion',
                                                         'usuario_modifica', 'justificacion']):
            return RespuestaJson.error('No se hicieron cambios en la consecutivo')
        else:
            try:
                with atomic():
                    consecutivo.save(update_fields=update_fields)
                    messages.success(request, 'Se ha editado el consecutivo {0}'.format(consecutivo.codigo))
                    return RespuestaJson.exitosa()
            except:
                rollback()
                LOGGER.exception('Falló la edición del consecutivo de actas de contrato.')
                RespuestaJson.error('Falló la edición del consecutivo de actas de contrato.')


class ConsecutivoActasContratosEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        consecutivo = ConsecutivoActasContratos.objects.get(id=id)
        body_unicode = request.body.decode('utf-8')
        datos_registro = json.loads(body_unicode)
        justificacion = datos_registro['justificacion']

        if not consecutivo.estado:
            return RespuestaJson.error(mensaje="Este consecutivo ya ha sido anulado.")
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
            LOGGER.exception('Error anulando el consecutivo de actas de contratos')
            return RespuestaJson.error('Ha ocurrido un error al realizar la acción')


def datos_xa_render(request, consecutivo: ConsecutivoActasContratos = None) -> dict:

    conseccontrato = ConsecutivoContrato.objects.filter(estado=True).values('id', 'codigo')
    lista_consecutivos = []
    tipos_actas = []

    for consecutivo_contrato in conseccontrato:
        lista_consecutivos.append({'campo_valor': consecutivo_contrato['id'], 'campo_texto': '{0}'
                                  .format(consecutivo_contrato['codigo'])})
        tipos_actas = TiposActas.choices
        del tipos_actas[0]

    datos = {'fecha': datetime.datetime.now(),
             'lista_consecutivos': lista_consecutivos,
             'menu_actual': 'consecutivos-actas-contratos',
             'tipo_acta': tipos_actas}

    if consecutivo:
        datos['consecutivo'] = consecutivo
        datos['editar'] = True

    return datos
