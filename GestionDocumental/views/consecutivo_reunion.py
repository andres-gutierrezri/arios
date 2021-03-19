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
from EVA.General.utilidades import paginar, app_datetime_now
from EVA.views.index import AbstractEvaLoggedView
from GestionDocumental.models.models import ConsecutivoReunion
from TalentoHumano.models import Colaborador


class ConsecutivoReunionView(AbstractEvaLoggedView):
    def get(self, request, id):
        if id == 0:
            consecutivos = ConsecutivoReunion.objects.filter(empresa_id=get_id_empresa_global(request))
            colaborador = Colaborador.objects.values('usuario_id')
        else:
            colaborador = Colaborador.objects.filter(usuario=request.user).values('usuario_id')
            consecutivos = ConsecutivoReunion.objects.filter(usuario_id=request.user.id,
                                                             empresa_id=get_id_empresa_global(request))

        opciones_filtro = [{'campo_valor': 0, 'campo_texto': 'Todos'},
                           {'campo_valor': 1, 'campo_texto': 'Mis consecutivos'}]

        page = request.GET.get('page', 1)
        search = request.GET.get('search', '')
        total = len(consecutivos)

        if search:
            consecutivos = consecutivos.filter(Q(codigo__icontains=search) |
                                               Q(fecha__icontains=search))
        coincidencias = len(consecutivos)
        consecutivos = paginar(consecutivos.order_by('-id'), page, 10)
        return render(request, 'GestionDocumental/ConsecutivosReuniones/index.html',
                      {'consecutivos': consecutivos,
                       'opciones_filtro': opciones_filtro,
                       'colaborador': colaborador,
                       'fecha': datetime.datetime.now(),
                       'buscar': search,
                       'coincidencias': coincidencias,
                       'total': total,
                       'menu_actual': 'consecutivos-reunion',
                       'id_filtro': id})


class ConsecutivoReunionesCrearView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'GestionDocumental/ConsecutivosReuniones/crear.html',
                      {'fecha': datetime.datetime.now(),
                       'menu_actual': 'consecutivos-reunion'})

    def post(self, request):
        consecutivo = ConsecutivoReunion.from_dictionary(request.POST)
        consecutivo.usuario = request.user
        consecutivo.fecha_crea = app_datetime_now()
        consecutivo.empresa_id = get_id_empresa_global(request)

        dato_consecutivo = ConsecutivoDocumento\
            .get_consecutivo_documento(tipo_documento_id=TipoDocumento.REUNIONES,
                                       empresa_id=get_id_empresa_global(request))
        anio_actual = str(datetime.datetime.now().year)
        consecutivo.codigo = 'ACR-{0:03d}-{1}{2}'.format(dato_consecutivo, anio_actual[2], anio_actual[3])

        consecutivo.save()
        messages.success(request, 'Se ha creado el consecutivo <br> {0}'.format(consecutivo.codigo))
        return redirect(reverse('GestionDocumental:consecutivo-reuniones-index', args=[1]))


class ConsecutivoReunionesEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        consecutivo = ConsecutivoReunion.objects.get(id=id)
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
                                 "mensaje": 'Ha ocurrido un error al realizar la acción'})
