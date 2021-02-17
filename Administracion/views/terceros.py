from datetime import datetime

from django.db import IntegrityError
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views import View

from Administracion.enumeraciones import TipoPersona, RegimenFiscal, ResponsabilidadesFiscales, Tributos
from Administracion.models import Tercero, TipoIdentificacion, TipoTercero, CentroPoblado, Empresa, Departamento, \
    Municipio, ConsecutivoDocumento, TipoDocumento
from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from Notificaciones.models.models import EventoDesencadenador
from Notificaciones.views.views import crear_notificacion_por_evento


class TerceroView(AbstractEvaLoggedView):
    def get(self, request):
        terceros = Tercero.objects.exclude(tipo_tercero=TipoTercero.PROVEEDOR)
        fecha = datetime.now()
        return render(request, 'Administracion/Tercero/index.html', {'terceros': terceros, 'fecha': fecha,
                                                                     'menu_actual': 'terceros'})


class TerceroCrearView(AbstractEvaLoggedView):
    OPCION = 'crear'

    def get(self, request):
        return render(request, 'Administracion/Tercero/crear-editar.html', datos_xa_render(self.OPCION))

    def post(self, request):
        tercero = Tercero.from_dictionary(request.POST)
        tercero.empresa_id = get_id_empresa_global(request)
        tercero.estado = True

        if Tercero.objects.filter(identificacion=tercero.identificacion):
            messages.warning(request, 'Ya existe un tercero con identificación {0}'.format(tercero.identificacion))
            return render(request, 'Administracion/Tercero/crear-editar.html', datos_xa_render(self.OPCION, tercero))

        if tercero.tipo_tercero_id == TipoTercero.CLIENTE:
            tercero.consecutivo_cliente = ConsecutivoDocumento.get_consecutivo_documento(TipoDocumento.CLIENTE,
                                                                                         tercero.empresa_id)
        tercero.save()
        crear_notificacion_por_evento(EventoDesencadenador.TERCERO, tercero.id, tercero.nombre)
        messages.success(request, 'Se ha agregado el tercero {0}'.format(tercero.nombre))
        return redirect(reverse('Administracion:terceros'))


class TerceroEditarView(AbstractEvaLoggedView):
    OPCION = 'editar'

    def get(self, request, id):
        tercero = Tercero.objects.get(id=id)
        return render(request, 'Administracion/Tercero/crear-editar.html', datos_xa_render(self.OPCION, tercero))

    def post(self, request, id):
        update_fields = ['nombre', 'identificacion', 'tipo_identificacion_id', 'estado',
                         'fecha_modificacion', 'tipo_tercero_id', 'centro_poblado_id', 'telefono', 'fax', 'direccion',
                         'digito_verificacion', 'tipo_persona', 'regimen_fiscal', 'responsabilidades_fiscales',
                         'tributos', 'correo_facelec', 'codigo_postal']

        tercero = Tercero.from_dictionary(request.POST)
        tercero.empresa_id = get_id_empresa_global(request)
        tercero.id = int(id)

        if Tercero.objects.filter(identificacion=tercero.identificacion).exclude(id=id).exists():
            messages.warning(request, 'Ya existe un tercero con identificación {0}'.format(tercero.identificacion))
            return render(request, 'Administracion/Tercero/crear-editar.html', datos_xa_render(self.OPCION, tercero))

        tercero_db = Tercero.objects.get(id=id)
        if tercero_db.comparar(tercero):
            messages.success(request, 'No se hicieron cambios en el tercero {0}'.format(tercero.nombre))
            return redirect(reverse('Administracion:terceros'))

        else:

            tercero.save(update_fields=update_fields)
            messages.success(request, 'Se ha actualizado el tercero {0}'.format(tercero.nombre)
                             + ' con identificación {0}'.format(tercero.identificacion))

            return redirect(reverse('Administracion:terceros'))


class TerceroEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        tercero = Tercero.objects.get(id=id)
        try:
            tercero.delete()
            messages.success(request, 'Se ha eliminado el tercero {0}'.format(tercero.nombre))
            return JsonResponse({"estado": "OK"})

        except IntegrityError:
            return JsonResponse({"estado": "error",
                                 "mensaje": "No se puede eliminar el tercero {0}".format(tercero.nombre) +
                                 "porque ya se encuentra asociado a otros módulos"})


class TerceroDetalleView(AbstractEvaLoggedView):
    def get(self, request, id):
        try:
            tercero = Tercero.objects.get(id=id)
            return JsonResponse({'estado': 'OK', 'datos': tercero.
                                to_dict(campos=['id', 'identificacion',
                                                'direccion', 'telefono',
                                                'fax', 'correo', 'digito_verificacion'])})
        except Tercero.DoesNotExist:
            return JsonResponse({"estado": "error", "mensaje": 'El cliente seleccionado no existe.'})


class PoliticaDeCofidencialidadView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('eva-index'))
        return render(request, 'Administracion/_common/_modal_politica_de_confidencialidad.html')

# region Métodos de ayuda


def datos_xa_render(opcion: str, tercero: Tercero = None) -> dict:
    """
    Datos necesarios para la creación de los html de Terceros.
    :param opcion: valor de la acción a realizar 'crear' o 'editar'
    :param tercero: Es opcional si se requiere pre cargar datos.
    :return: Un diccionario con los datos.
    """
    empresas = Empresa.objects \
        .filter(estado=True).values(campo_valor=F('id'), campo_texto=F('nombre')).order_by('nombre')
    tipos_identificacion = TipoIdentificacion.objects.get_xa_select_activos()
    tipo_terceros = TipoTercero.objects.get_xa_select_activos().exclude(id=TipoTercero.PROVEEDOR)
    departamentos = Departamento.objects.get_xa_select_activos()

    datos = {'empresas': empresas, 'tipos_identificacion': tipos_identificacion, 'tipo_terceros': tipo_terceros,
             'departamentos': departamentos, 'opcion': opcion, 'menu_actual': 'terceros',
             'tipos_persona': TipoPersona.choices, 'regimenes_fiscales': RegimenFiscal.choices,
             'responsabilidades': ResponsabilidadesFiscales.choices, 'tributos': Tributos.choices}
    if tercero:
        municipios = Municipio.objects.get_xa_select_activos()\
            .filter(departamento_id=tercero.centro_poblado.municipio.departamento_id)
        centros_poblados = CentroPoblado.objects.get_xa_select_activos()\
            .filter(municipio_id=tercero.centro_poblado.municipio_id)

        datos['municipios'] = municipios
        datos['centros_poblados'] = centros_poblados
        datos['tercero'] = tercero
        datos['responsabilidades_tercero'] = tercero.responsabilidades_fiscales.split(';')\
            if tercero.responsabilidades_fiscales else []

    return datos
# endregion
