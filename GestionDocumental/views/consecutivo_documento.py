import datetime
import json
from sqlite3 import IntegrityError

from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from Administracion.models import ConsecutivoDocumento, TipoDocumento
from Administracion.utils import get_id_empresa_global
from EVA.General.utilidades import paginar
from EVA.views.index import AbstractEvaLoggedView
from GestionDocumental.models import ConsecutivoOficio
from Proyectos.models import Contrato
from TalentoHumano.models import Colaborador


class ConsecutivoOficiosView(AbstractEvaLoggedView):
    def get(self, request, id):
        if id == 0:
            consecutivos = ConsecutivoOficio.objects.filter(empresa_id=get_id_empresa_global(request))
            colaborador = Colaborador.objects.values('usuario_id', 'proceso__sigla')
        else:
            colaborador = Colaborador.objects.filter(usuario=request.user).values('usuario_id', 'proceso__sigla')
            consecutivos = ConsecutivoOficio.objects.filter(usuario_id=request.user.id,
                                                            empresa_id=get_id_empresa_global(request))

        opciones_filtro = [{'campo_valor': 0, 'campo_texto': 'Todos'},
                           {'campo_valor': 1, 'campo_texto': 'Mis consecutivos'}]

        page = request.GET.get('page', 1)
        search = request.GET.get('search', '')
        total = len(consecutivos)

        if search:
            consecutivos = consecutivos.filter(Q(codigo__icontains=search) |
                                               Q(fecha__icontains=search) |
                                               Q(contrato__numero_contrato__icontains=search) |
                                               Q(contrato__cliente__nombre__icontains=search) |
                                               Q(detalle__icontains=search) |
                                               Q(destinatario__icontains=search) |
                                               Q(usuario__first_name__icontains=search) |
                                               Q(justificacion__icontains=search) |
                                               Q(usuario__last_name__icontains=search))
        coincidencias = len(consecutivos)
        consecutivos = paginar(consecutivos.order_by('-id'), page, 10)
        return render(request, 'GestionDocumental/ConsecutivoOficios/index.html', {'consecutivos': consecutivos,
                                                                                   'opciones_filtro': opciones_filtro,
                                                                                   'colaborador': colaborador,
                                                                                   'fecha': datetime.datetime.now(),
                                                                                   'buscar': search,
                                                                                   'coincidencias': coincidencias,
                                                                                   'total': total,
                                                                                   'menu_actual': 'consecutivos-oficios',
                                                                                   'id_filtro': id})


class ConsecutivoOficiosCrearView(AbstractEvaLoggedView):
    def get(self, request):
        contratos = Contrato.objects\
            .filter(empresa_id=get_id_empresa_global(request))\
            .values('id', 'numero_contrato', 'cliente__nombre')
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
        consecutivo.empresa_id = get_id_empresa_global(request)
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
        messages.success(request, 'Se ha creado el consecutivo <br> {0}'.format(consecutivo.codigo))
        return redirect(reverse('GestionDocumental:consecutivo-oficios-index', args=[1]))


class ConsecutivoOficiosEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        consecutivo = ConsecutivoOficio.objects.get(id=id)
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
