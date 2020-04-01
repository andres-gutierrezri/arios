import json
from datetime import datetime

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError

from Administracion.models import Proceso
from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from SGI.models import CadenaAprobacionEncabezado
from SGI.models.documentos import CadenaAprobacionDetalle, Archivo
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

        cadena = CadenaAprobacionEncabezado()
        cadena.nombre = request.POST.get('nombre', '')
        cadena.empresa_id = get_id_empresa_global(request)
        cadena.fecha_creacion = datetime.today()
        cadena.estado = True

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
            usuarios_seleccionados = request.POST.get('ultimo_usuario', '')[0]

        cadena = CadenaAprobacionEncabezado(id=id)
        cadena.nombre = request.POST.get('nombre', '')
        cadena.empresa_id = get_id_empresa_global(request)
        cadena.fecha_creacion = datetime.today()
        cadena.estado = request.POST.get('estado', 'False') == 'True'

        try:
            cadena.full_clean(validate_unique=False)
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

        CadenaAprobacionDetalle.objects.filter(cadena_aprobacion=cadena).delete()

        cadena.save()
        orden = 1
        for usuarios in usuarios_seleccionados:
            CadenaAprobacionDetalle.objects.create(cadena_aprobacion=cadena, usuario_id=usuarios, orden=orden)
            orden += 1

        messages.success(request, 'Se ha actualizado la cadena de aprobación {0}'.format(cadena.nombre))
        return redirect(reverse('SGI:cadenas-aprobacion-ver'))


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
