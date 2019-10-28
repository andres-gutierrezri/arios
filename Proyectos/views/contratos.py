from datetime import datetime

from django.db import IntegrityError
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib import messages
from django.http import JsonResponse


from Proyectos.models.contratos import Contrato
from Administracion.models.models import Empresa, TipoContrato
from Administracion.models import Tercero


class ContratoView(View):
    def get(self, request):
        contratos = Contrato.objects.all()
        fecha = datetime.now()
        return render(request, 'Proyectos/Contrato/index.html', {'contratos': contratos, 'fecha': fecha})


class ContratoCrearView(View):
    def get(self, request):
        tipo_contratos = TipoContrato.objects.all()
        empresas = Empresa.objects.all()
        terceros = Tercero.objects.all()
        rango_anho = range(2000, 2051)
        return render(request, 'Proyectos/Contrato/crear.html', {'tipo_contratos': tipo_contratos,
                                                                 'empresas': empresas, 'terceros': terceros,
                                                                 'rango_anho': rango_anho})

    def post(self, request):

        numero_contrato = request.POST.get('numero_contrato', '')
        cliente = int((request.POST.get('cliente_id', '0')))
        anho = int(request.POST.get('rango_anho', '0'))
        supervisor_nombre = request.POST.get('supervisor_nombre', '')
        supervisor_telefono = request.POST.get('supervisor_telefono', '')
        supervisor_correo = request.POST.get('supervisor_correo', '')
        residente = request.POST.get('residente', '')
        fecha_inicio = request.POST.get('fecha_inicio', '')
        fecha_terminacion = request.POST.get('fecha_terminacion', '')
        valor = request.POST.get('valor', '')
        periocidad_informes = request.POST.get('periocidad_informes', '')
        tiempo = request.POST.get('tiempo', '')
        tipo_contrato = int((request.POST.get('tipo_contrato_id', '0')))
        empresa = int((request.POST.get('empresa_id', '0')))

        contrato = Contrato(numero_contrato=numero_contrato, cliente_id=cliente, anho=anho,
                            supervisor_nombre=supervisor_nombre, supervisor_telefono=supervisor_telefono,
                            supervisor_correo=supervisor_correo, residente=residente, fecha_inicio=fecha_inicio,
                            fecha_terminacion=fecha_terminacion, valor=valor, periocidad_informes=periocidad_informes,
                            tiempo=tiempo, tipo_contrato_id=tipo_contrato, empresa_id=empresa)

        if Contrato.objects.filter(numero_contrato=numero_contrato):
            messages.warning(request, 'Ya existe un contrato con número {0}'.format(numero_contrato))
            tipo_contratos = TipoContrato.objects.all()
            empresas = Empresa.objects.all()
            terceros = Tercero.objects.all()
            rango_anho = range(2000, 2051)
            return render(request, 'Proyectos/Contrato/crear.html', {'contrato': contrato,
                                                                         'tipo_contratos': tipo_contratos,
                                                                         'empresas': empresas,
                                                                         'terceros': terceros,
                                                                         'rango_anho': rango_anho})

        fecha_1 = datetime.strptime(contrato.fecha_inicio, "%Y-%m-%d")
        fecha_2 = datetime.strptime(contrato.fecha_terminacion, "%Y-%m-%d")

        if fecha_1 > fecha_2:
            messages.warning(request, 'La fecha de inicio debe ser menor a la fecha de terminación')
            tipo_contratos = TipoContrato.objects.all()
            empresas = Empresa.objects.all()
            terceros = Tercero.objects.all()
            rango_anho = range(2000, 2051)
            return render(request, 'Proyectos/Contrato/crear.html', {'contrato': contrato,
                                                                     'tipo_contratos': tipo_contratos,
                                                                     'empresas': empresas,
                                                                     'terceros': terceros,
                                                                     'rango_anho': rango_anho})
        contrato.save()
        messages.success(request, 'Se ha agregado el contrato número {0}'.format(numero_contrato))

        return redirect(reverse('proyectos:contratos'))


class ContratoEditarView(View):
    def get(self, request, id):
        contrato = Contrato.objects.get(id=id)
        tipo_contratos = TipoContrato.objects.all().order_by('nombre')
        empresas = Empresa.objects.all().order_by('nombre')
        terceros = Tercero.objects.all().order_by('nombre')
        rango_anho = range(2000, 2051)

        return render(request, 'Proyectos/Contrato/editar.html', {'contrato': contrato,
                                                                         'tipo_contratos': tipo_contratos,
                                                                         'empresas': empresas,
                                                                         'terceros': terceros,
                                                                         'rango_anho': rango_anho})

    def post(self, request, id):
        update_fields = ['numero_contrato', 'cliente_id', 'anho', 'supervisor_nombre', 'supervisor_correo',
                         'supervisor_telefono', 'residente', 'fecha_inicio', 'fecha_terminacion', 'valor',
                         'periocidad_informes', 'tiempo', 'tipo_contrato_id', 'empresa_id']

        contrato = Contrato(id=id)
        contrato.numero_contrato = request.POST.get('numero_contrato', '')
        contrato.cliente_id = int(request.POST.get('cliente_id', ''))
        contrato.anho = int(request.POST.get('rango_anho', ''))
        contrato.supervisor_nombre = request.POST.get('supervisor_nombre', '')
        contrato.supervisor_correo = request.POST.get('supervisor_correo', '')
        contrato.supervisor_telefono = request.POST.get('supervisor_telefono', '')
        contrato.residente = request.POST.get('residente', '')
        contrato.fecha_inicio = datetime.strptime(request.POST.get('fecha_inicio', ''), "%Y-%m-%d")
        contrato.fecha_terminacion = datetime.strptime(request.POST.get('fecha_terminacion', ''), "%Y-%m-%d")
        contrato.valor = request.POST.get('valor', '')
        contrato.periocidad_informes = request.POST.get('periocidad_informes', '')
        contrato.tiempo = request.POST.get('tiempo', '')
        contrato.tipo_contrato_id = int(request.POST.get('tipo_contrato_id', ''))
        contrato.empresa_id = int(request.POST.get('empresa_id', ''))

        if Contrato.objects.filter(numero_contrato=contrato.numero_contrato).exclude(id=id):
            messages.warning(request, 'Ya existe un contrato con número {0}'.format(contrato.numero_contrato))
            tipo_contratos = TipoContrato.objects.all()
            empresas = Empresa.objects.all()
            terceros = Tercero.objects.all()
            rango_anho = range(2000, 2051)
            return render(request, 'Proyectos/Contrato/editar.html', {'contrato': contrato,
                                                                         'tipo_contratos': tipo_contratos,
                                                                         'empresas': empresas,
                                                                         'terceros': terceros,
                                                                         'rango_anho': rango_anho})

        if contrato.fecha_inicio > contrato.fecha_terminacion:
            messages.warning(request, 'La fecha de inicio debe ser menor a la fecha de terminación')
            tipo_contratos = TipoContrato.objects.all()
            empresas = Empresa.objects.all()
            terceros = Tercero.objects.all()
            rango_anho = range(2000, 2051)
            return render(request, 'Proyectos/Contrato/editar.html', {'contrato': contrato,
                                                                     'tipo_contratos': tipo_contratos,
                                                                     'empresas': empresas,
                                                                     'terceros': terceros,
                                                                     'rango_anho': rango_anho})

        contrato.save(update_fields=update_fields)
        messages.success(request, 'Se ha actualizado el contrato número {0}'.format(contrato.numero_contrato))

        return redirect(reverse('Proyectos:contratos'))


class ContratoEliminarView(View):
    def post(self, request, id):
        try:
            contrato = Contrato.objects.get(id=id)
            contrato.delete()
            messages.success(request, 'Se ha eliminado el contrato {0}'.format(contrato.numero_contrato))
            return JsonResponse({"Mensaje": "OK"})

        except IntegrityError:
            return JsonResponse({"Mensaje": "No se puede eliminar"})
