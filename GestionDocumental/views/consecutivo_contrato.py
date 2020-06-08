import datetime

from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse

from Administracion.models import TipoContrato, TipoDocumento, ConsecutivoDocumento, Tercero
from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from GestionDocumental.models.models import ConsecutivoContrato
from TalentoHumano.models import Colaborador


class ConsecutivoContratoView(AbstractEvaLoggedView):
    def get(self, request, id):
        if id == 0:
            consecutivos = ConsecutivoContrato.objects.all()
        else:
            consecutivos = ConsecutivoContrato.objects.filter(tipo_contrato_id=id)

        return render(request, 'GestionDocumental/ConsecutivoContratos/index.html',
                      {'consecutivos': consecutivos,
                       'tipo_contratos': tipos_contrato_filtro,
                       'id_tipo_contrato': id,
                       'fecha': datetime.datetime.now(),
                       'menu_actual': 'consecutivos-contrato'})


class ConsecutivoContratoCrearView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'GestionDocumental/ConsecutivoContratos/crear.html', datos_xa_render(request))

    def post(self, request):
        consecutivo = ConsecutivoContrato.from_dictionary(request.POST)
        consecutivo.numero_contrato = ConsecutivoDocumento\
            .get_consecutivo_por_anho(tipo_documento_id=TipoDocumento.CONTRATOS,
                                      empresa_id=get_id_empresa_global(request))
        sigla = TipoContrato.objects.get(id=consecutivo.tipo_contrato_id).sigla
        consecutivo.codigo = 'CTO_{0}_{1}'.format(consecutivo.numero_contrato, sigla)

        consecutivo.save()
        messages.success(request, 'Se ha creado el consecutivo {0}'.format(consecutivo.codigo))
        return redirect(reverse('GestionDocumental:consecutivo-contratos-index', args=[0]))


def datos_xa_render(request) -> dict:
    tipo_contratos = TipoContrato.objects.get_xa_select_activos().exclude(id=0)
    colaboradores = Colaborador.objects.get_xa_select_usuarios_activos()
    terceros = Tercero.objects.get_xa_select_activos()
    tipos_terminacion = [{'campo_valor': 1, 'campo_texto': 'Contrato Laboral a Terminación Definida'},
                         {'campo_valor': 2, 'campo_texto': 'Contrato Laboral a Terminación Indefinida'},
                         {'campo_valor': 3, 'campo_texto': 'Contrato con Entidad a Terminación Definida'},
                         {'campo_valor': 4, 'campo_texto': 'Contrato con Entidad a Terminación Indefinida'}]

    datos = {'fecha': datetime.datetime.now(),
             'tipo_terminacion': request.POST.get('tipo_terminacion', ''),
             'colaboradores': colaboradores,
             'terceros': terceros,
             'tipo_contratos': tipo_contratos,
             'tipos_terminacion': tipos_terminacion,
             'menu_actual': 'consecutivos-contrato'}

    return datos


def tipos_contrato_filtro():
    tipo_contratos = TipoContrato.objects.filter(estado=True)
    lista_tipo_contratos = [{'campo_valor': 0, 'campo_texto': 'Todos'}]
    for tipo_contrato in tipo_contratos:
        lista_tipo_contratos.append({'campo_valor': tipo_contrato.id, 'campo_texto': tipo_contrato.nombre})
    return lista_tipo_contratos
