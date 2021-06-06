from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from django.db import IntegrityError
from django.http import JsonResponse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from Administracion.models import Cargo, Proceso, TipoContrato, CentroPoblado, Rango, Municipio, Departamento, \
    TipoIdentificacion, Empresa
from Administracion.utils import get_id_empresa_global
from EVA import settings
from EVA.General.utilidades import validar_formato_imagen, app_datetime_now
from Notificaciones.views.correo_electronico import enviar_correo
from EVA.General.validacionpermisos import tiene_permisos
from TalentoHumano.models.colaboradores import ColaboradorContrato, TipoNovedad, NovedadColaborador, ColaboradorEmpresa, \
    ColaboradorProceso
from EVA.views.index import AbstractEvaLoggedView
from Notificaciones.models.models import EventoDesencadenador
from Notificaciones.views.views import crear_notificacion_por_evento
from Proyectos.models import Contrato
from TalentoHumano.models import Colaborador, EntidadesCAFE
from Administracion.models import PermisosFuncionalidad
from TalentoHumano.models.entidades_cafe import NivelRiesgoARL


class ColaboradoresIndexView(AbstractEvaLoggedView):

    def get(self, request, id_contrato):
        if id_contrato != 0:
            colaboradores = Colaborador.objects\
                .filter(colaboradorcontrato__contrato_id=id_contrato, empresa_id=get_id_empresa_global(request))\
                .order_by('usuario__first_name', 'usuario__last_name')
        else:
            colaboradores = Colaborador.objects.filter(empresa_id=get_id_empresa_global(request))\
                .order_by('usuario__first_name', 'usuario__last_name')

        contratos = Contrato.objects.get_xa_select_activos().filter(empresa_id=get_id_empresa_global(request))
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
            colaborador.usuario.get_full_name()
            colaboradores = Colaborador.objects.all()[:9]
            contratos = ColaboradorContrato.objects.filter(colaborador=colaborador)
            procesos = ColaboradorProceso.objects.filter(colaborador=colaborador)
            novedades = NovedadColaborador.objects.filter(colaborador=colaborador)
            entregas_dotacion = novedades.filter(tipo_novedad_id=TipoNovedad.ENTEREGA_DOTACION)
            novedades_colaborador = novedades.exclude(tipo_novedad_id=TipoNovedad.ENTEREGA_DOTACION)
            return render(request, 'TalentoHumano/Colaboradores/perfil.html',
                          {'colaborador': colaborador,
                           'contratos': contratos,
                           'procesos': procesos,
                           'entregas_dotacion': entregas_dotacion,
                           'novedades_colaborador': novedades_colaborador,
                           'colaboradores': colaboradores})


class ColaboradoresCrearView(AbstractEvaLoggedView):
    OPCION = 'crear'

    def get(self, request):
        return render(request, 'TalentoHumano/Colaboradores/crear-editar.html', datos_xa_render(self.OPCION))

    def post(self, request):
        colaborador = Colaborador.from_dictionary(request.POST)
        colaborador.empresa_sesion_id = get_id_empresa_global(request)
        colaborador.empresa_id = get_id_empresa_global(request)
        colaborador.usuario_crea = request.user
        contratos = request.POST.getlist('contrato_id[]', None)
        grupos = request.POST.getlist('grupo_id[]', None)
        procesos = request.POST.getlist('proceso_id[]', None)

        colaborador.foto_perfil = request.FILES.get('foto_perfil', None)
        if not colaborador.foto_perfil:
            foto_nombre = 'profile-none-m.svg' if colaborador.genero == 'M' else 'profile-none-f.svg'
            colaborador.foto_perfil = f'{settings.EVA_PUBLIC_MEDIA}/foto_perfil/{foto_nombre}'

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
            ColaboradorEmpresa.objects.create(colaborador=colaborador, empresa_id=get_id_empresa_global(request))
            crear_notificacion_por_evento(EventoDesencadenador.BIENVENIDA, colaborador.usuario_id,
                                          colaborador.nombre_completo)
            crear_notificacion_por_evento(EventoDesencadenador.COLABORADOR, colaborador.usuario_id,
                                          colaborador.nombre_completo)

            for contrato in contratos:
                ColaboradorContrato.objects.create(contrato_id=contrato, colaborador=colaborador)

            for grp in grupos:
                colaborador.usuario.groups.add(Group.objects.get(id=grp))

            for proceso in procesos:
                ColaboradorProceso.objects.create(proceso_id=proceso, colaborador=colaborador)

            messages.success(request, 'Se ha agregado el colaborador  {0}'.format(colaborador.nombre_completo))

            dominio = request.get_host()
            uidb64 = urlsafe_base64_encode(force_bytes(colaborador.usuario.pk))
            token = default_token_generator.make_token(colaborador.usuario)
            ruta = 'http://{0}/password-reset-confirm/{1}/{2}'.format(dominio, uidb64, token)

            mensaje = "<p>Hola " + colaborador.usuario.first_name + ", " \
                      "Te estamos enviando este correo para que asignes una contraseña a tu " \
                                                                    "cuenta en EVA.</p>" \
                      "<p>Tu usuario es: " + colaborador.usuario.username + "</p>"\
                      "<p>El siguiente enlace te llevará a EVA donde puedes realizar el cambio:</p>"\
                      "<a href=" + ruta + ">Ir a EVA para asignación de la contraseña nueva</a>"

            enviar_correo({'nombre': colaborador.usuario.first_name,
                           'mensaje': mensaje,
                           'asunto': 'Bienvenido a EVA',
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
                         'arl_id', 'afp_id', 'caja_compensacion_id', 'cesantias_id', 'arl_nivel_id',
                         'fecha_ingreso', 'fecha_examen', 'salario', 'jefe_inmediato_id', 'cargo_id',
                         'tipo_contrato_id', 'lugar_nacimiento_id', 'rango_id', 'fecha_nacimiento',
                         'identificacion', 'tipo_identificacion_id', 'fecha_expedicion', 'genero', 'telefono',
                         'estado', 'nombre_contacto', 'grupo_sanguineo', 'telefono_contacto', 'parentesco',
                         'fecha_modificacion', 'usuario_actualiza', 'empresa', 'empresa_sesion_id']

        colaborador = Colaborador.from_dictionary(request.POST)
        colaborador.usuario_actualiza = request.user
        contratos = request.POST.getlist('contrato_id[]', None)
        procesos = request.POST.getlist('proceso_id[]', None)
        colaborador.empresa_id = request.POST.get('empresa_id')
        colaborador.empresa_sesion_id = colaborador.empresa_id
        colaborador.id = int(id)
        colaborador.foto_perfil = request.FILES.get('foto_perfil', None)
        if colaborador.foto_perfil:
            update_fields.append('foto_perfil')
            request.session['colaborador'] = Colaborador.objects.get(usuario=request.user).foto_perfil.url

        try:
            # Se excluye el usuario debido a que el full clean valida el id del usuario existente y no tiene en cuenta
            # los nuevos datos de usuario.
            colaborador.full_clean(validate_unique=False, exclude=['usuario', 'empresa_sesion'])
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
        cant_contrato = colaborador_contrato_db.count()

        cont_contrato = 0
        if cant_contrato == len(contratos):
            for clb in colaborador_contrato_db:
                for ctr in contratos:
                    if clb.contrato.id == int(ctr):
                        cont_contrato += 1
        else:
            cont_contrato = len(contratos)

        colaborador_proceso_db = ColaboradorProceso.objects.filter(colaborador_id=id)
        cant_proceso = colaborador_proceso_db.count()

        cont_proceso = 0
        if cant_proceso == len(procesos):
            for clb in colaborador_proceso_db:
                for ctr in procesos:
                    if clb.proceso_id == int(ctr):
                        cont_proceso += 1
        else:
            cont_proceso = len(procesos)

        if colaborador_db.comparar(colaborador, excluir=['foto_perfil', 'empresa_sesion', 'usuario_actualiza',
                                                         'usuario_crea']) and \
                len(cambios_usuario) <= 0 and not colaborador.foto_perfil and cont_contrato == cant_contrato \
                and cont_proceso == cant_proceso:
            messages.success(request, 'No se hicieron cambios en el colaborador {0}'
                             .format(colaborador.nombre_completo))
            return redirect(reverse('TalentoHumano:colaboradores-index', args=[0]))

        if colaborador.fecha_ingreso < colaborador.fecha_examen:
            messages.warning(request, 'La fecha de examen debe ser menor o igual a la fecha de ingreso')
            return render(request, 'TalentoHumano/Colaboradores/crear-editar.html',
                          datos_xa_render(self.OPCION, colaborador))

        else:
            if len(cambios_usuario) > 0:
                colaborador.usuario.save(update_fields=cambios_usuario)

            colaborador.save(update_fields=update_fields)
            ColaboradorEmpresa.objects.filter(colaborador=colaborador, empresa=colaborador_db.empresa).delete()
            ColaboradorEmpresa.objects.create(colaborador=colaborador, empresa_id=colaborador.empresa_id)

            ColaboradorContrato.objects.filter(colaborador_id=id).delete()
            for contrato in contratos:
                ColaboradorContrato.objects.create(contrato_id=contrato, colaborador_id=id)

            ColaboradorProceso.objects.filter(colaborador_id=id).delete()
            for proceso in procesos:
                ColaboradorProceso.objects.create(proceso_id=proceso, colaborador_id=id)

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


class ColaboradorCambiarFotoPerfilView(AbstractEvaLoggedView):
    def get(self, request, id):
        colaborador = Colaborador.objects.get(id=id)
        if request.user == colaborador.usuario or tiene_permisos(request, 'TalentoHumano', ['change_colaborador'], []):
            return render(request, 'TalentoHumano/_elements/_modal_cambiar_foto_perfil.html',
                          {'colaborador': colaborador, 'menu_actual': 'colaboradores'})
        else:
            return redirect(reverse('TalentoHumano:colaboradores-perfil', args=[id]))

    def post(self, request, id):
        colaborador = Colaborador.objects.get(id=id)
        if request.user == colaborador.usuario or tiene_permisos(request, 'TalentoHumano', ['change_colaborador'], []):
            foto_nueva = request.FILES.get('cambio_foto_perfil', None)
            if foto_nueva:
                if validar_formato_imagen(foto_nueva):
                    colaborador.foto_perfil = foto_nueva
                    colaborador.save(update_fields=['foto_perfil'])
                    messages.success(request, 'La foto de perfil se actualizó correctamente.')

                    if colaborador.usuario == request.user:
                        request.session['colaborador'] = colaborador.foto_perfil.url
                else:
                    messages.error(request, 'La foto cargada no tiene un formato correcto. <br>'
                                            'Formatos Aceptados: JPG, JPEG, PNG')
            else:
                messages.success(request, 'No se realizaron cambios en la foto de perfil.')

        return redirect(reverse('TalentoHumano:colaboradores-perfil', args=[id]))


class AgregarNovedadView(AbstractEvaLoggedView):
    def get(self, request, id_usuario):
        colaborador = Colaborador.objects.get(usuario_id=id_usuario)
        tipos_novedad = TipoNovedad.objects.get_xa_select_activos()
        return render(request, 'TalentoHumano/_elements/_modal_agregar_novedad.html', {'colaborador': colaborador,
                                                                                       'tipos_novedad': tipos_novedad})

    def post(self, request, id_usuario):
        colaborador = Colaborador.objects.get(usuario_id=id_usuario)
        novedad = NovedadColaborador.from_dictionary(request.POST)
        novedad.colaborador = colaborador
        novedad.usuario_crea = request.user
        novedad.fecha_crea = app_datetime_now()
        try:
            novedad.full_clean()
        except ValidationError as errores:
            if 'descripcion' in errores.message_dict:
                messages.error(request, 'La descripción ingresada excede el tamaño máximo')
            else:
                messages.error(request, 'Ha ocurrido un error')
            return redirect(reverse('TalentoHumano:colaboradores-index', args=[0]))

        if novedad.tipo_novedad.activar_usuario:
            usuario = User.objects.get(id=id_usuario)
            usuario.is_active = True
            usuario.save(update_fields=['is_active'])
        if novedad.tipo_novedad.desactivar_usuario:
            usuario = User.objects.get(id=id_usuario)
            usuario.is_active = False
            usuario.save(update_fields=['is_active'])

        novedad.save()
        messages.success(request, 'Se agregó la novedad correctamente')
        return redirect(reverse('TalentoHumano:colaboradores-index', args=[0]))


class SeleccionEmpresaView(AbstractEvaLoggedView):
    def get(self, request, id_usuario):
        todas_empresas = Empresa.objects.filter(estado=True)
        empresas_seleccionadas = ColaboradorEmpresa.objects.filter(colaborador__usuario_id=id_usuario)
        lista_empresas = []
        for empresa in todas_empresas:
            seleccion = False
            for selecciones in empresas_seleccionadas:
                if empresa == selecciones.empresa:
                    seleccion = True
                    break
            lista_empresas.append({'id': empresa.id, 'nombre': empresa.nombre, 'logo': empresa.logo.url,
                                   'seleccion': seleccion})
        lista_selecciones = []
        for e_s in empresas_seleccionadas:
            lista_selecciones.append(e_s.empresa_id)

        return render(request, 'TalentoHumano/_elements/_modal_seleccion_empresa.html',
                      {'empresas': lista_empresas,
                       'selecciones': lista_selecciones,
                       'id_usuario': id_usuario})

    def post(self, request, id_usuario):
        colaborador = Colaborador.objects.get(usuario_id=id_usuario)

        selecciones = request.POST.get('empresas_seleccionadas', '')
        if selecciones:
            selecciones = selecciones.split(',')
            ColaboradorEmpresa.objects.filter(colaborador=colaborador).delete()
        else:
            messages.success(request, 'No se encontraron selecciones. No se realizó ningún cambio.')
            return redirect(reverse('TalentoHumano:colaboradores-index', args=[0]))

        for sel in selecciones:
            ColaboradorEmpresa.objects.create(colaborador=colaborador, empresa_id=sel)
        messages.success(request, 'Se guardaron las empresas seleccionadas correctamente.')
        return redirect(reverse('TalentoHumano:colaboradores-index', args=[0]))


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
    cesantias = EntidadesCAFE.objects.cesantias_xa_select()
    arl_nivel = NivelRiesgoARL.objects.get_xa_select_activos()
    jefe_inmediato = Colaborador.objects.get_xa_select()
    contrato = Contrato.objects.get_xa_select_activos()
    grupos = construir_grupos_xa_select()
    grupos_colaborador = obtener_lista_grupos(colaborador, opcion)
    contratos_colaborador = ColaboradorContrato.objects.get_ids_contratos_list(colaborador)
    procesos_colaborador = ColaboradorProceso.objects.get_ids_procesos_list(colaborador)
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
    empresa = Empresa.objects.get_xa_select_activos()

    procesos_selecciones = ColaboradorProceso.objects.get_ids_procesos_list(colaborador)
    datos = {'arl': arl, 'eps': eps, 'afp': afp, 'caja_compensacion': caja_compensacion, 'cesantias': cesantias,
             'arl_nivel': arl_nivel, 'empresa': empresa, 'jefe_inmediato': jefe_inmediato, 'contrato': contrato,
             'cargo': cargo, 'proceso': proceso, 'tipo_contrato': tipo_contratos, 'rango': rango,
             'departamentos': departamentos, 'talla_camisa': talla_camisa, 'talla_zapatos': talla_zapatos,
             'talla_pantalon': talla_pantalon, 'tipo_identificacion': tipo_identificacion, 'opcion': opcion,
             'genero': genero, 'contratos_colaborador': contratos_colaborador, 'grupo_sanguineo': grupo_sanguineo,
             'menu_actual': 'colaboradores', 'grupos': grupos, 'grupos_colaborador': grupos_colaborador,
             'procesos_colaborador': procesos_colaborador, 'procesos_selecciones': procesos_selecciones}

    if colaborador:
        municipios = Municipio.objects.get_xa_select_activos() \
            .filter(departamento_id=colaborador.lugar_nacimiento.municipio.departamento_id)
        lugar_nacimiento = CentroPoblado.objects.get_xa_select_activos() \
            .filter(municipio_id=colaborador.lugar_nacimiento.municipio_id)
        datos['municipios'] = municipios
        datos['lugar_nacimiento'] = lugar_nacimiento
        datos['colaborador'] = colaborador

    return datos


def construir_grupos_xa_select():
    lista = []
    grupos = PermisosFuncionalidad.objects.filter(estado=True, grupo__isnull=False, solo_admin=False)
    for grp in grupos:
        lista.append({'campo_valor': grp.grupo.id, 'campo_texto': grp.nombre})
    return lista


def obtener_lista_grupos(colaborador, opcion):
    lista = []
    if opcion == 'editar':
        grupos = colaborador.usuario.groups.all()
        for grp in grupos:
            lista.append(grp.id)
    elif opcion == 'str':
        grupos = colaborador.usuario.groups.all()
        for grp in grupos:
            lista.append(str(grp.id))
    return lista
# endregion

