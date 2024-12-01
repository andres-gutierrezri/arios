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
from GestionDocumental.models.models import ConsecutivoPlanTrabajo
from TalentoHumano.models import Colaborador
from TalentoHumano.models.colaboradores import ColaboradorProceso
from Administracion.models import ConsecutivoDocumento, TipoDocumento
from Proyectos.models import Contrato

LOGGER = logging.getLogger(__name__)

class ConsecutivoPlanTrabajoView(AbstractEvaLoggedView):
    def get(self, request, id):
        if id == 0:
            consecutivos = ConsecutivoPlanTrabajo.objects.filter(empresa_id=get_id_empresa_global(request))
            colaborador = Colaborador.objects.values('usuario_id')
        else:
            colaborador = Colaborador.objects.filter(usuario=request.user).values('usuario_id')
            consecutivos = ConsecutivoPlanTrabajo.objects.filter(usuario_crea_id=request.user.id,
                                                            empresa_id=get_id_empresa_global(request))

        opciones_filtro = [{'campo_valor': 0, 'campo_texto': 'Todos'},
                           {'campo_valor': 1, 'campo_texto': 'Mis consecutivos'}]

        page = request.GET.get('page', 1)
        search = request.GET.get('search', '')
        total = len(consecutivos)

        if search:
            consecutivos = consecutivos.filter(Q(codigo__icontains=search) |
                                               Q(fecha_creacion__icontains=search) |
                                               Q(contrato__numero_contrato__icontains=search) |
                                               Q(contrato__cliente__nombre__icontains=search) |
                                               Q(descripcion__icontains=search) |
                                               Q(justificacion__icontains=search) |
                                               Q(usuario_crea__username__icontains=search))
        coincidencias = len(consecutivos)
        consecutivos = paginar(consecutivos.order_by('-id'), page, 10)

        return render(request, 'GestionDocumental/ConsecutivoPlanTrabajo/index.html', {'consecutivos': consecutivos,
                                                                                   'opciones_filtro': opciones_filtro,
                                                                                   'colaborador': colaborador,
                                                                                   'fecha': datetime.datetime.now(),
                                                                                   'buscar': search,
                                                                                   'coincidencias': coincidencias,
                                                                                   'total': total,
                                                                                   'menu_actual': 'consecutivos-plantrabajo',
                                                                                   'id_filtro': id})


class ConsecutivoPlanTrabajoCrearView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'GestionDocumental/ConsecutivoPlanTrabajo/_modal_crear_editar_consecutivo.html',
                          datos_xa_render(request))

    def post(self, request):
        consecutivo = ConsecutivoPlanTrabajo.from_dictionary(request.POST)
        consecutivo.usuario_crea = request.user
        consecutivo.empresa_id = get_id_empresa_global(request)
        try:
            consecutivo.full_clean(exclude=['consecutivo', 'codigo'])
        except ValidationError as errores:
            return RespuestaJson.error('Falló generación del consecutivo. '
                                       'Valide los datos ingresados al editar el consecutivo')

        try:
            with atomic():
                consecutivo.consecutivo = ConsecutivoDocumento.\
                    get_consecutivo_por_anho(tipo_documento_id=TipoDocumento.PLAN_TRABAJO,
                                              empresa_id=get_id_empresa_global(request))
                proceso = request.POST.get('proceso_id', '')
                if proceso:
                    consecutivo.proceso = ColaboradorProceso.objects.get(proceso_id=proceso,
                                                                         colaborador__usuario=request.user).proceso
                else:
                    consecutivo.proceso = ColaboradorProceso.objects.filter(colaborador__usuario=
                                                                            request.user).first().proceso
                    consecutivo.anio = app_datetime_now().year

                if not consecutivo.contrato_id:
                    consecutivo.numero_contrato = consecutivo.proceso.sigla
                else:
                    consecutivo.numero_contrato = consecutivo.contrato.numero_contrato
                    consecutivo.anio = consecutivo.contrato.anho

                consecutivo.actualizar_codigo()
                consecutivo.save()
                messages.success(request, 'Se ha creado el consecutivo {0}'.format(consecutivo.codigo))
                return RespuestaJson.exitosa()
        except:
            rollback()
            LOGGER.exception('Falló la generación del consecutivo de actas de contrato.')
            return RespuestaJson.error('Ha ocurrido un error al crear el consecutivo.')


class ConsecutivoPlanTrabajoEditarView(AbstractEvaLoggedView):
    def get(self, request, id):
        consecutivo = ConsecutivoPlanTrabajo.objects.get(id=id)
        return render(request, 'GestionDocumental/ConsecutivoPlanTrabajo/_modal_crear_editar_consecutivo.html',
                      datos_xa_render(request, consecutivo))

    def post(self, request, id):
        update_fields = ['fecha_modificacion', 'contrato_id', 'codigo', 'descripcion',
                         'justificacion', 'usuario_modifica']

        consecutivo = ConsecutivoPlanTrabajo.from_dictionary(request.POST)
        consecutivo_db = ConsecutivoPlanTrabajo.objects.get(id=id)

        consecutivo.fecha_creacion = consecutivo_db.fecha_creacion
        consecutivo.id = consecutivo_db.id
        consecutivo.consecutivo = consecutivo_db.consecutivo
        consecutivo.empresa = consecutivo_db.empresa
        consecutivo.usuario_modifica = request.user

        proceso = request.POST.get('proceso_id', '')

        if proceso:
            consecutivo.proceso = ColaboradorProceso.objects.get(proceso_id=proceso,
                                                                 colaborador__usuario=request.user).proceso
        else:
            consecutivo.proceso = ColaboradorProceso.objects.filter(colaborador__usuario=
                                                                    request.user).first().proceso
            consecutivo.anio = app_datetime_now().year

        if not consecutivo.contrato_id:
            consecutivo.numero_contrato = consecutivo.proceso.sigla
        else:
            consecutivo.numero_contrato = consecutivo.contrato.numero_contrato
            consecutivo.anio = consecutivo.contrato.anho

        consecutivo.actualizar_codigo(consecutivo_db.consecutivo)

        try:
            consecutivo.full_clean(validate_unique=False, exclude=['usuario_crea'])
        except ValidationError as errores:
            return RespuestaJson.error(mensaje="Falló editar. Valide los datos ingresados al editar el consecutivo")

        if consecutivo_db.comparar(consecutivo, excluir=['usuario_crea', 'fecha_creacion', 'fecha_modificacion',
                                                         'usuario_modifica', 'justificacion']):
            return RespuestaJson.error("No se hicieron cambios en la consecutivo")
        else:
            try:
                with atomic():
                    consecutivo.save(update_fields=update_fields)
                    messages.success(request, 'Se ha editado el consecutivo {0}'.format(consecutivo.codigo))
                    return RespuestaJson.exitosa()
            except:
                rollback()
                LOGGER.exception('Falló la edición del consecutivo de plan de trabajo.')
                RespuestaJson.error('Falló la edición del consecutivo de plan de trabajo.')


class ConsecutivoPlanTrabajoEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        consecutivo = ConsecutivoPlanTrabajo.objects.get(id=id)
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
            LOGGER.exception('Error anulando el consecutivo de requerimiento interno')
            return RespuestaJson.error('Ha ocurrido un error al realizar la acción')


def datos_xa_render(request, consecutivo: ConsecutivoPlanTrabajo = None) -> dict:
    contratos = Contrato.objects \
                .filter(empresa_id=get_id_empresa_global(request)) \
                .values('id', 'numero_contrato', 'cliente__nombre')
    lista_contratos = []
    for contrato in contratos:
        lista_contratos.append({'campo_valor': contrato['id'], 'campo_texto': '{0} - {1}'
                                .format(contrato['numero_contrato'], contrato['cliente__nombre'])})

    procesos = ColaboradorProceso.objects.filter(colaborador__usuario=request.user)
    lista_procesos = []
    if procesos.count() > 1:
        for proceso in procesos:
            lista_procesos.append({'campo_valor': proceso.proceso.id, 'campo_texto': proceso.proceso.nombre})

    datos = {'fecha': datetime.datetime.now(),
             'contratos': lista_contratos,
             'procesos': lista_procesos,
             'lista_procesos': lista_procesos,
             'menu_actual': 'consecutivos-plantrabajo'}

    if consecutivo:
        datos['consecutivo'] = consecutivo
        datos['editar'] = True

    return datos
