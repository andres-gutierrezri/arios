import datetime

from django.shortcuts import render, redirect
from django.urls import reverse

from Administracion.models import ConsecutivoDocumento, TipoDocumento
from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from GestionDocumental.models import ConsecutivoOficio
from Proyectos.models import Contrato
from TalentoHumano.models import Colaborador


class ConsecutivoOficiosView(AbstractEvaLoggedView):
    def get(self, request, id):
        if id == 0:
            consecutivos = ConsecutivoOficio.objects.all()
            colaborador = Colaborador.objects.values('usuario_id', 'proceso__sigla')
        else:
            colaborador = Colaborador.objects.filter(usuario=request.user).values('usuario_id', 'proceso__sigla')
            consecutivos = ConsecutivoOficio.objects.filter(usuario_id=request.user.id)

        opciones_filtro = [{'campo_valor': 0, 'campo_texto': 'Todos'},
                           {'campo_valor': 1, 'campo_texto': 'Mis consecutivos'}]

        return render(request, 'GestionDocumental/ConsecutivoOficios/index.html', {'consecutivos': consecutivos,
                                                                                   'opciones_filtro': opciones_filtro,
                                                                                   'colaborador': colaborador,
                                                                                   'fecha': datetime.datetime.now(),
                                                                                   'menu_actual': 'consecutivos-oficios',
                                                                                   'id_filtro': id})


class ConsecutivoOficiosCrearView(AbstractEvaLoggedView):
    def get(self, request):
        contratos = Contrato.objects.values('id', 'numero_contrato', 'cliente__nombre')
        lista_contratos = []
        for contrato in contratos:
            lista_contratos.append({'campo_valor': contrato['id'], 'campo_texto': '{0} - {1}'
                                   .format(contrato['numero_contrato'], contrato['cliente__nombre'])})

        return render(request, 'GestionDocumental/ConsecutivoOficios/crear.html', {'fecha': datetime.datetime.now(),
                                                                                   'contratos': lista_contratos,
                                                                                   'menu_actual': 'consecutivos-oficios'})

    def post(self, request):
        consecutivo = ConsecutivoOficio.from_dictionary(request.POST)
        consecutivo.usuario = request.user
        consecutivo.consecutivo = ConsecutivoDocumento\
            .get_consecutivo_por_anho(tipo_documento_id=TipoDocumento.OFICIOS,
                                      empresa_id=get_id_empresa_global(request))

        colaborador = Colaborador.objects.get(usuario=request.user)

        if not consecutivo.contrato_id:
            contrato = colaborador.proceso.sigla
        else:
            contrato = consecutivo.contrato.numero_contrato

        consecutivo.codigo = '{0}-{1:03d}-{2}-{3}'.format(colaborador.proceso.sigla, consecutivo.consecutivo,
                                                          contrato, datetime.datetime.now().year).upper()

        consecutivo.save()
        return redirect(reverse('GestionDocumental:consecutivo-oficios-index', args=[1]))
