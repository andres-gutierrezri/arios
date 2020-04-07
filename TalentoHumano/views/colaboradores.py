from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect, reverse
from django.db import IntegrityError
from django.http import JsonResponse
from django.template.loader import get_template
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from Administracion.models import Cargo, Proceso, TipoContrato, CentroPoblado, Rango, Municipio, Departamento, \
    TipoIdentificacion
from Notificaciones.views.correo_electronico import enviar_correo
from EVA.General.validacionpermisos import tiene_permisos
from TalentoHumano.models.colaboradores import ColaboradorContrato
from EVA.views.index import AbstractEvaLoggedView
from Notificaciones.models.models import EventoDesencadenador
from Notificaciones.views.views import crear_notificacion_por_evento
from Proyectos.models import Contrato
from TalentoHumano.models import Colaborador, EntidadesCAFE


class ColaboradoresIndexView(AbstractEvaLoggedView):

    def get(self, request, id_contrato):
        if id_contrato != 0:
            colaboradores = Colaborador.objects.filter(colaboradorcontrato__contrato_id=id_contrato)\
                .order_by('usuario__first_name', 'usuario__last_name')
        else:
            colaboradores = Colaborador.objects.all().order_by('usuario__first_name', 'usuario__last_name')

        contratos = Contrato.objects.get_xa_select_activos()
        return render(request, 'TalentoHumano/Colaboradores/index.html', {'colaboradores': colaboradores,
                                                                          'contratos': contratos,
                                                                          'id_contrato': id_contrato,
                                                                          'menu_actual': 'colaboradores'})


class ColaboradoresPerfilView(AbstractEvaLoggedView):

    def get(self, request, id):
        if request.session['colaborador_id'] != id and \
                not tiene_permisos(request, 'TalentoHumano', ['view_colaborador'], None):
            return redirect(reverse('eva-index'))
        else:
            colaborador = Colaborador.objects.get(id=id)
            colaboradores = Colaborador.objects.all()[:9]
            contratos = ColaboradorContrato.objects.filter(colaborador=colaborador)
            return render(request, 'TalentoHumano/Colaboradores/perfil.html', {'colaborador': colaborador,
                                                                               'contratos': contratos,
                                                                               'colaboradores': colaboradores})


class ColaboradoresCrearView(AbstractEvaLoggedView):
    OPCION = 'crear'

    def get(self, request):
        return render(request, 'TalentoHumano/Colaboradores/crear-editar.html', datos_xa_render(self.OPCION))

    def post(self, request):
        colaborador = Colaborador.from_dictionary(request.POST)
        contratos = request.POST.getlist('contrato_id[]', None)

        colaborador.foto_perfil = request.FILES.get('foto_perfil', None)
        if not colaborador.foto_perfil:
            colaborador.foto_perfil = 'foto_perfil/profile-none.png'

        try:
            # Se excluye el usuario debido a que el id no es asignado  después de ser guardado en la BD.
            colaborador.full_clean(exclude=['usuario', 'empresa_sesion'])
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

        if User.objects.filter(email__iexact=colaborador.usuario.email).exists():
            messages.warning(request, 'El correo electrónico ya está asociado a otro usuario')
            return render(request, 'TalentoHumano/Colaboradores/crear-editar.html',
                          datos_xa_render(self.OPCION, colaborador))

        else:
            colaborador.usuario.save()
            # Se realiza esto ya que el campo usuario_id del modelo no es asignado automáticamente
            # despues de guardar el ususario en la BD.
            colaborador.usuario_id = colaborador.usuario.id
            colaborador.empresa_sesion_id = Contrato.objects.get(id=contratos[0]).empresa_id
            colaborador.save()
            crear_notificacion_por_evento(EventoDesencadenador.BIENVENIDA, colaborador.id)
            crear_notificacion_por_evento(EventoDesencadenador.COLABORADOR, colaborador.id)

            for contrato in contratos:
                ColaboradorContrato.objects.create(contrato_id=contrato, colaborador=colaborador)

            messages.success(request, 'Se ha agregado el colaborador  {0}'.format(colaborador.nombre_completo))

            dominio = request.get_host()
            uidb64 = urlsafe_base64_encode(force_bytes(colaborador.usuario.pk))
            token = default_token_generator.make_token(colaborador.usuario)
            ruta = 'http://{0}/password-reset-confirm/{1}/{2}'.format(dominio, uidb64, token)

            mensaje = "<p>Hola " + colaborador.usuario.first_name + ", " \
                      "Te estamos enviando este correo para que asignes una nueva contraseña a tu " \
                                                                    "cuenta en Arios Ingeniería SAS.</p>" \
                      "<p>Tu usuario es: " + colaborador.usuario.username + "</p>"\
                      "<p>El siguiente enlace te redireccionará a la página donde puedes realizar el cambio:</p>"\
                      "<a href=" + ruta + ">Ir a la página para asignación de nueva contraseña </a>"

            enviar_correo({'nombre': colaborador.usuario.first_name,
                           'mensaje': mensaje,
                           'asunto': 'Bienvenido a Arios Ingenieria SAS',
                           'token': False,
                           'lista_destinatarios': [colaborador.usuario.email]})
            return redirect(reverse('TalentoHumano:colaboradores-index', args=[0]))


class ColaboradorEditarView(AbstractEvaLoggedView):
    OPCION = 'editar'

    def get(self, request, id):
        colaborador = Colaborador.objects.get(id=id)

        return render(request, 'TalentoHumano/Colaboradores/crear-editar.html',
                      datos_xa_render(self.OPCION, colaborador))

    def post(self, request, id):
        update_fields = ['direccion', 'talla_camisa', 'talla_zapatos', 'talla_pantalon', 'eps_id',
                         'arl_id', 'afp_id', 'caja_compensacion_id', 'fecha_ingreso', 'fecha_examen',
                         'fecha_dotacion', 'salario', 'jefe_inmediato_id', 'cargo_id', 'proceso_id',
                         'tipo_contrato_id', 'lugar_nacimiento_id', 'rango_id', 'fecha_nacimiento',
                         'identificacion', 'tipo_identificacion_id', 'fecha_expedicion', 'genero', 'telefono',
                         'estado', 'nombre_contacto', 'grupo_sanguineo', 'telefono_contacto', 'parentesco']

        colaborador = Colaborador.from_dictionary(request.POST)
        contratos = request.POST.getlist('contrato_id[]', None)

        colaborador.id = int(id)
        colaborador.foto_perfil = request.FILES.get('foto_perfil', None)
        if colaborador.foto_perfil:
            update_fields.append('foto_perfil')
            request.session['colaborador'] = Colaborador.objects.get(usuario=request.user).foto_perfil.url

        try:
            colaborador.full_clean(validate_unique=False, exclude=['empresa_sesion'])
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, colaborador)
            datos['errores'] = errores.message_dict
            return render(request, 'TalentoHumano/Colaboradores/crear-editar.html', datos)

        if Colaborador.objects.filter(identificacion=colaborador.identificacion).exclude(id=id).exists():
            messages.warning(request, 'Ya existe un colaborador con identificación {0}'
                             .format(colaborador.identificacion))
            return render(request, 'TalentoHumano/Colaboradores/crear-editar.html',
                          datos_xa_render(self.OPCION, colaborador))

        if User.objects.filter(email__iexact=colaborador.usuario.email).exclude(id=colaborador.usuario_id).exists():

            messages.warning(request, 'El correo electrónico ya está asociado a otro usuario')
            return render(request, 'TalentoHumano/Colaboradores/crear-editar.html',
                          datos_xa_render(self.OPCION, colaborador))

        colaborador_db = Colaborador.objects.get(id=id)

        cambios_usuario: list = []

        if colaborador_db.usuario.first_name != colaborador.usuario.first_name:
            cambios_usuario.append('first_name')

        if colaborador_db.usuario.last_name != colaborador.usuario.last_name:
            cambios_usuario.append('last_name')

        if colaborador_db.usuario.email != colaborador.usuario.email:
            cambios_usuario.append('email')

        if 'first_name' in cambios_usuario or 'last_name' in cambios_usuario:
            cambios_usuario.append('username')

        colaborador_contrato_db = ColaboradorContrato.objects.filter(colaborador_id=id)
        cant = colaborador_contrato_db.count()

        cont = 0
        if cant == len(contratos):
            for clb in colaborador_contrato_db:
                for ctr in contratos:
                    if clb.contrato.id == int(ctr):
                        cont += 1

        if colaborador_db.comparar(colaborador, excluir=['foto_perfil', 'empresa_sesion']) and \
                len(cambios_usuario) <= 0 and not colaborador.foto_perfil and cont == cant:
            messages.success(request, 'No se hicieron cambios en el colaborador {0}'
                             .format(colaborador.nombre_completo))
            return redirect(reverse('TalentoHumano:colaboradores-index', args=[0]))

        if colaborador.fecha_dotacion < colaborador.fecha_ingreso:
            messages.warning(request, 'La fecha de ingreso debe ser menor o igual a la fecha de entrega de dotación')
            return render(request, 'TalentoHumano/Colaboradores/crear-editar.html',
                          datos_xa_render(self.OPCION, colaborador))

        if colaborador.fecha_ingreso < colaborador.fecha_examen:
            messages.warning(request, 'La fecha de examen debe ser menor o igual a la fecha de ingreso')
            return render(request, 'TalentoHumano/Colaboradores/crear-editar.html',
                          datos_xa_render(self.OPCION, colaborador))

        else:
            if len(cambios_usuario) > 0:
                colaborador.usuario.save(update_fields=cambios_usuario)

            colaborador.save(update_fields=update_fields)

            ColaboradorContrato.objects.filter(colaborador_id=id).delete()
            for contrato in contratos:
                ColaboradorContrato.objects.create(contrato_id=contrato, colaborador_id=id)

            if colaborador.foto_perfil:
                request.session['colaborador'] = Colaborador.objects.get(usuario=request.user).foto_perfil.url

            messages.success(request, 'Se ha actualizado el colaborador {0}'.format(colaborador.nombre_completo)
                             + ' con identificación {0}'.format(colaborador.identificacion))

            return redirect(reverse('TalentoHumano:colaboradores-index', args=[0]))


class ColaboradorEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        colaborador = Colaborador.objects.get(id=id)
        try:
            colaborador.delete()
            messages.success(request, 'Se ha eliminado el colaborador  {0}'.format(colaborador.nombre_completo)
                             + ' ' + ' con indentificación {0}'.format(colaborador.identificacion))
            return JsonResponse({"estados": "OK"})

        except IntegrityError:
            return JsonResponse({"estado": "error",
                                 "mensaje": "No se puede eliminar el colaborador {0} con identificación {1} porque ya"
                                            " se encuentra asociado a otro módulo".format(colaborador.nombre_completo,
                                                                                          colaborador.identificacion)})


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
    contratos_colaborador = ColaboradorContrato.objects.get_ids_contratos_list(colaborador)
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
    genero = [{'campo_valor': 'M', 'campo_texto': 'Masculino'}, {'campo_valor': 'F', 'campo_texto': 'Femenino'},
              {'campo_valor': 'O', 'campo_texto': 'Otro'}]
    tipo_identificacion = TipoIdentificacion.objects.get_xa_select_activos()
    grupo_sanguineo = [{'campo_valor': grupo_sanguineo, 'campo_texto': str(grupo_sanguineo)} for grupo_sanguineo in
                    ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']]

    datos = {'arl': arl, 'eps': eps, 'afp': afp, 'caja_compensacion': caja_compensacion,
             'jefe_inmediato': jefe_inmediato, 'contrato': contrato, 'cargo': cargo, 'proceso': proceso,
             'tipo_contrato': tipo_contratos, 'rango': rango, 'departamentos': departamentos,
             'talla_camisa': talla_camisa, 'talla_zapatos': talla_zapatos, 'talla_pantalon': talla_pantalon,
             'tipo_identificacion': tipo_identificacion, 'opcion': opcion, 'genero': genero,
             'contratos_colaborador': contratos_colaborador, 'grupo_sanguineo': grupo_sanguineo,
             'menu_actual': 'colaboradores'}

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

