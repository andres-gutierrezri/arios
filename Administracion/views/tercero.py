from datetime import datetime
from sqlite3 import IntegrityError

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from Administracion.models import Tercero, TipoIdentificacion, TipoTercero, CentroPoblado, Empresa, Departamento, \
    Municipio


def tercero_view(request):
    terceros = Tercero.objects.all()
    fecha = datetime.now()
    return render(request, 'Administracion/Tercero/index.html', {'terceros': terceros, 'fecha': fecha})


def principal_view(request):
    return render(request, 'Administracion/index.html')


class TerceroCrearView(View):
    def get(self, request):
        tipo_identificacion = TipoIdentificacion.objects.all()
        tipo_terceros = TipoTercero.objects.all()
        departamentos = Departamento.objects.all().order_by('nombre')
        empresas = Empresa.objects.all()
        opcion = 'crear'
        return render(request, 'Administracion/Tercero/crear-editar.html', {'tipo_identificacion': tipo_identificacion,
                                                                            'tipo_terceros': tipo_terceros,
                                                                            'departamentos': departamentos,
                                                                            'empresas': empresas,
                                                                            'opcion': opcion})

    def post(self, request):

        nombre = request.POST.get('nombre', '')
        identificacion = request.POST.get('identificacion', '')
        tipo_identificacion = int(request.POST.get('tipo_identificacion_id', '0'))
        empresa = int(request.POST.get('empresa_id', '0'))
        tipo_tercero = int(request.POST.get('tipo_tercero_id', '0'))
        centro_poblado = int(request.POST.get('centro_poblado_id', '0'))
        tercero = Tercero(nombre=nombre, identificacion=identificacion, tipo_identificacion_id=tipo_identificacion,
                          estado=True, empresa_id=empresa,
                          tipo_tercero_id=tipo_tercero, centro_poblado_id=centro_poblado)

        if Tercero.objects.filter(identificacion=identificacion):
            messages.warning(request, 'Ya existe un tercero con identificación {0}'.format(identificacion))
            tipo_identificacion = TipoIdentificacion.objects.all()
            tipo_terceros = TipoTercero.objects.all()
            departamentos = Departamento.objects.all().order_by('nombre')
            empresas = Empresa.objects.all()
            municipios = Municipio.objects.all().order_by('nombre')
            c_poblados = CentroPoblado.objects.all().order_by('nombre')
            return render(request, 'Administracion/Tercero/crear-editar.html',
                          {'tercero': tercero,
                           'tipo_identificacion': tipo_identificacion,
                           'tipo_terceros': tipo_terceros,
                           'departamentos': departamentos,
                           'empresas': empresas,
                           'municipios': municipios,
                           'c_poblados': c_poblados})

        tercero.save()
        messages.success(request, 'Se ha agregado el tercero {0}'.format(nombre))

        return redirect(reverse('Administracion:terceros'))


class TerceroEditarView(View):
    def get(self, request, id):
        tercero = Tercero.objects.get(id=id)
        empresas = Empresa.objects.filter(estado=True).order_by('nombre')
        tipo_identificaciones = TipoIdentificacion.objects.filter(estado=True).order_by('nombre')
        tipo_terceros = TipoTercero.objects.filter(estado=True).order_by('nombre')
        departamentos = Departamento.objects.all().order_by('nombre')
        municipios = Municipio.objects.filter(departamento_id=tercero.centro_poblado.municipio.departamento_id)\
            .order_by('nombre')
        c_poblados = CentroPoblado.objects.filter(municipio_id=tercero.centro_poblado.municipio_id).order_by('nombre')
        opcion = 'editar'
        return render(request, 'Administracion/Tercero/crear-editar.html',
                      {'tercero': tercero, 'empresas': empresas,
                       'tipo_identificaciones': tipo_identificaciones,
                       'tipo_terceros': tipo_terceros,
                       'departamentos': departamentos,
                       'municipios': municipios,
                       'c_poblados': c_poblados,
                       'opcion': opcion})

    def post(self, request, id):
        update_fields = ['nombre', 'identificacion', 'tipo_identificacion_id', 'estado', 'empresa_id',
                         'fecha_modificacion', 'tipo_tercero_id', 'centro_poblado_id']

        tercero = Tercero(id=id)
        tercero.nombre = request.POST.get('nombre', '')
        tercero.identificacion = request.POST.get('identificacion', '')
        tercero.tipo_identificacion_id = int(request.POST.get('tipo_identificacion_id', ''))
        tercero.estado = request.POST.get('estado', 'False') == 'True'
        tercero.empresa_id = int(request.POST.get('empresa_id', '0'))
        tercero.fecha_modificacion = datetime.now()
        tercero.tipo_tercero_id = int(request.POST.get('tipo_tercero_id', '0'))
        tercero.centro_poblado_id = int(request.POST.get('centro_poblado_id', '0'))

        if Tercero.objects.filter(identificacion=tercero.identificacion).exclude(id=id):

            messages.warning(request, 'Ya existe un tercero con identificación {0}'.format(tercero.identificacion))
            tercero = Tercero.objects.get(id=id)
            empresas = Empresa.objects.filter(estado=True).order_by('nombre')
            tipo_identificaciones = TipoIdentificacion.objects.filter(estado=True).order_by('nombre')
            tipo_terceros = TipoTercero.objects.filter(estado=True).order_by('nombre')
            departamentos = Departamento.objects.all().order_by('nombre')
            municipios = Municipio.objects.filter(departamento_id=tercero.centro_poblado.municipio.departamento_id)\
                .order_by('nombre')
            c_poblados = CentroPoblado.objects.filter(municipio_id=tercero.centro_poblado.municipio_id)\
                .order_by('nombre')
            return render(request, 'Administracion/Tercero/crear-editar.html.html',
                          {'tercero': tercero, 'empresas': empresas,
                           'tipo_identificaciones': tipo_identificaciones,
                           'tipo_terceros': tipo_terceros,
                           'departamentos': departamentos,
                           'municipios': municipios,
                           'c_poblados': c_poblados})

        elif Tercero.objects.filter(nombre=tercero.nombre, identificacion=tercero.identificacion,
                                    tipo_identificacion_id=tercero.tipo_identificacion_id, estado=tercero.estado,
                                    empresa_id=tercero.empresa_id, tipo_tercero_id=tercero.tipo_tercero_id,
                                    centro_poblado_id=tercero.centro_poblado_id):

            messages.success(request, 'No se hicieron cambios en el tercero {0}'.format(tercero.nombre))
            return redirect(reverse('Administracion:terceros'))

        else:

            tercero.save(update_fields=update_fields)
            messages.success(request, 'Se ha actualizado el tercero {0}'.format(tercero.nombre)
                             + ' con identificación {0}'.format(tercero.identificacion))

            return redirect(reverse('Administracion:terceros'))


class TerceroEliminarView(View):
    def post(self, request, id):
        try:
            tercero = Tercero.objects.get(id=id)
            tercero.delete()
            messages.success(request, 'Se ha eliminado el tercero {0}'.format(tercero.nombre))
            return JsonResponse({"Mensaje": "OK"})

        except IntegrityError:
            return JsonResponse({"Mensaje": "No se puede eliminar"})




