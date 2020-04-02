import json
from datetime import datetime

from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError

from Administracion.models import Proceso
from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from SGI.models import CadenaAprobacionEncabezado
from SGI.models.documentos import CadenaAprobacionDetalle, Archivo, ResultadosAprobacion, EstadoArchivo
from TalentoHumano.models import Colaborador


class CadenaAprobacionView(AbstractEvaLoggedView):
    def get(self, request):
        cadenas_aprobacion = CadenaAprobacionEncabezado.objects.all()
        detalles = CadenaAprobacionDetalle.objects.all()
        fecha = datetime.now()
        procesos = Proceso.objects.filter(empresa_id=get_id_empresa_global(request)).order_by('nombre')
        return render(request, 'SGI/CadenasAprobacion/index.html', {'cadenas_aprobacion': cadenas_aprobacion,
                                                                    'detalles': detalles,
                                                                    'fecha': fecha,
                                                                    'menu_actual': 'cadenas_aprobacion',
                                                                    'procesos': procesos})


class CadenaAprobacionCrearView(AbstractEvaLoggedView):
    OPCION = 'crear'

    def get(self, request):
        return render(request, 'SGI/CadenasAprobacion/crear-editar.html', datos_xa_render(self.OPCION, request))

    def post(self, request):
        usuarios_seleccionados = request.POST.get('usuarios_seleccionados', '').split(',')
        if usuarios_seleccionados[0]:
            usuarios_seleccionados.append(request.POST.get('ultimo_usuario', '')[0])
        else:
            usuarios_seleccionados = request.POST.get('ultimo_usuario', '')

        cadena = CadenaAprobacionEncabezado.from_dictionary(request.POST)
        cadena.empresa_id = get_id_empresa_global(request)
        cadena.estado = True
        cadena.fecha_creacion = datetime.today()

        try:
            cadena.full_clean()
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, request, cadena)
            datos['errores'] = errores.message_dict
            if 'nombre' in errores.message_dict:
                for mensaje in errores.message_dict['nombre']:
                    if mensaje.startswith('Ya existe'):
                        messages.warning(request,
                                         'Ya existe una cadena de aprobación con ese nombre {0}'.format(cadena.nombre))
                        break
            return render(request, 'SGI/CadenasAprobacion/crear-editar.html', datos)
        cadena.save()

        orden = 1
        for usuarios in usuarios_seleccionados:
            CadenaAprobacionDetalle.objects.create(cadena_aprobacion=cadena, usuario_id=usuarios, orden=orden)
            orden += 1

        messages.success(request, 'Se ha agregado la cadena de aprobación {0}'.format(cadena.nombre))
        return redirect(reverse('SGI:cadenas-aprobacion-ver'))


class CadenaAprobacionEditarView(AbstractEvaLoggedView):
    OPCION = 'editar'

    def get(self, request, id):
        cadena = CadenaAprobacionEncabezado.objects.get(id=id)
        return render(request, 'SGI/CadenasAprobacion/crear-editar.html', datos_xa_render(self.OPCION, request, cadena))

    def post(self, request, id):
        usuarios_seleccionados = request.POST.get('usuarios_seleccionados', '').split(',')
        if usuarios_seleccionados[0]:
            usuarios_seleccionados.append(request.POST.get('ultimo_usuario', '')[0])
        else:
            usuarios_seleccionados = request.POST.get('ultimo_usuario', '')

        cadena = CadenaAprobacionEncabezado.from_dictionary(request.POST)
        cadena.id = id

        try:
            cadena.full_clean(validate_unique=False, exclude=['empresa', 'fecha_creacion'])
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, request, cadena)
            datos['errores'] = errores.message_dict
            if 'nombre' in errores.message_dict:
                for mensaje in errores.message_dict['nombre']:
                    if mensaje.startswith('Ya existe'):
                        messages.warning(request,
                                         'Ya existe una cadena de aprobación con ese nombre {0}'.format(cadena.nombre))
                        break
            return render(request, 'SGI/CadenasAprobacion/crear-editar.html', datos)
        if usuarios_seleccionados:
            CadenaAprobacionDetalle.objects.filter(cadena_aprobacion=cadena).delete()

        cadena.save(update_fields=['nombre', 'estado'])
        orden = 1
        for usuarios in usuarios_seleccionados:
            CadenaAprobacionDetalle.objects.create(cadena_aprobacion=cadena, usuario_id=usuarios, orden=orden)
            orden += 1

        messages.success(request, 'Se ha actualizado la cadena de aprobación {0}'.format(cadena.nombre))
        return redirect(reverse('SGI:cadenas-aprobacion-ver'))


class CadenaAprobacionEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        try:
            if Archivo.objects.filter(cadena_aprobacion=CadenaAprobacionEncabezado.objects.get(id=id)):
                return JsonResponse({"Mensaje": "ERROR-CADENA"})

            CadenaAprobacionDetalle.objects.filter(cadena_aprobacion_id=id).delete()
            cadena_encabezado = CadenaAprobacionEncabezado.objects.get(id=id)
            cadena_encabezado.delete()
            messages.success(request, 'Se ha eliminado la cadena de aprobación {0}'.format(cadena_encabezado.nombre))
            return JsonResponse({"Mensaje": "OK"})

        except IntegrityError:
            return JsonResponse({"Mensaje": "ERROR-CADENA"})


class AprobacionDocumentoView(AbstractEvaLoggedView):
    def get(self, request):
        usuario = Colaborador.objects.get(usuario=request.user)
        archivos = ResultadosAprobacion.objects.filter(usuario=usuario, usuario_anterior=EstadoArchivo.APROBADO,
                                                       estado=EstadoArchivo.PENDIENTE)
        procesos = Proceso.objects.filter(empresa_id=get_id_empresa_global(request)).order_by('nombre')
        fecha = datetime.now()
        return render(request, 'SGI/AprobacionDocumentos/index.html', {'archivos': archivos,
                                                                       'procesos': procesos,
                                                                       'menu_actual': 'aprobacion_documentos',
                                                                       'fecha': fecha})


class AccionDocumentoView(AbstractEvaLoggedView):
    def get(self, request, id):
        documento = Archivo.objects.get(resultadosaprobacion=id)
        opciones = [{'texto': 'Aprobado', 'valor': EstadoArchivo.APROBADO},
                    {'texto': 'Rechazado', 'valor': EstadoArchivo.RECHAZADO}]
        return render(request, 'SGI/AprobacionDocumentos/accion_documento.html', {'documento': documento,
                                                                                  'opciones': opciones})

    def post(self, request, id):
        comentario = request.POST.get('comentario', '')
        opcion = request.POST.get('opcion', '')
        usuario_colaborador = Colaborador.objects.get(usuario=request.user)
        resultado = ResultadosAprobacion.objects.get(archivo_id=id, usuario=usuario_colaborador)
        resultado.estado = opcion
        resultado.comentario = comentario
        resultado.save(update_fields=['estado', 'comentario'])

        cadena = CadenaAprobacionDetalle.objects.filter(cadena_aprobacion__archivo__resultadosaprobacion=resultado).order_by('orden')
        if int(opcion) == EstadoArchivo.APROBADO:
            siguiente = False
            for usuario in cadena:
                if usuario.usuario == usuario_colaborador and usuario != cadena.last() and not siguiente:
                    siguiente = True
                elif siguiente:
                    usuario_siguiente = ResultadosAprobacion.objects.get(usuario=usuario.usuario, archivo_id=id)
                    usuario_siguiente.usuario_anterior = EstadoArchivo.APROBADO
                    usuario_siguiente.save(update_fields=['usuario_anterior'])
                    break
                if usuario == cadena.last() and not siguiente:
                    archivo_nuevo = Archivo(id=id)
                    archivo_nuevo.estado_id = EstadoArchivo.APROBADO
                    archivo_nuevo.save(update_fields=['estado'])
                    archivo_anterior = Archivo.objects.filter(documento=archivo_nuevo.documento,
                                                              estado=EstadoArchivo.APROBADO)
                    if archivo_anterior:
                        archivo_anterior[0].estado = EstadoArchivo.OBSOLETO
                        archivo_anterior[0].save(update_fields=['estado'])
        else:
            otros_usuarios = ResultadosAprobacion.objects.filter(archivo_id=id, estado=EstadoArchivo.PENDIENTE)
            for otro_usuario in otros_usuarios:
                otro_usuario = ResultadosAprobacion(id=otro_usuario.id)
                otro_usuario.usuario_anterior = EstadoArchivo.RECHAZADO
                otro_usuario.estado = EstadoArchivo.RECHAZADO
                otro_usuario.comentario = 'Rechazado por el usuario {0}'.format(usuario_colaborador.usuario.first_name)
                otro_usuario.save(update_fields=['usuario_anterior', 'estado', 'comentario'])

        return redirect(reverse('SGI:aprobacion-documentos-ver'))


# region Métodos de ayuda

def datos_xa_render(opcion: str, request, cadena_aprobacion: CadenaAprobacionEncabezado = None) -> dict:
    """
    Datos necesarios para la creación de los html de Cadena de aprobación.
    :param request: request del usuario
    :param opcion: valor de la acción a realizar 'crear' o 'editar'
    :return: Un diccionario con los datos.
    """
    procesos = Proceso.objects.filter(empresa_id=get_id_empresa_global(request)).order_by('nombre')
    colaboradores = Colaborador.objects.get_xa_select_activos()
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

    if cadena_aprobacion:
        datos['cadena'] = cadena_aprobacion
    return datos

# endregion
