import datetime

from django.shortcuts import render
from EVA.General.utilidades import paginar
from EVA.views.index import AbstractEvaLoggedView
from TalentoHumano.models import PermisoLaboral


class PermisosLaboralesIndexView(AbstractEvaLoggedView):
    def get(self, request):
        permisos = PermisoLaboral.objects.filter(usuario_crea_id=request.user.id)
        page = request.GET.get('page', 1)
        permisos = paginar(permisos.order_by('-id'), page, 10)
        return render(request, 'TalentoHumano/PermisosLaborales/index.html',
                      {'permisos': permisos,
                       'fecha': datetime.datetime.now(),
                       'menu_actual': 'permisos-laborales'})


class PermisoLaboralCrearView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'TalentoHumano/PermisosLaborales/_modal_crear_editar_permiso.html',
                      {'fecha': datetime.datetime.now(),
                       'menu_actual': 'permisos-laborales'})
