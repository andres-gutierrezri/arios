from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import F

from Proyectos.models.contratos import Contrato
from Administracion.models import Tercero, Empresa, TipoContrato, TipoTercero


class ContratoView(View):
    def get(self, request):
        contratos = Contrato.objects.all()
        fecha = datetime.now()
        return render(request, 'Proyectos/Contrato/index.html', {'contratos': contratos, 'fecha': fecha})


class ContratoCrearView(View):
    def __init__(self):
        self.opcion = 'crear'
        super().__init__()

    def get(self, request):
        return render(request, 'Proyectos/Contrato/crear-editar.html', datos_xa_render(self.opcion))

    def post(self, request):

        contrato = Contrato.from_dictionary(request.POST)
        try:
            contrato.full_clean()
        except ValidationError as errores:
            datos = datos_xa_render(self.opcion, contrato)
            datos['contrato'] = contrato
            datos['errores'] = errores
            return render(request, 'Proyectos/Contrato/crear-editar.html', datos)

        if Contrato.objects.filter(numero_contrato=contrato.numero_contrato).exists():
            messages.warning(request, 'Ya existe un contrato con número {0}'.format(contrato.numero_contrato))
            datos = datos_xa_render(self.opcion, contrato)
            return render(request, 'Proyectos/Contrato/crear-editar.html', datos)

        if Contrato.objects.filter(numero_contrato=contrato.numero_contrato):
            messages.warning(request, 'Ya existe un contrato con número {0}'.format(contrato.numero_contrato))
            return render(request, 'Proyectos/Contrato/crear-editar.html', datos_xa_render(self.opcion, contrato))

        if contrato.fecha_inicio > contrato.fecha_terminacion:
            messages.warning(request, 'La fecha de inicio debe ser menor o igual a la fecha de terminación')
            return render(request, 'Proyectos/Contrato/crear-editar.html', datos_xa_render(self.opcion, contrato))

        contrato.save()
        messages.success(request, 'Se ha agregado el contrato número {0}'.format(contrato.numero_contrato))
        return redirect(reverse('proyectos:contratos'))


class ContratoEditarView(View):
    def __init__(self):
        self.opcion = 'editar'
        super().__init__()

    def get(self, request, id):
        contrato = Contrato.objects.get(id=id)
        return render(request, 'Proyectos/Contrato/crear-editar.html', datos_xa_render(self.opcion, contrato))

    def post(self, request, id):
        update_fields = ['numero_contrato', 'cliente_id', 'anho', 'supervisor_nombre', 'supervisor_correo',
                         'supervisor_telefono', 'residente', 'fecha_inicio', 'fecha_terminacion', 'valor',
                         'periodicidad_informes', 'tiempo', 'tipo_contrato_id', 'empresa_id']

        contrato = Contrato.from_dictionary(request.POST)
        contrato.id = int(id)

        try:
            contrato.full_clean(validate_unique=False)
        except ValidationError as errores:
            datos = datos_xa_render(self.opcion, contrato)
            datos['contrato'] = contrato
            datos['errores'] = errores
            return render(request, 'Proyectos/Contrato/crear-editar.html', datos)

        if Contrato.objects.filter(numero_contrato=contrato.numero_contrato).exclude(id=id).exists():
            messages.warning(request, 'Ya existe un contrato con número {0}'.format(contrato.numero_contrato))
            return render(request, 'Proyectos/Contrato/crear-editar.html', datos_xa_render(self.opcion, contrato))

        if contrato.fecha_inicio > contrato.fecha_terminacion:
            messages.warning(request, 'La fecha de inicio debe ser menor o igual a la fecha de terminación')
            return render(request, 'Proyectos/Contrato/crear-editar.html', datos_xa_render(self.opcion, contrato))

        contrato_db = Contrato.objects.get(id=id)
        if contrato_db.comparar(contrato):
            messages.success(request, 'No se hicieron cambios en el contrato número {0}'
                             .format(contrato.numero_contrato))
            return redirect(reverse('Proyectos:contratos'))
        else:
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


# region Métodos de ayuda
def datos_xa_render(opcion: str, contrato: Contrato = None) -> dict:
    """
    Datos necesarios para la creación de los html de Contratos.
    :param opcion: valor de la acción a realizar 'crea' o 'editar'
    :param contrato: Es opcional si se requiere pre cargar datos.
    :return: Un diccionario con los datos.
    """

    tipo_contratos = TipoContrato.objects.tipos_comerciales(True)\
        .values(campo_valor=F('id'), campo_texto=F('nombre')).order_by('nombre')
    empresas = Empresa.objects.filter(estado=True).values(campo_valor=F('id'), campo_texto=F('nombre')) \
        .order_by('nombre')
    terceros = Tercero.objects.filter(tipo_tercero_id=TipoTercero.CLIENTE) \
        .values(campo_valor=F('id'), campo_texto=F('nombre')).order_by('nombre')
    rango_anho = [{'campo_valor': anho, 'campo_texto': str(anho)} for anho in range(2000, 2051)]

    datos = {'tipo_contratos': tipo_contratos,
             'empresas': empresas,
             'terceros': terceros,
             'rango_anho': rango_anho,
             'opcion': opcion}
    if contrato:
        datos['contrato'] = contrato

    return datos
# endregion
