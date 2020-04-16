import json
from datetime import datetime

from django.db import IntegrityError
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError

from Administracion.models import Proceso
from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from Notificaciones.models.models import EventoDesencadenador
from Notificaciones.views.views import crear_notificacion_por_evento
from SGI.models import CadenaAprobacionEncabezado
from SGI.models.documentos import CadenaAprobacionDetalle, Archivo, ResultadosAprobacion, EstadoArchivo, Documento
from TalentoHumano.models import Colaborador


class CadenaAprobacionView(AbstractEvaLoggedView):
    def get(self, request):
        cadenas_aprobacion = CadenaAprobacionEncabezado.objects.all()
        detalles = CadenaAprobacionDetalle.objects.all()
        colaboradores = Colaborador.objects.all()
        procesos = Proceso.objects.filter(empresa_id=get_id_empresa_global(request)).order_by('nombre')
        return render(request, 'SGI/CadenasAprobacion/index.html', {'cadenas_aprobacion': cadenas_aprobacion,
                                                                    'detalles': detalles,
                                                                    'fecha': datetime.now(),
                                                                    'colaboradores': colaboradores,
                                                                    'menu_actual': 'cadenas_aprobacion',
                                                                    'procesos': procesos})


def usuarios_seleccionados(request):
    selecciones = request.POST.get('usuarios_seleccionados', '').split(',')
    if selecciones[0]:
        selecciones.append(request.POST.get('ultimo_usuario', '')[0])
    else:
        selecciones = request.POST.get('ultimo_usuario', '')

    return selecciones


class CadenaAprobacionCrearView(AbstractEvaLoggedView):
    OPCION = 'crear'

    def get(self, request):
        return render(request, 'SGI/CadenasAprobacion/crear-editar.html', datos_xa_render(self.OPCION, request))

    def post(self, request):
        selecciones = usuarios_seleccionados(request)

        cadena = CadenaAprobacionEncabezado.from_dictionary(request.POST)
        cadena.empresa_id = get_id_empresa_global(request)
        cadena.estado = True

        try:
            cadena.full_clean()
        except ValidationError as errores:
            return render(request, 'SGI/CadenasAprobacion/crear-editar.html',
                          datos_xa_render(self.OPCION, request, cadena, errores))
        cadena.save()

        orden = 1
        for usuario in selecciones:
            CadenaAprobacionDetalle.objects.create(cadena_aprobacion=cadena, usuario_id=usuario, orden=orden)
            orden += 1

        messages.success(request, 'Se ha agregado la cadena de aprobación {0}'.format(cadena.nombre))
        return redirect(reverse('SGI:cadenas-aprobacion-ver'))


class CadenaAprobacionEditarView(AbstractEvaLoggedView):
    OPCION = 'editar'

    def get(self, request, id):
        cadena = CadenaAprobacionEncabezado.objects.get(id=id)
        return render(request, 'SGI/CadenasAprobacion/crear-editar.html', datos_xa_render(self.OPCION, request, cadena))

    def post(self, request, id):
        selecciones = usuarios_seleccionados(request)
        cadena = CadenaAprobacionEncabezado.from_dictionary(request.POST)
        cadena.id = id

        try:
            cadena.full_clean(validate_unique=False, exclude=['empresa'])
        except ValidationError as errores:
            return render(request, 'SGI/CadenasAprobacion/crear-editar.html',
                          datos_xa_render(self.OPCION, request, cadena, errores))

        if not Documento.objects.filter(cadena_aprobacion_id=id):
            if usuarios_seleccionados:
                CadenaAprobacionDetalle.objects.filter(cadena_aprobacion=cadena).delete()

        cadena.save(update_fields=['nombre', 'estado'])
        orden = 1
        for usuarios in selecciones:
            CadenaAprobacionDetalle.objects.create(cadena_aprobacion=cadena, usuario_id=usuarios, orden=orden)
            orden += 1

        messages.success(request, 'Se ha actualizado la cadena de aprobación {0}'.format(cadena.nombre))
        return redirect(reverse('SGI:cadenas-aprobacion-ver'))


class CadenaAprobacionEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        error = "Esta cadena de aprobación no puede ser eliminada porque se encuentra en uso"
        try:
            if not Archivo.objects.filter(cadena_aprobacion_id=id):
                cadena_encabezado = CadenaAprobacionEncabezado.objects.get(id=id)
                cadena_encabezado.delete()
                messages.success(request, 'Se ha eliminado la cadena de aprobación {0}'.format(cadena_encabezado.nombre))
                return JsonResponse({"estado": "OK"})
            else:
                return JsonResponse(
                    {"estado": "error",
                     "error": error})

        except IntegrityError:
            return JsonResponse(
                {"estado": "error",
                 "error": error})


class AprobacionDocumentoView(AbstractEvaLoggedView):
    def get(self, request):
        archivos = ResultadosAprobacion.objects.filter(usuario=request.user, estado_id=EstadoArchivo.PENDIENTE,
                                                       aprobacion_anterior=EstadoArchivo.APROBADO)
        procesos = Proceso.objects.filter(empresa_id=get_id_empresa_global(request)).order_by('nombre')
        fecha = datetime.now()
        return render(request, 'SGI/AprobacionDocumentos/index.html', {'archivos': archivos,
                                                                       'procesos': procesos,
                                                                       'menu_actual': 'aprobacion_documentos',
                                                                       'fecha': fecha})

# region Constantes de Accion de Documento
ACCION_NUEVO = 0
ACCION_CADENA_APROBADO = 1
ACCION_APROBADO = 2
ACCION_RECHAZADO = 3
ACCION_APROBACION_DIRECTA = 4
# endregion


class AccionAprobacionDocumentosView(AbstractEvaLoggedView):
    def get(self, request, id):
        documento = Archivo.objects.get(resultadosaprobacion=id)
        opciones = [{'texto': 'Aprobado', 'valor': EstadoArchivo.APROBADO},
                    {'texto': 'Rechazado', 'valor': EstadoArchivo.RECHAZADO}]
        return render(request, 'SGI/AprobacionDocumentos/accion_documento.html', {'documento': documento,
                                                                                  'opciones': opciones})

    def post(self, request, id):
        comentario = request.POST.get('comentario', '')
        opcion = request.POST.get('opcion', '')
        resultado = ResultadosAprobacion.objects.get(archivo_id=id, usuario=request.user)
        resultado.estado_id = opcion
        resultado.comentario = comentario
        resultado.save(update_fields=['estado', 'comentario'])

        if int(opcion) == EstadoArchivo.APROBADO:
            usuario_cadena = usuario_siguiente_cadena_aprobacion_detalle(resultado.archivo, request.user)
            if usuario_cadena:
                usuario_siguiente = ResultadosAprobacion.objects.get(usuario=usuario_cadena.usuario,
                                                                     archivo_id=id)
                usuario_siguiente.aprobacion_anterior = EstadoArchivo.APROBADO
                usuario_siguiente.save(update_fields=['aprobacion_anterior'])
                crear_notificacion_cadena(usuario_siguiente.archivo, ACCION_CADENA_APROBADO)
                crear_notificacion_cadena(usuario_cadena, ACCION_NUEVO, posicion=usuario_cadena.orden)
            else:
                archivo_nuevo = Archivo.objects.get(id=id)
                archivo_nuevo.estado_id = EstadoArchivo.APROBADO
                archivo_nuevo.save(update_fields=['estado'])
                documento = Documento(id=archivo_nuevo.documento.id)
                documento.version_actual = archivo_nuevo.version
                documento.save(update_fields=['version_actual'])
                archivo_anterior = Archivo.objects.filter(documento=archivo_nuevo.documento,
                                                          estado_id=EstadoArchivo.APROBADO).exclude(id=id)
                crear_notificacion_cadena(archivo_nuevo, ACCION_APROBADO)

                if archivo_anterior:
                    anterior = Archivo(id=archivo_anterior.first().id)
                    anterior.estado_id = EstadoArchivo.OBSOLETO
                    anterior.save(update_fields=['estado'])
        else:
            archivo = Archivo(id=id)
            archivo.estado_id = EstadoArchivo.RECHAZADO
            archivo.save(update_fields=['estado_id'])
            crear_notificacion_cadena(Archivo.objects.get(id=id), ACCION_RECHAZADO)

        messages.success(request, 'Se guardaron los datos correctamente')
        return redirect(reverse('SGI:aprobacion-documentos-ver'))


def crear_notificacion_cadena(archivo, accion, posicion: int = 0):
    if accion == ACCION_NUEVO:
        usuario = CadenaAprobacionDetalle.objects.get(cadena_aprobacion=archivo.cadena_aprobacion, orden=posicion)

        crear_notificacion_por_evento(EventoDesencadenador.NOTIFICACION_CA, archivo.id,
                                      contenido={'titulo': 'Solicitud de Aprobación',
                                                 'mensaje': 'Tienes un documento pendiente para aprobación',
                                                 'usuario': usuario.usuario_id})
    if accion == ACCION_APROBADO:
        crear_notificacion_por_evento(EventoDesencadenador.SOLICITUD_APROBACION, archivo.id,
                                      contenido={'titulo': 'Documento Aprobado',
                                                 'mensaje': 'Tu solicitud para el documento '
                                                            + archivo.documento.nombre + ' ha sido aprobada',
                                                 'usuario': archivo.usuario_id})
    elif accion == ACCION_CADENA_APROBADO:
        crear_notificacion_por_evento(EventoDesencadenador.SOLICITUD_APROBACION, archivo.id,
                                      contenido={'titulo': 'Documento en aprobación',
                                                 'mensaje': 'Tu solicitud para el documento '
                                                            + archivo.documento.nombre + ' está avanzando',
                                                 'usuario': archivo.usuario_id})
    elif accion == ACCION_RECHAZADO:
        crear_notificacion_por_evento(EventoDesencadenador.SOLICITUD_APROBACION, archivo.id,
                                      contenido={'titulo': 'Documento Rechazado',
                                                 'mensaje': 'Tu solicitud para el documento '
                                                            + archivo.documento.nombre + ' ha sido rechazada',
                                                 'usuario': archivo.usuario_id})
    elif accion == ACCION_APROBACION_DIRECTA:
        crear_notificacion_por_evento(EventoDesencadenador.APROBACION_DIRECTA_DOCUMENTO, archivo.id,
                                      contenido={'titulo': 'Documento Aprobado',
                                                 'mensaje': 'Tu solicitud para el documento '
                                                            + archivo.documento.nombre + ' ha sido aprobada',
                                                 'usuario': archivo.usuario_id})


def usuario_siguiente_cadena_aprobacion_detalle(archivo, usuario):
    """
    Retorna el detalle de la cadena de aprobacion del usuario siguiente con respecto al usuario actual.
    :exception: Si no existe un usuario siguiente, retorna una instancia vacia del detalle de la cadena de aprobación.
    :param archivo: Instancia del archivo que se está procesando
    :param usuario: Usuario actual, el cual está realizando la acción
    :return: Una instancia del detalle de la cadena de aprobación con el usuario siguiente.
    """
    detalle_cadena = CadenaAprobacionDetalle.objects.filter(cadena_aprobacion=archivo.cadena_aprobacion)\
        .order_by('orden')
    siguiente = False
    for usuario_cadena in detalle_cadena:
        if usuario_cadena.usuario == usuario and usuario_cadena != detalle_cadena.last() and not siguiente:
            siguiente = True
        elif siguiente:
            return usuario_cadena
        if usuario_cadena == detalle_cadena.last() and not siguiente:
            return CadenaAprobacionDetalle.objects.none()


class SolicitudesAprobacionDocumentoView(AbstractEvaLoggedView):
    def get(self, request):
        archivos = Archivo.objects.filter(usuario=request.user)\
            .exclude(estado=EstadoArchivo.OBSOLETO)

        procesos = Proceso.objects.filter(empresa_id=get_id_empresa_global(request)).order_by('nombre')
        return render(request, 'SGI/AprobacionDocumentos/solicitudes_aprobacion.html',
                      {'archivos': archivos,
                       'procesos': procesos,
                       'menu_actual': 'solicitudes_aprobacion',
                       'fecha': datetime.now()})


class DetalleSolicitudAprobacionView(AbstractEvaLoggedView):
    def get(self, request, id):
        archivos = ResultadosAprobacion.objects.filter(archivo_id=id).order_by('id')

        for archivo in archivos:
            if archivo.estado_id == EstadoArchivo.RECHAZADO:
                archivos = archivos.exclude(estado_id=EstadoArchivo.PENDIENTE)
                break

        return render(request, 'SGI/AprobacionDocumentos/detalle_solicitud_aprobacion.html',
                      {'archivos': archivos})


# region Métodos de ayuda

def datos_xa_render(opcion: str, request, cadena_aprobacion: CadenaAprobacionEncabezado = None, errores = None) -> dict:
    """
    Datos necesarios para la creación de los html de Cadena de aprobación.
    :param request: request del usuario
    :param opcion: valor de la acción a realizar 'crear' o 'editar'
    :return: Un diccionario con los datos.
    """
    procesos = Proceso.objects.filter(empresa_id=get_id_empresa_global(request)).order_by('nombre')
    colaboradores = Colaborador.objects.filter(estado=True).values(id_usuario=F('usuario_id'),
                                                                   nombre=F('usuario__first_name'),
                                                                   apellido=F('usuario__last_name')).order_by('nombre')
    contador = 1
    selecciones = ''
    if opcion == 'editar':
        detalle = CadenaAprobacionDetalle.objects.filter(cadena_aprobacion=cadena_aprobacion)
        if not Archivo.objects.filter(cadena_aprobacion=cadena_aprobacion):
            contador = detalle.count()
            selecciones = list(detalle.values('usuario_id', 'orden'))
        else:
            messages.warning(request, 'Solo es posible editar nombre y estado '
                                      'porque esta cadena de aprobación ya se encuentra en uso.')

    datos = {'opcion': opcion, 'cadena': cadena_aprobacion, 'procesos': procesos,
             'valores_selectores': json.dumps({'colaboradores': list(colaboradores),
                                               'contador': contador, 'opcion': opcion, 'selecciones': selecciones})}
    if errores:
        datos['errores'] = errores.message_dict
        if 'nombre' in errores.message_dict:
            for mensaje in errores.message_dict['nombre']:
                if mensaje.startswith('Ya existe'):
                    messages.warning(request, 'Ya existe una cadena de aprobación con ese nombre')
                    break
        return datos
    if cadena_aprobacion:
        datos['cadena'] = cadena_aprobacion
    return datos

# endregion
