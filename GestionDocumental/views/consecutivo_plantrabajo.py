import datetime
import json
from sqlite3 import IntegrityError

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
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


class ConsecutivoPlanTrabajoView(AbstractEvaLoggedView):
    def get(self, request, id):
        if id == 0:
            consecutivos = ConsecutivoPlanTrabajo.objects.filter(empresa_id=get_id_empresa_global(request))
            colaborador = Colaborador.objects.values('usuario_id')
        else:
            colaborador = Colaborador.objects.filter(usuario=request.user).values('usuario_id')
            consecutivos = ConsecutivoPlanTrabajo.objects.filter(usuario_id=request.user.id,
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
        consecutivo.consecutivo = ConsecutivoDocumento.\
            get_consecutivo_por_anho(tipo_documento_id=TipoDocumento.PLAN_TRABAJO,
                                      empresa_id=get_id_empresa_global(request))
        proceso = request.POST.get('proceso_id', '')
        if proceso:
            proceso = ColaboradorProceso.objects.get(proceso_id=proceso, colaborador__usuario=request.user).proceso
        else:
            proceso = ColaboradorProceso.objects.filter(colaborador__usuario=request.user).first().proceso
            anio = str(app_datetime_now().year)[2:4]

        if not consecutivo.contrato_id:
            contrato = proceso.sigla
        else:
            contrato = consecutivo.contrato.numero_contrato
            anio = str(consecutivo.contrato.anho).upper()[2:4]

        consecutivo.codigo = 'PT-{0:03d}-{1}-{2}'.format(consecutivo.consecutivo,
                                                             contrato, anio)
        try:
            consecutivo.save()
        except:
            return RespuestaJson.error("Ha ocurrido un error al guardar la información")
        messages.success(request, 'Se ha creado el consecutivo {0}'.format(consecutivo.codigo))
        return RespuestaJson.exitosa()


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
            proceso = ColaboradorProceso.objects.get(proceso_id=proceso, colaborador__usuario=request.user).proceso
        else:
            proceso = ColaboradorProceso.objects.filter(colaborador__usuario=request.user).first().proceso
            anio = str(app_datetime_now().year)[2:4]

        if not consecutivo.contrato_id:
            contrato = proceso.sigla
        else:
            contrato = consecutivo.contrato.numero_contrato
            anio = str(consecutivo.contrato.anho).upper()[2:4]

        consecutivo.codigo = 'PT-{0:03d}-{1}-{2}'.format(consecutivo_db.consecutivo, contrato, anio)

        try:
            consecutivo.full_clean(validate_unique=False, exclude=['usuario_crea'])
        except ValidationError as errores:
            return RespuestaJson.error(mensaje="Falló editar. Valide los datos ingresados al editar el consecutivo")

        if consecutivo_db.comparar(consecutivo, excluir=['usuario_crea', 'fecha_crea', 'fecha_modificacion',
                                                         'usuario_modifica', 'justificacion']):
            return RespuestaJson.error("No se hicieron cambios en la consecutivo")
        else:
            consecutivo.save(update_fields=update_fields)
            messages.success(request, 'Se ha editado el consecutivo {0}'.format(consecutivo.codigo))
            return RespuestaJson.exitosa()

