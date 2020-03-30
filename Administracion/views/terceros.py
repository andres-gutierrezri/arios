from datetime import datetime

from django.db import IntegrityError
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError

from Administracion.models import Tercero, TipoIdentificacion, TipoTercero, CentroPoblado, Empresa, Departamento, \
    Municipio
from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from Notificaciones.models.models import EventoDesencadenador
from Notificaciones.views.views import crear_notificacion_por_evento


class TerceroView(AbstractEvaLoggedView):
    def get(self, request):
        terceros = Tercero.objects.all()
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
        try:
            tercero.full_clean()
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, tercero)
            datos['errores'] = errores.message_dict
            if 'identificacion' in errores.message_dict:
                for mensaje in errores.message_dict['identificacion']:
                    if mensaje.startswith('Ya existe'):
                        messages.warning(request,
                                         'Ya existe un tercero con identificación {0}'.format(tercero.identificacion))
                        break
            return render(request, 'Administracion/Tercero/crear-editar.html', datos)

        tercero.save()
        crear_notificacion_por_evento(EventoDesencadenador.TERCERO, tercero.id)
        messages.success(request, 'Se ha agregado el tercero {0}'.format(tercero.nombre))
        return redirect(reverse('Administracion:terceros'))


class TerceroEditarView(AbstractEvaLoggedView):
    OPCION = 'editar'

    def get(self, request, id):
        tercero = Tercero.objects.get(id=id)
        return render(request, 'Administracion/Tercero/crear-editar.html', datos_xa_render(self.OPCION, tercero))

    def post(self, request, id):
        update_fields = ['nombre', 'identificacion', 'tipo_identificacion_id', 'estado',
                         'fecha_modificacion', 'tipo_tercero_id', 'centro_poblado_id', 'telefono', 'fax', 'direccion']

        tercero = Tercero.from_dictionary(request.POST)
        tercero.empresa_id = get_id_empresa_global(request)
        tercero.id = int(id)

        try:
            tercero.full_clean(validate_unique=False)
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, tercero)
            datos['errores'] = errores.message_dict
            return render(request, 'Administracion/Tercero/crear-editar.html', datos)

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
        try:
            tercero = Tercero.objects.get(id=id)
            tercero.delete()
            messages.success(request, 'Se ha eliminado el tercero {0}'.format(tercero.nombre))
            return JsonResponse({"Mensaje": "OK"})

        except IntegrityError:
            tercero = Tercero.objects.get(id=id)
            messages.warning(request, 'No se puede eliminar el tercero {0}'.format(tercero.nombre) +
                             ' porque ya se encuentra asociado a otros módulos')
            return JsonResponse({"Mensaje": "No se puede eliminar"})


class TerceroDetalleView(AbstractEvaLoggedView):
    def get(self, request, id):
        try:
            tercero = Tercero.objects.get(id=id)
            return JsonResponse({'estado': 'OK', 'datos': tercero.to_dict(campos=['id', 'identificacion',
                                                                                  'direccion', 'telefono',
                                                                                  'fax', 'correo'])})
        except Tercero.DoesNotExist:
            return JsonResponse({"estado": "error", "mensaje": 'El cliente seleccionado no existe.'})


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
    tipo_terceros = TipoTercero.objects.get_xa_select_activos()
    departamentos = Departamento.objects.get_xa_select_activos()

    datos = {'empresas': empresas, 'tipos_identificacion': tipos_identificacion, 'tipo_terceros': tipo_terceros,
             'departamentos': departamentos, 'opcion': opcion, 'menu_actual': 'terceros'}
    if tercero:
        municipios = Municipio.objects.get_xa_select_activos()\
            .filter(departamento_id=tercero.centro_poblado.municipio.departamento_id)
        centros_poblados = CentroPoblado.objects.get_xa_select_activos()\
            .filter(municipio_id=tercero.centro_poblado.municipio_id)

        datos['municipios'] = municipios
        datos['centros_poblados'] = centros_poblados
        datos['tercero'] = tercero

    return datos
# endregion
