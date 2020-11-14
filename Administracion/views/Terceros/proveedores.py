from django.shortcuts import render

from Administracion.models import TipoIdentificacion
from EVA.views.index import AbstractEvaLoggedProveedorView


class PerfilProveedorView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        opciones = [{'id': 1, 'nombre': 'Información Básica', 'url': '/administracion/proveedor/perfil/informacion-basica'}]
        return render(request, 'Administracion/Tercero/Proveedor/perfil.html',
                      {'opciones': opciones})


class PerfilInformacionBasicaView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        tipo_identificacion = TipoIdentificacion.objects.get_xa_select_activos()
        tipo_identificacion_personas = TipoIdentificacion.objects.get_xa_select_personas_activos()
        json_tipo_identificacion = TipoIdentificacion.objects.get_activos_like_json()
        return render(request, 'Administracion/Tercero/Proveedor/informacion_basica.html',
                      {'tipo_identificacion': tipo_identificacion,
                       'tipo_identificacion_personas': tipo_identificacion_personas,
                       'json_tipo_identificacion': json_tipo_identificacion})
