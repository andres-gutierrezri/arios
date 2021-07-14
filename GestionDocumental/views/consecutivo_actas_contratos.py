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
from TalentoHumano.models import Colaborador
from TalentoHumano.models.colaboradores import ColaboradorProceso
from Administracion.models import ConsecutivoDocumento, TipoDocumento
from Proyectos.models import Contrato
from enum import Enum



class ConsecutivoActasContratosView(AbstractEvaLoggedView):
    def get(self, request, id):

        consecutivos = ConsecutivoActasContratos.objects.filter(usuario_crea_id=request.user.id,
                                                                    empresa_id=get_id_empresa_global(request),
                                                                    tipo_acta=id)

        opciones_filtro = [{'campo_valor': 0, 'campo_texto': 'Acta de suspención'},
                           {'campo_valor': 1, 'campo_texto': 'Acta de reinicio'},
                           {'campo_valor': 2, 'campo_texto': 'Acta de ampliación de la suspensión'}]

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

        tipo_acta = request.POST.get('tipo_acta_id', '')

        return render(request, 'GestionDocumental/ConsecutivoActasContratos/index.html', {
            'consecutivos': consecutivos,
            'opciones_filtro': opciones_filtro,
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

def datos_xa_render(request, consecutivo: ConsecutivoActasContratos = None) -> dict:

    conseccontrato = ConsecutivoContrato.objects.filter(estado=True).values('id', 'codigo')
    lista_consecutivos = []

    for consecutivo_contrato in conseccontrato:
        lista_consecutivos.append({'campo_valor': consecutivo_contrato['id'], 'campo_texto': '{0}'
                               .format(consecutivo_contrato['codigo'])})

    tipo_acta= [{'campo_valor': 0, 'campo_texto': 'Acta de suspención'},
                       {'campo_valor': 1, 'campo_texto': 'Acta de reinicio'},
                       {'campo_valor': 2, 'campo_texto': 'Acta de ampliación de la suspensión'}]

    datos = {'fecha': datetime.datetime.now(),
             'lista_consecutivos': lista_consecutivos,
             'menu_actual': 'consecutivos-actas-contratos',
             'tipo_acta': tipo_acta}

    if consecutivo:
        print(consecutivo)
        datos['consecutivo'] = consecutivo
        datos['editar'] = True

    return datos
