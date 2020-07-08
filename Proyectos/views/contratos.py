from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import F

from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from Notificaciones.models.models import EventoDesencadenador
from Notificaciones.views.views import crear_notificacion_por_evento
from Proyectos.models.contratos import Contrato
from Administracion.models import Tercero, Empresa, TipoContrato, Proceso
from TalentoHumano.models import Colaborador


class ContratoView(AbstractEvaLoggedView):
    def get(self, request):
        contratos = Contrato.objects.filter(empresa_id=get_id_empresa_global(request))
        fecha = datetime.now()
        return render(request, 'Proyectos/Contrato/index.html', {'contratos': contratos, 'fecha': fecha,
                                                                 'menu_actual': 'contratos'})


class ContratoCrearView(AbstractEvaLoggedView):
    OPCION = 'crear'

    def get(self, request):
        return render(request, 'Proyectos/Contrato/crear-editar.html', datos_xa_render(self.OPCION))

    def post(self, request):
        contrato = Contrato.from_dictionary(request.POST)
        contrato.empresa_id = get_id_empresa_global(request)
        contrato.residente = Colaborador.objects.get(id=contrato.residente_id).usuario
        try:
            contrato.full_clean()
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, contrato)
            datos['errores'] = errores.message_dict
            return render(request, 'Proyectos/Contrato/crear-editar.html', datos)

        if Contrato.objects.filter(numero_contrato=contrato.numero_contrato).exists():
            messages.warning(request, 'Ya existe un contrato con número {0}'.format(contrato.numero_contrato))
            return render(request, 'Proyectos/Contrato/crear-editar.html', datos_xa_render(self.OPCION, contrato))

        contrato.save()
        crear_notificacion_por_evento(EventoDesencadenador.CONTRATO, contrato.id, contrato.numero_contrato)
        messages.success(request, 'Se ha agregado el contrato número {0}'.format(contrato.numero_contrato))
        return redirect(reverse('proyectos:contratos'))


class ContratoEditarView(AbstractEvaLoggedView):
    OPCION = 'editar'

    def get(self, request, id):
        contrato = Contrato.objects.get(id=id)
        return render(request, 'Proyectos/Contrato/crear-editar.html', datos_xa_render(self.OPCION, contrato))

    def post(self, request, id):
        update_fields = ['numero_contrato', 'cliente_id', 'anho', 'supervisor_nombre', 'supervisor_correo',
                         'supervisor_telefono', 'residente', 'fecha_inicio', 'fecha_terminacion', 'valor',
                         'periodicidad_informes', 'tiempo', 'tipo_contrato_id', 'empresa_id']

        contrato = Contrato.from_dictionary(request.POST)
        contrato.empresa_id = get_id_empresa_global(request)
        contrato.residente = Colaborador.objects.get(id=contrato.residente_id).usuario
        contrato.id = int(id)

        try:
            contrato.full_clean(validate_unique=False)
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, contrato)
            datos['errores'] = errores.message_dict
            return render(request, 'Proyectos/Contrato/crear-editar.html', datos)

        if Contrato.objects.filter(numero_contrato=contrato.numero_contrato).exclude(id=id).exists():
            messages.warning(request, 'Ya existe un contrato con número {0}'.format(contrato.numero_contrato))
            return render(request, 'Proyectos/Contrato/crear-editar.html', datos_xa_render(self.OPCION, contrato))

        contrato_db = Contrato.objects.get(id=id)
        if contrato_db.comparar(contrato):
            messages.success(request, 'No se hicieron cambios en el contrato número {0}'
                             .format(contrato.numero_contrato))
            return redirect(reverse('Proyectos:contratos'))
        else:
            contrato.save(update_fields=update_fields)
            messages.success(request, 'Se ha actualizado el contrato número {0}'.format(contrato.numero_contrato))
            return redirect(reverse('Proyectos:contratos'))


class ContratoEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        try:
            contrato = Contrato.objects.get(id=id)
            contrato.delete()
            messages.success(request, 'Se ha eliminado el contrato {0}'.format(contrato.numero_contrato))
            return JsonResponse({"estado": "OK"})

        except IntegrityError:
            return JsonResponse({"estado": "error", "mensaje": "Este contrato no se puede eliminar "
                                                               "porque ya está siendo usado."})


# region Métodos de ayuda
def datos_xa_render(opcion: str, contrato: Contrato = None) -> dict:
    """
    Datos necesarios para la creación de los html de Contratos.
    :param opcion: valor de la acción a realizar 'crea' o 'editar'
    :param contrato: Es opcional si se requiere pre cargar datos.
    :return: Un diccionario con los datos.
    """

    tipo_contratos = TipoContrato.objects.tipos_comerciales(True, True)
    procesos = Proceso.objects.get_xa_select_activos()
    residentes = Colaborador.objects.get_xa_select_activos()
    empresas = Empresa.objects.filter(estado=True).values(campo_valor=F('id'), campo_texto=F('nombre')) \
        .order_by('nombre')
    terceros = Tercero.objects.clientes_xa_select()
    rango_anho = [{'campo_valor': anho, 'campo_texto': str(anho)} for anho in range(2000, 2051)]

    datos = {'tipo_contratos': tipo_contratos,
             'procesos': procesos,
             'residentes': residentes,
             'empresas': empresas,
             'terceros': terceros,
             'rango_anho': rango_anho,
             'opcion': opcion,
             'menu_actual': 'contratos'}
    if contrato:
        datos['contrato'] = contrato

    return datos
# endregion
