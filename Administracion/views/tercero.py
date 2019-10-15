from datetime import datetime
from sqlite3 import IntegrityError

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from Administracion.models import Tercero, TipoIdentificacion, TipoTercero, CentroPoblado, Empresa


def tercero_view(request):
    terceros = Tercero.objects.all()
    fecha = datetime.now()
    return render(request, 'Tercero/index.html', {'terceros': terceros, 'fecha': fecha})


class TerceroCrearView(View):
    def get(self, request):
        tipo_identificacion = TipoIdentificacion.objects.all()
        tipo_terceros = TipoTercero.objects.all()
        centros_poblados=CentroPoblado.objects.all()
        empresas = Empresa.objects.all()
        return render(request, 'Tercero/crear.html', {'tipo_identificacion': tipo_identificacion,
                                                      'tipo_terceros': tipo_terceros,
                                                      'centros_poblados': centros_poblados, 'empresas': empresas})

    def post(self, request):

        nombre = request.POST.get('nombre', '')
        identificacion = request.POST.get('identificacion', '')
        tipo_identificacion = request.POST.get('tipo_identificacion_id', '')
        empresa = request.POST.get('empresa_id', '')
        fecha_creacion = request.POST.get('fecha_creacion', '')
        fecha_modificacion = request.POST.get('fecha_modificacion', '')
        terceros = request.POST.get('terceros', '')
        tipo_tercero = request.POST.get('tipo_tercero_id', '')
        centro_poblado = request.POST.get('centro_poblado_id', '')
        tercero = Tercero(nombre=nombre, identificacion=identificacion, tipo_identificacion_id=tipo_identificacion,
                          estado=True, empresa_id=empresa, fecha_modificacion=fecha_modificacion, terceros=terceros,
                          tipo_tercero_id=tipo_tercero, centro_poblado_id=centro_poblado, fecha_creacion=fecha_creacion)
        tercero.save()

        # if error:
        #     error = 'Ya existe un tercero con ese nombre'
        #     tipo_identificacion = TipoIdentificacion.objects.all()
        #     return render(request, 'Tercero/crear.html', {'tipo_identificacion': tipo_identificacion,
        #                                                   'tercero': tercero})

        return redirect(reverse('Administracion:tercero'))


class TerceroEditarView(View):
    def get(self, request, id):
        tercero = Tercero.objects.get(id=id)
        empresas = Empresa.objects.filter(estado=True).order_by('nombre')
        tipo_identificaciones = TipoIdentificacion.objects.filter(estado=True).order_by('nombre')
        tipo_terceros = TipoTercero.objects.filter(estado=True).order_by('nombre')
        centro_poblados = CentroPoblado.objects.all().order_by('nombre')
        return render(request, 'Tercero/editar.html', {'tercero': tercero, 'empresas': empresas,
                                                       'tipo_identificaciones': tipo_identificaciones,
                                                       'tipo_terceros': tipo_terceros,
                                                       'centro_poblados': centro_poblados})

    def post(self, request, id):
        update_fields = ['nombre', 'identificacion', 'tipo_identificacion_id', 'estado', 'empresa_id', 'fecha_creacion',
                         'fecha_modificacion', 'terceros', 'tipo_tercero_id', 'centro_poblado_id']
        tercero = Tercero(id=id)
        tercero.nombre = request.POST.get('nombre', '')
        tercero.identificacion = request.POST.get('identificacion', '')
        tercero.tipo_identificacion_id = request.POST.get('tipo_identificacion_id', '')
        tercero.estado = request.POST.get('estado', 'False') == 'True'
        tercero.empresa_id = request.POST.get('empresa_id', '')
        tercero.fecha_creacion = request.POST.get('fecha_creacion', '')
        tercero.fecha_modificacion = request.POST.get('fecha_modificacion', '')
        tercero.terceros = request.POST.get('terceros', '')
        tercero.tipo_tercero_id = request.POST.get('tipo_tercero_id', '')
        tercero.centro_poblado_id = request.POST.get('centro_poblado_id', '')
        tercero.save(update_fields=update_fields)

        return redirect(reverse('Administracion:tercero'))


@method_decorator(csrf_exempt, name='dispatch')
class TerceroEliminarView(View):
    def post(self, request, id):
        try:
            Tercero.objects.filter(id=id).delete()

            return JsonResponse({"Mensaje": "OK"})
        except IntegrityError:
            return JsonResponse({"Mensaje": "No se puede eliminar"})

