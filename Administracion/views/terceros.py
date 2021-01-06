import json
from datetime import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
from django.db.models import F
from django.db.transaction import atomic
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views import View
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from Administracion.enumeraciones import TipoPersona, RegimenFiscal, ResponsabilidadesFiscales, Tributos, \
    EstadosProveedor
from Administracion.models import Tercero, TipoIdentificacion, TipoTercero, CentroPoblado, Empresa, Departamento, \
    Municipio
from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView, AbstractEvaLoggedProveedorView
from Notificaciones.models.models import EventoDesencadenador, SeleccionDeNotificacionARecibir
from Notificaciones.views.correo_electronico import enviar_correo
from Notificaciones.views.views import crear_notificacion_por_evento
from TalentoHumano.models import Colaborador


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


class IndexProveedorView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        if request.user.is_authenticated:
            if Tercero.objects.filter(usuario=request.user):
                messages.success(request, 'Ha iniciado sesión como {0}'.format(request.user.email))
            else:
                return redirect(reverse('Administracion:iniciar-sesion'))
        return render(request, 'Administracion/index.html')


class InicioSesionProveedorView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if Tercero.objects.filter(usuario=request.user):
                messages.success(request, 'Ha iniciado sesión como {0}'.format(request.user.email))
            else:
                return redirect(reverse('Administracion:iniciar-sesion'))
        return render(request, 'Administracion/Tercero/Proveedor/Autenticacion/inicio-sesion.html')

    def post(self, request):
        if request.user.is_authenticated:
            if Colaborador.objects.filter(usuario=request.user):
                messages.success(request, 'Ha iniciado sesión como {0}'.format(request.user))
                return redirect(reverse('Administracion:proveedor-index'))
        else:
            correo = request.POST.get('correo', '')
            password = request.POST.get('password', '')
            usuario = User.objects.filter(email=correo)
            if usuario:
                try:
                    user = authenticate(username=usuario.first().username, password=password)
                    login(request, user)
                    messages.success(request, 'Ha iniciado sesión como {0}'.format(user.email))
                    request.session['proveedor'] = user.first_name
                    proveedor = Tercero.objects.filter(usuario=user)
                    if proveedor:
                        request.session['proveedor_foto'] = 'EVA/Plantilla/img/profile.png'
                        request.session['proveedor_nombre'] = proveedor.first().nombre
                        request.session['proveedor_correo'] = user.email
                        request.session['proveedor_empresa'] = proveedor.first().empresa_to_dict()
                        messages.success(request, 'Ha iniciado sesión como {0}'.format(request.user.first_name))
                except:
                    messages.warning(request, 'El correo y/o la contraseña no son válidos')
                    return redirect(reverse('Administracion:proveedor-iniciar-sesion'))
            else:
                messages.warning(request, 'El correo y/o la contraseña no son válidos')
                return redirect(reverse('Administracion:proveedor-iniciar-sesion'))

        return redirect(reverse('Administracion:proveedor-index'))


class RegistroProveedorView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('eva-index'))
        tipo_identificacion = TipoIdentificacion.objects.get_xa_select_activos()
        return render(request, 'Administracion/Tercero/Proveedor/registro.html',
                      {'tipo_identificacion': tipo_identificacion})

    @atomic
    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        datos_registro = json.loads(body_unicode)

        nombre = datos_registro['nombre']
        correo = datos_registro['correo']
        identificacion = datos_registro['identificacion']

        usuario = Colaborador.crear_usuario(nombre if len(nombre) < 20 else nombre[:20], 'proveedor', correo)

        tercero = Tercero()
        tercero.nombre = nombre
        tercero.estado = False
        tercero.tipo_tercero_id = TipoTercero.objects.get(nombre='Proveedor').id
        tercero.tipo_identificacion_id = datos_registro['tipoIdentificacion']
        tercero.identificacion = identificacion
        tercero.tipo_persona = 1 if tercero.tipo_identificacion.sigla == 'NIT' else 2
        tercero.telefono_movil_principal = datos_registro['celular']
        tercero.correo_principal = correo
        tercero.empresa_id = 1
        tercero.nombre_rl = ''
        tercero.identificacion_rl = ''
        tercero.telefono_fijo_principal = ''
        tercero.telefono_fijo_auxiliar = ''
        tercero.telefono_movil_auxiliar = ''
        tercero.correo_auxiliar = ''
        tercero.es_vigente = True
        tercero.estado_proveedor = EstadosProveedor.REGISTRADO

        if User.objects.filter(email=correo):
            return JsonResponse({'estado': 'ERROR', 'mensaje': 'El correo ingresado ya se encuentra registrado'})

        if Tercero.objects.filter(identificacion=identificacion):
            return JsonResponse({'estado': 'ERROR',
                                 'mensaje': 'El número de identificación ingresado ya está registrado'})
        try:
            usuario.save()
            tercero.usuario = usuario
            tercero.save()
            SeleccionDeNotificacionARecibir\
                .objects.create(envio_x_email=True, estado=True, usuario=usuario,
                                evento_desencadenador_id=EventoDesencadenador.RESPUESTA_SOLICITUD_PROVEEDOR)
            dominio = request.get_host()
            uidb64 = urlsafe_base64_encode(force_bytes(usuario.pk))
            token = default_token_generator.make_token(usuario)
            ruta = 'http://{0}/password-assign-proveedor/{1}/{2}'.format(dominio, uidb64, token)

            mensaje = "<p>Hola {0}, " \
                      "Te estamos enviando este correo para que asignes una contraseña a tu " \
                      "cuenta de proveedor en EVA.</p>" \
                      "<p>Tu usuario es: {1}</p>" \
                      "<p>El siguiente enlace te llevará a EVA donde puedes realizar la " \
                      "asignación de tu contraseña:</p>" \
                      "<a href={2}>Ir a EVA para asignar una contraseña</a>"\
                .format(tercero.nombre, usuario.email, ruta)

            enviar_correo({'nombre': tercero.nombre,
                           'mensaje': mensaje,
                           'asunto': 'Bienvenido a EVA',
                           'token': False,
                           'lista_destinatarios': [usuario.email]})
        except:
            return JsonResponse({'estado': 'ERROR'})

        return JsonResponse({'estado': 'OK', 'datos': {'correo': correo}})


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
    tipo_terceros = TipoTercero.objects.get_xa_select_activos()
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
