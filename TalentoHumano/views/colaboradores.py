from django.core.exceptions import ValidationError
from django.views import View
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from django.db import IntegrityError
from django.http import JsonResponse

from Administracion.models import Cargo, Proceso, TipoContrato, CentroPoblado, Rango, Municipio, Departamento, \
    TipoIdentificacion
from Proyectos.models import Contrato
from TalentoHumano.models import Colaborador, EntidadesCAFE


# Create your views here.


class ColaboradoresIndexView(View):

    def get(self, request):
        colaboradores = Colaborador.objects.all()
        return render(request, 'TalentoHumano/Colaboradores/index.html', {'colaboradores': colaboradores})


class ColaboradoresPerfilView(View):

    def get(self, request, id):
        colaborador = Colaborador.objects.get(id=id)
        colaboradores = Colaborador.objects.all()

        return render(request, 'TalentoHumano/Colaboradores/perfil.html', {'colaborador': colaborador,
                                                                           'colaboradores': colaboradores})


class ColaboradoresCrearView(View):
    OPCION = 'crear'

    def get(self, request):
        return render(request, 'TalentoHumano/Colaboradores/crear-editar.html', datos_xa_render(self.OPCION))

    def post(self, request):
        colaborador = Colaborador.from_dictionary(request.POST)
        try:
            # Se excluye el usuario debido a que el id no es asignado  después de ser guardado en la BD.
            colaborador.full_clean(exclude=['usuario'])
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, colaborador)
            datos['errores'] = errores.message_dict
            if 'identificacion' in errores.message_dict:
                for mensaje in errores.message_dict['identificacion']:
                    if mensaje.startswith('Ya existe'):
                        messages.warning(request, 'Ya existe un colaborador con identificación {0}'
                                         .format(colaborador.identificacion))
                        break
            return render(request, 'TalentoHumano/Colaboradores/crear-editar.html', datos)

        if colaborador.fecha_dotacion < colaborador.fecha_ingreso:
            messages.warning(request, 'La fecha de ingreso debe ser menor o igual a la fecha de entrega de dotación')
            return render(request, 'TalentoHumano/Colaboradores/crear-editar.html',
                          datos_xa_render(self.OPCION, colaborador))

        if colaborador.fecha_ingreso < colaborador.fecha_examen:
            messages.warning(request, 'La fecha de examen debe ser menor o igual a la fecha de ingreso')
            return render(request, 'TalentoHumano/Colaboradores/crear-editar.html',
                          datos_xa_render(self.OPCION, colaborador))

        else:

            colaborador.usuario.save()
            # Se realiza esto ya que el campo usuario_id del modelo no es asignado automáticamente despues de guardar el
            # ususario en la BD.
            colaborador.usuario_id = colaborador.usuario.id
            colaborador.save()
            messages.success(request, 'Se ha agregado el colaborador  {0}'.format(colaborador.nombre_completo))
            return redirect(reverse('TalentoHumano:colaboradores-index'))


class ColaboradorEditarView(View):
    OPCION = 'editar'

    def get(self, request, id):
        colaborador = Colaborador.objects.get(id=id)

        return render(request, 'TalentoHumano/Colaboradores/crear-editar.html',
                      datos_xa_render(self.OPCION, colaborador))

    def post(self, request, id):
        update_fields = ['direccion', 'talla_camisa', 'talla_zapatos', 'talla_pantalon', 'eps_id',
                         'arl_id', 'afp_id', 'caja_compensacion_id', 'fecha_ingreso', 'fecha_examen', 'fecha_dotacion',
                         'salario', 'jefe_inmediato_id', 'contrato_id', 'cargo_id', 'proceso_id', 'tipo_contrato_id',
                         'lugar_nacimiento_id', 'rango_id', 'fecha_nacimiento', 'identificacion',
                         'tipo_identificacion_id', 'fecha_expedicion', 'genero', 'telefono', 'estado']

        colaborador = Colaborador.from_dictionary(request.POST)
        colaborador.id = int(id)

        try:
            colaborador.full_clean(validate_unique=False, exclude=['usuario'])
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, colaborador)
            datos['errores'] = errores.message_dict
            return render(request, 'TalentoHumano/Colaboradores/crear-editar.html', datos)

        if Colaborador.objects.filter(identificacion=colaborador.identificacion).exclude(id=id).exists():
            messages.warning(request, 'Ya existe un colaborador con identificación {0}'
                             .format(colaborador.identificacion))
            return render(request, 'TalentoHumano/Colaboradores/crear-editar.html',
                          datos_xa_render(self.OPCION, colaborador))

        colaborador.usuario.save()
        colaborador.usuario_id = colaborador.usuario.id
        colaborador_db = Colaborador.objects.get(id=id)

        if colaborador_db.comparar(colaborador):
            messages.success(request, 'No se hicieron cambios en el colaborador {0}'
                             .format(colaborador.nombre_completo))
            return redirect(reverse('TalentoHumano:colaboradores-index'))
        if colaborador.fecha_dotacion < colaborador.fecha_ingreso:
            messages.warning(request, 'La fecha de ingreso debe ser menor o igual a la fecha de entrega de dotación')
            return render(request, 'TalentoHumano/Colaboradores/crear-editar.html',
                          datos_xa_render(self.OPCION, colaborador))

        if colaborador.fecha_ingreso < colaborador.fecha_examen:
            messages.warning(request, 'La fecha de examen debe ser menor o igual a la fecha de ingreso')
            return render(request, 'TalentoHumano/Colaboradores/crear-editar.html',
                          datos_xa_render(self.OPCION, colaborador))

        else:

            colaborador.usuario.save()
            # Se realiza esto ya que el campo usuario_id del modelo no es asignado automáticamente despues de guardar el
            # ususario en la BD.
            colaborador.usuario_id = colaborador.usuario.id

            colaborador.save(update_fields=update_fields)
            messages.success(request, 'Se ha actualizado el colaborador {0}'.format(colaborador.nombre_completo)
                             + ' con identificación {0}'.format(colaborador.identificacion))

            return redirect(reverse('TalentoHumano:colaboradores-index'))


class ColaboradorEliminarView(View):
    def post(self, request, id):
        try:
            colaborador = Colaborador.objects.get(id=id)
            colaborador.delete()
            messages.success(request, 'Se ha eliminado el colaborador  {0}'.format(colaborador.nombre_completo) + ' '
                             + ' con indentificación {0}'.format(colaborador.identificacion))
            return JsonResponse({"Mensaje": "OK"})

        except IntegrityError:
            colaborador = Colaborador.objects.get(id=id)
            messages.warning(request, 'No se puede eliminar el colaborador  {0}'.format(colaborador.nombre_completo) +
                             ' ' + ' con identificación {0}'.format(colaborador.identificacion) +
                             ' porque ya se encuentra asociada a otro módulo')
            return JsonResponse({"Mensaje": "No se puede eliminar"})


# region Métodos de ayuda


def datos_xa_render(opcion: str = None, colaborador: Colaborador = None) -> dict:
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
    jefe_inmediato = Colaborador.objects.get_xa_select()
    contrato = Contrato.objects.get_xa_select_activos()
    cargo = Cargo.objects.get_xa_select_activos()
    proceso = Proceso.objects.get_xa_select_activos()
    tipo_contratos = TipoContrato.objects.tipos_laborares(True, True)
    departamentos = Departamento.objects.get_xa_select_activos()
    rango = Rango.objects.get_xa_select_activos()
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
