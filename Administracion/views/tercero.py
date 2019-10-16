from datetime import datetime
from sqlite3 import IntegrityError

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from Administracion.models import Tercero, TipoIdentificacion, TipoTercero, CentroPoblado, Empresa, Departamento


def tercero_view(request):
    terceros = Tercero.objects.all()
    fecha = datetime.now()
    return render(request, 'Administracion/Tercero/index.html', {'terceros': terceros, 'fecha': fecha})


def principal_view(request):
    return render(request, 'Administracion/Tercero/principal.html')


class TerceroCrearView(View):
    def get(self, request):
        tipo_identificacion = TipoIdentificacion.objects.all()
        tipo_terceros = TipoTercero.objects.all()
        departamentos = Departamento.objects.all().order_by('nombre')
        empresas = Empresa.objects.all()
        return render(request, 'Administracion/Tercero/crear.html', {'tipo_identificacion': tipo_identificacion,
                                                      'tipo_terceros': tipo_terceros,
                                                      'departamentos': departamentos,
                                                      'empresas': empresas})

    def post(self, request):

        nombre = request.POST.get('nombre', '')
        identificacion = request.POST.get('identificacion', '')
        tipo_identificacion = request.POST.get('tipo_identificacion_id', '')
        empresa = request.POST.get('empresa_id', '')
        # fecha_creacion = request.POST.get('fecha_creacion', '')
        # fecha_modificacion = request.POST.get('fecha_modificacion', '')
        tipo_tercero = request.POST.get('tipo_tercero_id', '')
        centro_poblado = request.POST.get('centro_poblado_id', '')
        tercero = Tercero(nombre=nombre, identificacion=identificacion, tipo_identificacion_id=tipo_identificacion,
                          estado=True, empresa_id=empresa,
                          tipo_tercero_id=tipo_tercero, centro_poblado_id=centro_poblado)
        fecha = datetime.today()
        tercero.save()

        return redirect(reverse('Administracion:terceros'))


class TerceroEditarView(View):
    def get(self, request, id):
        tercero = Tercero.objects.get(id=id)
        empresas = Empresa.objects.filter(estado=True).order_by('nombre')
        tipo_identificaciones = TipoIdentificacion.objects.filter(estado=True).order_by('nombre')
        tipo_terceros = TipoTercero.objects.filter(estado=True).order_by('nombre')
        departamentos = Departamento.objects.all().order_by('nombre')
        return render(request, 'Administracion/Tercero/editar.html', {'tercero': tercero, 'empresas': empresas,
                                                       'tipo_identificaciones': tipo_identificaciones,
                                                       'tipo_terceros': tipo_terceros,
                                                       'departamentos': departamentos})

    def post(self, request, id):
        update_fields = ['nombre', 'identificacion', 'tipo_identificacion_id', 'estado', 'empresa_id',
                         'fecha_modificacion', 'tipo_tercero_id', 'centro_poblado_id']
        tercero = Tercero(id=id)
        tercero.nombre = request.POST.get('nombre', '')
        tercero.identificacion = request.POST.get('identificacion', '')
        tercero.tipo_identificacion_id = request.POST.get('tipo_identificacion_id', '')
        tercero.estado = request.POST.get('estado', 'False') == 'True'
        tercero.empresa_id = request.POST.get('empresa_id', '')
        # tercero.fecha_creacion = request.POST.get('fecha_creacion', '')
        tercero.fecha_modificacion = datetime.today()
        tercero.tipo_tercero_id = request.POST.get('tipo_tercero_id', '')
        tercero.centro_poblado_id = request.POST.get('centro_poblado_id', '')
        tercero.save(update_fields=update_fields)

        return redirect(reverse('Administracion:terceros'))


@method_decorator(csrf_exempt, name='dispatch')
class TerceroEliminarView(View):
    def post(self, request, id):
        try:
            Tercero.objects.filter(id=id).delete()

            return JsonResponse({"Mensaje": "OK"})
        except IntegrityError:
            return JsonResponse({"Mensaje": "No se puede eliminar"})

