from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse

from Administracion.models import TipoIdentificacion, Pais, Tercero, Departamento, Municipio
from EVA.views.index import AbstractEvaLoggedProveedorView


class PerfilProveedorView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        opciones = [{'id': 1, 'nombre': 'Información Básica', 'url': '/administracion/proveedor/perfil/informacion-basica'}]
        return render(request, 'Administracion/Tercero/Proveedor/perfil.html',
                      {'opciones': opciones})


class PerfilInformacionBasicaView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        return render(request, 'Administracion/Tercero/Proveedor/informacion_basica.html',
                      datos_xa_render_informacion_basica(request))

    def post(self, request):
        update_fields = ('nombre', 'tipo_identificacion_id', 'identificacion', 'ciudad', 'nombre_rl',
                         'tipo_identificacion_rl', 'identificacion_rl', 'lugar_expedicion_rl', 'telefono_fijo_principal',
                         'telefono_movil_principal', 'telefono_fijo_auxiliar', 'telefono_movil_auxiliar',
                         'correo_principal', 'correo_auxiliar', 'fecha_inicio_actividad', 'fecha_constitucion')

        proveedor = Tercero.objects.get(usuario=request.user)

        proveedor.nombre = request.POST.get('nombre', '')
        proveedor.tipo_identificacion_id = request.POST.get('tipo_identificacion', '')
        proveedor.identificacion = request.POST.get('nit', '')
        proveedor.ciudad_id = request.POST.get('municipio', '')

        proveedor.nombre_rl = request.POST.get('nombre_rl', '')
        proveedor.tipo_identificacion_rl_id = request.POST.get('tipo_identificacion_rl', '')
        proveedor.identificacion_rl = request.POST.get('identificacion_rl', '')
        proveedor.lugar_expedicion_rl_id = request.POST.get('municipio_rl', '')

        proveedor.telefono_fijo_principal = request.POST.get('fijo_principal', '')
        proveedor.telefono_movil_principal = request.POST.get('movil_principal', '')
        proveedor.telefono_fijo_auxiliar = request.POST.get('fijo_auxiliar', '')
        proveedor.telefono_movil_auxiliar = request.POST.get('movil_auxiliar', '')
        proveedor.correo_principal = request.POST.get('correo_pincipal', '')
        proveedor.correo_auxiliar = request.POST.get('correo_auxiliar', '')

        proveedor.fecha_inicio_actividad = request.POST.get('fecha_inicio_actividad', '')
        proveedor.fecha_constitucion = request.POST.get('fecha_constitucion', '')

        if not proveedor.fecha_inicio_actividad:
            proveedor.fecha_inicio_actividad = None

        if not proveedor.fecha_constitucion:
            proveedor.fecha_constitucion = None

        try:
            proveedor.save(update_fields=update_fields)
            messages.success(self.request, 'Se ha guardado la información básica correctamente.')
            return redirect(reverse('Administracion:proveedor-perfil'))
        except:
            messages.error(self.request, 'Ha ocurrido un error al actualizar la información.')
            return redirect(reverse('Administracion:proveedor-perfil'))


def datos_xa_render_informacion_basica(request):
    tipo_identificacion = TipoIdentificacion.objects.get_xa_select_activos()
    tipo_identificacion_personas = TipoIdentificacion.objects.get_xa_select_personas_activos()
    json_tipo_identificacion = TipoIdentificacion.objects.get_activos_like_json()
    paises = Pais.objects.get_xa_select_activos()
    proveedor = Tercero.objects.get(usuario=request.user)

    departamentos = ''
    municipios = ''
    departamentos_rl = ''
    municipios_rl = ''

    if proveedor.ciudad:
        departamentos = Departamento.objects.get_xa_select_activos().filter(pais=proveedor.ciudad.departamento.pais)
        municipios = Municipio.objects.get_xa_select_activos().filter(departamento=proveedor.ciudad.departamento)
    if proveedor.lugar_expedicion_rl:
        departamentos_rl = Departamento.objects.get_xa_select_activos() \
            .filter(pais=proveedor.lugar_expedicion_rl.departamento.pais)
        municipios_rl = Municipio.objects.get_xa_select_activos() \
            .filter(departamento=proveedor.lugar_expedicion_rl.departamento)

    datos = {'tipo_identificacion': tipo_identificacion, 'tipo_identificacion_personas': tipo_identificacion_personas,
             'json_tipo_identificacion': json_tipo_identificacion, 'paises': paises, 'proveedor': proveedor,
             'departamentos': departamentos, 'municipios': municipios, 'departamentos_rl': departamentos_rl,
             'municipios_rl': municipios_rl}
    return datos
