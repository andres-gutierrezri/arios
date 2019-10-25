from datetime import datetime
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib import messages


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
        terceros = Tercero.objects.filter(tipo_tercero_id=1)
        return render(request, 'Proyectos/Contrato/crear.html', {'tipo_contratos': tipo_contratos,
                                                                 'empresas': empresas, 'terceros': terceros})

    def post(self, request):

        numero_contrato = request.POST.get('numero_contrato', '')
        cliente = int(request.POST.get('cliente_id', '0'))
        anho = request.POST.get('anho', '')
        supervisor_nombre = request.POST.get('supervisor_nombre', '')
        supervisor_telefono = request.POST.get('supervisor_telefono', '')
        supervisor_correo = request.POST.get('supervisor_correo', '')
        residente = request.POST.get('residente', '')
        fecha_inicio = request.POST.get('fecha_inicio', '')
        fecha_terminacion = request.POST.get('fecha_terminacion', '')
        valor = request.POST.get('valor', '')
        periocidad_informes = request.POST.get('periocidad_informes', '')
        tiempo = request.POST.get('tiempo', '')
        tipo_contrato = int(request.POST.get('tipo_contrato_id', '0'))
        empresa = int(request.POST.get('empresa_id', '0'))

        contrato = Contrato(numero_contrato=numero_contrato, cliente=cliente, anho=anho,
                            supervisor_nombre=supervisor_nombre, supervisor_telefono=supervisor_telefono,
                            supervisor_correo=supervisor_correo, residente=residente, fecha_inicio=fecha_inicio,
                            fecha_terminacion=fecha_terminacion, valor=valor, periocidad_informes=periocidad_informes,
                            tiempo=tiempo, tipo_contrato_id=tipo_contrato, empresa_id=empresa)

        contrato.save()
        messages.success(request, 'Se ha agregado el contrato número {0}'.format(numero_contrato))

        return redirect(reverse('Proyectos:contratos'))

