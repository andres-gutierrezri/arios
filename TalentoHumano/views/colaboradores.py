from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.views import View
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from django.db.models import F

from Administracion.models import Cargo, Proceso, TipoContrato, CentroPoblado, Rango, Municipio, Departamento, \
    TipoIdentificacion
from Proyectos.models import Contrato
from TalentoHumano.models import Colaboradores, EntidadesCAFE, TipoEntidadesCAFE


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

    eps = EntidadesCAFE.objects.eps_xa_select()
    arl = EntidadesCAFE.objects.arl_xa_select()
    afp = EntidadesCAFE.objects.afp_xa_select()
    caja_compensacion = EntidadesCAFE.objects.caja_compensacion_xa_select()
    jefe_inmediato = Colaboradores.objects.get_xa_select()
    contrato = Contrato.objects.get_xa_select()
    cargo = Cargo.objects.get_xa_select()
    proceso = Proceso.objects.get_xa_select()
    tipo_contratos = TipoContrato.objects.tipos_laborares(True, True)
    departamentos = Departamento.objects.get_xa_select_activos()
    rango = Rango.objects.get_xa_select()
    talla_camisa = [{'campo_valor': talla_camisa, 'campo_texto': str(talla_camisa)} for talla_camisa in
                    ['S', 'M', 'L', 'XL']]
    talla_pantalon = [{'campo_valor': talla_pantalon, 'campo_texto': str(talla_pantalon)} for talla_pantalon in
                      range(6, 45)]
    talla_zapatos = [{'campo_valor': talla_zapatos, 'campo_texto': str(talla_zapatos)} for talla_zapatos in
                     range(20, 47)]
    genero = [{'campo_valor': genero, 'campo_texto': str(genero)} for genero in ['Masculino', 'Femenino']]
    tipo_identificacion = TipoIdentificacion.objects.get_xa_select_activos()

    datos = {'arl': arl, 'eps': eps, 'afp': afp, 'caja_compensacion': caja_compensacion,
             'jefe_inmediato': jefe_inmediato, 'contrato': contrato, 'cargo': cargo, 'proceso': proceso,
             'tipo_contrato': tipo_contratos, 'rango': rango, 'departamentos': departamentos,
             'talla_camisa': talla_camisa, 'talla_zapatos': talla_zapatos, 'talla_pantalon': talla_pantalon,
             'tipo_identificacion': tipo_identificacion, 'opcion': opcion, 'genero': genero}

    if colaborador:
        municipios = Municipio.objects.get_xa_select_activos() \
            .filter(departamento_id=colaborador.lugar_nacimiento.municipio.departamento_id)
        lugar_nacimiento = CentroPoblado.objects.get_xa_select_activos() \
            .filter(municipio_id=colaborador.lugar_nacimiento.municipio_id)
        datos['municipios'] = municipios
        datos['lugar_nacimiento'] = lugar_nacimiento
        datos['colaborador'] = colaborador

    return datos

# endregion
