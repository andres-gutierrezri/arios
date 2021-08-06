import datetime

from django.shortcuts import render
from EVA.General.utilidades import paginar
from EVA.views.index import AbstractEvaLoggedView
from TalentoHumano.models import PermisoLaboral, TipoPermiso


class PermisosLaboralesIndexView(AbstractEvaLoggedView):
    def get(self, request, id_tipo_permiso):
        if id_tipo_permiso == 0:
            permisos = PermisoLaboral.objects.filter(usuario_crea_id=request.user.id)
        else:
            permisos = PermisoLaboral.objects.filter(tipo_permiso_id=id_tipo_permiso, usuario_crea_id=request.user.id)

        page = request.GET.get('page', 1)
        permisos = paginar(permisos.order_by('-id'), page, 10)
        return render(request, 'TalentoHumano/PermisosLaborales/index.html',
                      {'permisos': permisos,
                       'fecha': datetime.datetime.now(),
                       'tipos_permiso': self.tipos_permiso_filtro(),
                       'id_tipo_permiso': id_tipo_permiso,
                       'menu_actual': 'permisos-laborales'})

    @staticmethod
    def tipos_permiso_filtro() -> list:
        tipos_permiso = TipoPermiso.objects.filter(estado=True)
        lista_tipo_permiso = [{'campo_valor': 0, 'campo_texto': 'Todos'}]
        for tipo_permiso in tipos_permiso:
            lista_tipo_permiso.append({'campo_valor': tipo_permiso.id, 'campo_texto': tipo_permiso.nombre})
        return lista_tipo_permiso


class PermisoLaboralCrearView(AbstractEvaLoggedView):
    def get(self, request):
        return render(request, 'TalentoHumano/PermisosLaborales/_modal_crear_editar_permiso.html', datos_xa_render())


def datos_xa_render(permiso: PermisoLaboral = None) -> dict:
    tipo_permiso = TipoPermiso.objects.get_xa_select_activos()

    datos = {'tipo_permiso': tipo_permiso,
             'fecha': datetime.datetime.now(),
             'menu_actual': 'permisos-laborales'}

    if permiso:
        datos['permiso'] = permiso
        datos['editar'] = True

    return datos
