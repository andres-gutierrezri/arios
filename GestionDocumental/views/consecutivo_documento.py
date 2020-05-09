import datetime

from django.shortcuts import render, redirect
from django.urls import reverse

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
                                                                                   'menu_actual': 'consecutivos',
                                                                                   'id_filtro': id})


class ConsecutivoOficiosCrearView(AbstractEvaLoggedView):
    def get(self, request):
        contratos = Contrato.objects.get_xa_select_activos()
        return render(request, 'GestionDocumental/ConsecutivoOficios/crear.html', {'fecha': datetime.datetime.now(),
                                                                                   'contratos': contratos,
                                                                                   'menu_actual': 'consecutivos'})

    def post(self, request):
        consecutivo = ConsecutivoOficio.from_dictionary(request.POST)
        consecutivo.usuario = request.user
        anterior_consecutivo = ConsecutivoOficio.objects.last()
        if anterior_consecutivo:
            if anterior_consecutivo.fecha.year < datetime.datetime.now().year:
                consecutivo.consecutivo = 1
            else:
                consecutivo.consecutivo = anterior_consecutivo.consecutivo + 1
        else:
            consecutivo.consecutivo = 1

        colaborador = Colaborador.objects.get(usuario=request.user)

        if not consecutivo.contrato_id:
            contrato = colaborador.proceso.sigla
        else:
            contrato = consecutivo.contrato.numero_contrato

        consecutivo.codigo = '{0}-{1}-{2}-{3}'.format(colaborador.proceso.sigla, consecutivo.consecutivo,
                                                      contrato, datetime.datetime.now().year).upper()

        consecutivo.save()
        return redirect(reverse('GestionDocumental:consecutivo-oficios-index', args=[1]))
