from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from Administracion.models import Tercero, TipoIdentificacion, TipoTercero, CentroPoblado, Empresa


def tercero_view(request):
    terceros = Tercero.objects.all()

    return render(request, 'Tercero/index.html', {'terceros': terceros})


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



        return redirect(reverse('Administracion:Tercero'))


