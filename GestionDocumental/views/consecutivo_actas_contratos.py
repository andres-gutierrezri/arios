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
from GestionDocumental.models.models import ConsecutivoActasContratos
from TalentoHumano.models import Colaborador
from TalentoHumano.models.colaboradores import ColaboradorProceso
from Administracion.models import ConsecutivoDocumento, TipoDocumento
from Proyectos.models import Contrato


class ConsecutivoActasContratosView(AbstractEvaLoggedView):
    def get(self, request, id):
        if id == 0:
            consecutivos = ConsecutivoActasContratos.objects.filter(empresa_id=get_id_empresa_global(request))
            colaborador = Colaborador.objects.values('usuario_id')
        else:
            colaborador = Colaborador.objects.filter(usuario=request.user).values('usuario_id')
            consecutivos = ConsecutivoActasContratos.objects.filter(usuario_crea_id=request.user.id,
                                                                   empresa_id=get_id_empresa_global(request))

        opciones_filtro = [{'campo_valor': 0, 'campo_texto': 'Todos'},
                           {'campo_valor': 1, 'campo_texto': 'Mis consecutivos'}]

        opciones_actas = [{'campo_valor': 0, 'campo_texto': 'Suspención'},
                           {'campo_valor': 1, 'campo_texto': 'Reinicio'},
                           {'campo_valor': 2, 'campo_texto': 'Ampliación de la suspensión'}]

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

        return render(request, 'GestionDocumental/ConsecutivoActasContratos/index.html', {
            'consecutivos': consecutivos,
            'opciones_filtro': opciones_filtro,
            'opciones_actas': opciones_actas,
            'colaborador': colaborador,
            'fecha': datetime.datetime.now(),
            'buscar': search,
            'coincidencias': coincidencias,
            'total': total,
            'menu_actual': 'consecutivos-actas-contratos',
            'id_filtro': id})
