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
from GestionDocumental.models.models import ConsecutivoActasContratos, ConsecutivoContrato
from Administracion.models import ConsecutivoDocumento, TipoDocumento
from GestionDocumental.Enumeraciones import TiposActas


class ConsecutivoActasContratosView(AbstractEvaLoggedView):
    def get(self, request, id):

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
                                               Q(fecha_reinicio__icontains=search)  |
                                               Q(fecha_suspension__icontains=search))
        coincidencias = len(consecutivos)
        consecutivos = paginar(consecutivos.order_by('-id'), page, 10)

        tipo_acta = request.POST.get('tipo_acta_id', '')

        return render(request, 'GestionDocumental/ConsecutivoActasContratos/index.html', {
            'consecutivos': consecutivos,
            'opciones_filtro': TiposActas.choices,
            'fecha': datetime.datetime.now(),
            'buscar': search,
            'coincidencias': coincidencias,
            'total': total,
            'menu_actual': 'consecutivos-actas-contratos',
            'id_filtro': id,
            'editar':False})


class ConsecutivoActasContratosCrearView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'GestionDocumental/ConsecutivoActasContratos/_modal_crear_editar_consecutivo.html',
                      datos_xa_render(request))

    def post(self, request):
        consecutivo = ConsecutivoActasContratos.from_dictionary(request.POST)
        consecutivo.usuario_crea = request.user
        consecutivo.empresa_id = get_id_empresa_global(request)
        consecutivo.consecutivo = ConsecutivoDocumento. \
            get_consecutivo_por_anho(tipo_documento_id=TipoDocumento.ACTAS_CONTRATOS,
                                     empresa_id=get_id_empresa_global(request))

        consecutivo.contrato = ConsecutivoContrato.objects.filter().values('id')
        if consecutivo.tipo_acta == "0":
            codigo_tipo_acta = "AS"
        elif consecutivo.tipo_acta == "1":
            codigo_tipo_acta = "AR"
        elif consecutivo.tipo_acta == "2":
            codigo_tipo_acta = "AAS"

        consecutivo.codigo = '{0}-{1:03d}-{2}'.format(codigo_tipo_acta, consecutivo.consecutivo,
                                                          app_datetime_now().year)

        try:
            consecutivo.save()
        except:
            return RespuestaJson.error("Ha ocurrido un error al guardar la información")
        messages.success(request, 'Se ha creado el consecutivo {0}'.format(consecutivo.codigo))
        return RespuestaJson.exitosa()


class ConsecutivoActasContratosEditarView(AbstractEvaLoggedView):
    def get(self, request, id):
        consecutivo = ConsecutivoActasContratos.objects.get(id=id)
        return render(request, 'GestionDocumental/ConsecutivoActasContratos/_modal_crear_editar_consecutivo.html',
                      datos_xa_render(request, consecutivo))

    def post(self, request, id):
        update_fields = ['tipo_acta', 'consecutivo_contrato_id', 'usuario_modifica','fecha_suspension',
                         'fecha_reinicio', 'justificacion', 'fecha_modificacion','descripcion', 'codigo']

        consecutivo = ConsecutivoActasContratos.from_dictionary(request.POST)
        consecutivo_db = ConsecutivoActasContratos.objects.get(id=id)

        consecutivo.id = consecutivo_db.id
        consecutivo.codigo = consecutivo_db.codigo
        consecutivo.consecutivo = consecutivo_db.consecutivo
        consecutivo.usuario_modifica = request.user
        consecutivo.empresa_id = get_id_empresa_global(request)
        consecutivo.fecha_modificacion = app_datetime_now()

        if consecutivo.tipo_acta == "0":
            codigo_tipo_acta = "AS"
        elif consecutivo.tipo_acta == "1":
            codigo_tipo_acta = "AR"
        elif consecutivo.tipo_acta == "2":
            codigo_tipo_acta = "AAS"

        consecutivo.codigo = '{0}-{1:03d}-{2}'.format(codigo_tipo_acta, consecutivo_db.consecutivo,
                                                      app_datetime_now().year)

        try:
            consecutivo.full_clean(validate_unique=False, exclude=['usuario_crea'])
        except ValidationError as errores:
            return RespuestaJson.error(mensaje="Falló editar. Valide los datos ingresados al editar el consecutivo")

        if consecutivo_db.comparar(consecutivo, excluir=['usuario_crea', 'fecha_creacion', 'fecha_modificacion',
                                                         'usuario_modifica', 'justificacion']):
            return RespuestaJson.error("No se hicieron cambios en la consecutivo")
        else:
            consecutivo.save(update_fields=update_fields)
            messages.success(request, 'Se ha editado el consecutivo {0}'.format(consecutivo.codigo))
            return RespuestaJson.exitosa()


class ConsecutivoActasContratosEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        consecutivo = ConsecutivoActasContratos.objects.get(id=id)
        body_unicode = request.body.decode('utf-8')
        datos_registro = json.loads(body_unicode)
        justificacion = datos_registro['justificacion']

        if not consecutivo.estado:
            return RespuestaJson.error(mensaje="Este consecutivo ya ha sido anulado.")
        try:
            consecutivo.estado = False
            consecutivo.justificacion = justificacion
            consecutivo.usuario_modifica = request.user
            consecutivo.fecha_modificacion = app_datetime_now();
            consecutivo.save(update_fields=['estado', 'justificacion', 'fecha_modificacion', 'usuario_modifica'])
            messages.success(request, 'Consecutivo {0} anulado'.format(consecutivo.codigo))
            return RespuestaJson.exitosa()
        except IntegrityError:
            return RespuestaJson.error(mensaje="Ha ocurrido un error al realizar la acción")


def datos_xa_render(request, consecutivo: ConsecutivoActasContratos = None) -> dict:

    conseccontrato = ConsecutivoContrato.objects.filter(estado=True).values('id', 'codigo')
    lista_consecutivos = []

    for consecutivo_contrato in conseccontrato:
        lista_consecutivos.append({'campo_valor': consecutivo_contrato['id'], 'campo_texto': '{0}'
                               .format(consecutivo_contrato['codigo'])})

    datos = {'fecha': datetime.datetime.now(),
             'lista_consecutivos': lista_consecutivos,
             'menu_actual': 'consecutivos-actas-contratos',
             'tipo_acta': TiposActas.choices}

    if consecutivo:
        print(consecutivo)
        datos['consecutivo'] = consecutivo
        datos['editar'] = True

    return datos


