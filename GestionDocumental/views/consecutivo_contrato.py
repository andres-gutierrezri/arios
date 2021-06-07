import datetime
import json
import os
from sqlite3 import IntegrityError

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_sameorigin

from Administracion.models import TipoContrato, TipoDocumento, ConsecutivoDocumento, Tercero
from Administracion.utils import get_id_empresa_global
from EVA.General.utilidades import paginar, app_datetime_now
from EVA.views.index import AbstractEvaLoggedView
from GestionDocumental.models.models import ConsecutivoContrato
from TalentoHumano.models import Colaborador


class ConsecutivoContratoView(AbstractEvaLoggedView):
    def get(self, request, id):
        if id == 0:
            consecutivos = ConsecutivoContrato.objects.filter(empresa_id=get_id_empresa_global(request))
        else:
            consecutivos = ConsecutivoContrato.objects.filter(tipo_contrato_id=id,
                                                              empresa_id=get_id_empresa_global(request))
        page = request.GET.get('page', 1)
        search = request.GET.get('search', '')
        total = len(consecutivos)
        if search:
            consecutivos = consecutivos.filter(Q(codigo__icontains=search) |
                                               Q(usuario__first_name__icontains=search) |
                                               Q(usuario__last_name__icontains=search) |
                                               Q(tercero__nombre__icontains=search) |
                                               Q(fecha_inicio__icontains=search) |
                                               Q(fecha_final__icontains=search) |
                                               Q(fecha_crea__icontains=search) |
                                               Q(justificacion__icontains=search) |
                                               Q(tipo_contrato__nombre__icontains=search)
                                               )

        coincidencias = len(consecutivos)
        consecutivos = paginar(consecutivos.order_by('-id'), page, 10)
        return render(request, 'GestionDocumental/ConsecutivoContratos/index.html',
                      {'consecutivos': consecutivos,
                       'tipo_contratos': tipos_contrato_filtro,
                       'id_tipo_contrato': id,
                       'fecha': datetime.datetime.now(),
                       'buscar': search,
                       'coincidencias': coincidencias,
                       'total': total,
                       'menu_actual': 'consecutivos-contrato'})


class ConsecutivoContratoCrearView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'GestionDocumental/ConsecutivoContratos/_modal_crear_editar_consecutivo.html', datos_xa_render(request))

    def post(self, request):
        consecutivo = ConsecutivoContrato.from_dictionary(request.POST)
        consecutivo.empresa_id = get_id_empresa_global(request)
        consecutivo.numero_contrato = ConsecutivoDocumento\
            .get_consecutivo_por_anho(tipo_documento_id=TipoDocumento.CONTRATOS,
                                      empresa_id=get_id_empresa_global(request))
        sigla = TipoContrato.objects.get(id=consecutivo.tipo_contrato_id).sigla
        consecutivo.codigo = 'CTO_{0:03d}_{1}_{2}'.format(consecutivo.numero_contrato, sigla, app_datetime_now().year)
        consecutivo.usuario_crea = request.user
        consecutivo.save()
        messages.success(request, 'Se ha creado el consecutivo {0}'.format(consecutivo.codigo))
        return redirect(reverse('GestionDocumental:consecutivo-contratos-index', args=[0]))


class ConsecutivoContratoEditarView(AbstractEvaLoggedView):
    def get(self, request, id_contrato):
        return render(request, 'GestionDocumental/ConsecutivoContratos/_modal_crear_editar_consecutivo.html',
                      datos_xa_render_editar(request, id_contrato))

    def post(self, request, id_contrato):
        update_fields = ['fecha_inicio', 'fecha_final', 'codigo', 'tercero_id',
                         'tipo_contrato_id', 'usuario_id', 'justificacion']
        consecutivo = ConsecutivoContrato.from_dictionary(request.POST)
        consecutivo_db = ConsecutivoContrato.objects.get(id=id_contrato)

        consecutivo.id = consecutivo_db.id
        consecutivo.ruta_archivo = consecutivo_db.ruta_archivo
        consecutivo.numero_contrato = consecutivo_db.numero_contrato
        consecutivo.usuario_crea = consecutivo_db.usuario_crea
        consecutivo.empresa = consecutivo_db.empresa
        sigla = TipoContrato.objects.get(id=consecutivo.tipo_contrato_id).sigla
        consecutivo.codigo = 'CTO_{0:03d}_{1}_{2}'.format(consecutivo.numero_contrato, sigla, app_datetime_now().year)

        try:
            consecutivo.full_clean(validate_unique=False)
        except ValidationError as errores:
            messages.error(request, 'Falló editar. Valide los datos ingresados al editar el consecutivo')
            return redirect(reverse('GestionDocumental:consecutivo-contratos-index', args=[0]))

        if consecutivo_db.comparar(consecutivo, excluir=['fecha_modificacion', 'ruta_archivo']):
            messages.success(request, 'No se hicieron cambios en la consecutivo {0}'.format(consecutivo.codigo))
            return redirect(reverse('GestionDocumental:consecutivo-contratos-index', args=[0]))
        else:
            consecutivo.save(update_fields=update_fields)
            messages.success(request, 'Se ha editado el consecutivo {0}'.format(consecutivo.codigo))
            return redirect(reverse('GestionDocumental:consecutivo-contratos-index', args=[0]))


class ConsecutivoContratoEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        consecutivo = ConsecutivoContrato.objects.get(id=id)
        body_unicode = request.body.decode('utf-8')
        datos_registro = json.loads(body_unicode)

        justificacion = datos_registro['justificacion']
        if not consecutivo.estado:
            return JsonResponse({"estado": "error",
                                 "mensaje": 'Este consecutivo ya ha sido eliminado.'})
        try:
            consecutivo.estado = False
            consecutivo.justificacion = justificacion
            consecutivo.save(update_fields=['estado', 'justificacion'])
            messages.success(request, 'Se ha eliminado el consecutivo {0}'.format(consecutivo.codigo))
            return JsonResponse({"estado": "OK"})

        except IntegrityError:
            return JsonResponse({"estado": "error",
                                 "mensaje": 'Ha ocurrido un erro al realizar la acción'})


class ArchivoCargarView(AbstractEvaLoggedView):

    def get(self, request, id_contrato):
        consecutivo = ConsecutivoContrato.objects.get(id=id_contrato)
        return render(request, 'GestionDocumental/ConsecutivoContratos/_modal_cargar_contrato.html', {'contrato': consecutivo})

    def post(self, request, id_contrato):
        consecutivo = ConsecutivoContrato.objects.get(id=id_contrato)

        consecutivo.ruta_archivo = request.FILES.get('archivo', None)
        
        consecutivo.save(update_fields=['ruta_archivo'])
        messages.success(request, 'Se cagó archivo del consecutivo:  {0}'.format(consecutivo.codigo))
        return redirect(reverse('GestionDocumental:consecutivo-contratos-index', args=[0]))


class VerArchivoView(AbstractEvaLoggedView):
    @xframe_options_sameorigin
    def get(self, request, id_contrato):
        consecutivo = ConsecutivoContrato.objects.get(id=id_contrato)
        if consecutivo.ruta_archivo:
            extension = os.path.splitext(consecutivo.ruta_archivo.url)[1]
            mime_types = {'.docx': 'application/msword', '.xlsx': 'application/vnd.ms-excel',
                          '.pptx': 'application/vnd.ms-powerpoint',
                          '.xlsm': 'application/vnd.ms-excel.sheet.macroenabled.12',
                          '.dwg': 'application/octet-stream'
                          }

            mime_type = mime_types.get(extension, 'application/pdf')

            response = HttpResponse(consecutivo.ruta_archivo, content_type=mime_type)
            response['Content-Disposition'] = 'inline; filename="{0}{1}"' \
                .format(consecutivo.codigo, extension)
        else:
            response = redirect(reverse('GestionDocumental:consecutivo-contratos-index', args=[0]))
        return response


def datos_xa_render(request) -> dict:
    tipo_contratos = TipoContrato.objects
    colaboradores = Colaborador.objects.get_xa_select_usuarios_activos_x_empresa(request)
    terceros = Tercero.objects.get_xa_select_activos()
    extra_tipos_contrato = []
    for tipo_contrato in tipo_contratos.all():
        extra_tipos_contrato.append({'id': tipo_contrato.id, 'laboral': tipo_contrato.laboral,
                                     'fecha_fin': tipo_contrato.tiene_fecha_fin})

    datos = {'fecha': datetime.datetime.now(),
             'tipo_terminacion': request.POST.get('tipo_terminacion', ''),
             'colaboradores': colaboradores,
             'terceros': terceros,
             'tipo_contratos': tipo_contratos.get_xa_select_activos().exclude(id=0),
             'extra_tipos_contrato': json.dumps(extra_tipos_contrato),
             'menu_actual': 'consecutivos-contrato'}

    return datos


def datos_xa_render_editar(request, id_contrato) -> dict:
    consecutivo = ConsecutivoContrato.objects.get(id=id_contrato)
    tipo_contratos = TipoContrato.objects
    colaboradores = Colaborador.objects.get_xa_select_usuarios_activos_x_empresa(request)
    terceros = Tercero.objects.get_xa_select_activos()
    extra_tipos_contrato = []
    for tipo_contrato in tipo_contratos.all():
        extra_tipos_contrato.append({'id': tipo_contrato.id, 'laboral': tipo_contrato.laboral,
                                     'fecha_fin': tipo_contrato.tiene_fecha_fin})

    datos = {'fecha': datetime.datetime.now(),
             'tipo_terminacion': request.POST.get('tipo_terminacion', ''),
             'colaboradores': colaboradores,
             'terceros': terceros,
             'tipo_contratos': tipo_contratos.get_xa_select_activos().exclude(id=0),
             'motivo':consecutivo.justificacion,
             'extra_tipos_contrato': json.dumps(extra_tipos_contrato),
             'contrato_actual': id_contrato,
             'menu_actual': 'consecutivos-contrato',
             'colaborador_actual': consecutivo.usuario_id,
             'tercero_actual': consecutivo.tercero_id,
             'tipo_contrato_actual': consecutivo.tipo_contrato_id,
             'fecha_inicial':consecutivo.fecha_inicio,
             'fecha_final':consecutivo.fecha_final,
             'tipo_contrato_actu': consecutivo.tipo_contrato,
             'editar':True
             }

    return datos


def tipos_contrato_filtro():
    tipo_contratos = TipoContrato.objects.filter(estado=True)
    lista_tipo_contratos = [{'campo_valor': 0, 'campo_texto': 'Todos'}]
    for tipo_contrato in tipo_contratos:
        lista_tipo_contratos.append({'campo_valor': tipo_contrato.id, 'campo_texto': tipo_contrato.nombre})
    return lista_tipo_contratos

