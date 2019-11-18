from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.views import View
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from django.db.models import F

from Administracion.models import Cargo, Proceso, TipoContrato, CentroPoblado, Rango
from Proyectos.models import Contrato
from TalentoHumano.models import Colaboradores, EntidadesCAFE

# Create your views here.


class ColaboradoresIndexView(View):

    def get(self, request):
        colaboradores = Colaboradores.objects.all()
        fecha = datetime.now()
        return render(request, 'TalentoHumano/Colaboradores/index.html', {'fecha': fecha,
                                                                          'colaboradores': colaboradores})

class ColaboradoresCrearView(View):
    OPCION = 'crear'

    def get(self, request):
        return render(request, 'TalentoHumano/Colaboradores/crear-editar.html', datos_xa_render(self.OPCION))

    def post(self, request):
        colaboradores = Colaboradores.from_dictionary(request.POST)
        try:
            colaboradores.full_clean()
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, colaboradores)
            datos['errores'] = errores.message_dict
            return render(request, 'TalentoHumano/Colaboradores/crear-editar.html', datos)

        if Colaboradores.objects.filter(identificacion=colaboradores.identificacion).exists():
            messages.warning(request, 'Ya existe un colaborador con identificación {0}'
                             .format(colaboradores.identificacion))
            return render(request, 'TalentoHumano/Colaboradores/crear-editar.html',
                          datos_xa_render(self.OPCION, colaboradores))

        colaboradores.save()
        messages.success(request, 'Se ha agregado el colaborador  {0}'.format(colaboradores.usuario.first_name) + ' ' +
                         '{0}'.format(colaboradores.usuario.last_name))
        return redirect(reverse('TalentoHumano:colaboradores-index'))



# region Métodos de ayuda


def datos_xa_render(opcion: str, colaborador: Colaboradores = None) -> dict:
    """
    Datos necesarios para la creación de los html de Colaboradores.
    :param opcion: valor de la acción a realizar 'crear' o 'editar'
    :param colaborador: Es opcional si se requiere pre cargar datos.
    :return: Un diccionario con los datos.
    """

    entidad_cafe = EntidadesCAFE.objects.get_xa_select_activos()
    jefe_inmediato = Colaboradores.objects \
        .filter(estado=True).values(campo_valor=F('id'), campo_texto=F('nombre')).order_by('nombre')
    contrato = Contrato.objects.get_xa_select_activos()
    cargo = Cargo.objects.get_xa_select_activos()
    proceso = Proceso.objects.get_xa_select_activos()
    tipo_contrato = TipoContrato.objects.get_xa_select_activos()
    lugar_nacimiento = CentroPoblado.objects.get_xa_select_activos()
    rango = Rango.objects.get_xa_select_activos()

    datos = {'entidad_cafe': entidad_cafe, 'jefe_inmediato': jefe_inmediato,
             'contrato': contrato, 'cargo': cargo, 'proceso': proceso, 'tipo_contrato': tipo_contrato,
             'lugar_nacimiento': lugar_nacimiento, 'rango': rango, 'opcion': opcion}

    if colaborador:
        datos['colaborador'] = colaborador

    return datos

# endregion
