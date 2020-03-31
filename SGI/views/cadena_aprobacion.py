from datetime import datetime

from django.db import IntegrityError
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError

from Administracion.models import Tercero, TipoIdentificacion, TipoTercero, CentroPoblado, Empresa, Departamento, \
    Municipio
from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from Notificaciones.models.models import EventoDesencadenador
from Notificaciones.views.views import crear_notificacion_por_evento
from SGI.models import CadenaAprobacionEncabezado


class CadenaAprobacionView(AbstractEvaLoggedView):
    def get(self, request):
        cadenas_aprobacion = CadenaAprobacionEncabezado.objects.all()
        fecha = datetime.now()
        return render(request, 'SGI/CadenasAprobacion/index.html', {'cadenas_aprobacion': cadenas_aprobacion,
                                                                    'fecha': fecha,
                                                                    'menu_actual': 'cadenas_aprobacion'})
