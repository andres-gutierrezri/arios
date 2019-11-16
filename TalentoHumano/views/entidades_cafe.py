from datetime import datetime

from django.db import IntegrityError
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.core.exceptions import ValidationError

from TalentoHumano.models import EntidadesCAFE, TipoEntidadesCAFE


def index(request):
    entidades_cafe = EntidadesCAFE.objects.all()
    tipos_entidades = TipoEntidadesCAFE.objects.get_xa_select_activos()
    fecha = datetime.now()
    return render(request, 'TalentoHumano/Entidades_CAFE/index.html', {'entidades_cafe': entidades_cafe,
                                                                       'fecha': fecha,
                                                                       'tipos_entidades': tipos_entidades})


class EntidadCAFECrearView(View):
    OPCION = 'crear'

    def get(self, request):
        return render(request, 'TalentoHumano/Entidades_CAFE/crear-editar.html', datos_xa_render(self.OPCION))

    def post(self, request):
        entidad_cafe = EntidadesCAFE.from_dictionary(request.POST)
        try:
            entidad_cafe.full_clean()
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, entidad_cafe)
            datos['errores'] = errores.message_dict
            return render(request, 'TalentoHumano/Entidades_CAFE/crear-editar.html', datos)

        if EntidadesCAFE.objects.filter(nombre__iexact=entidad_cafe.nombre).exists():
            messages.warning(request, 'Ya existe una entidad con nombre {0}'.format(entidad_cafe.nombre))
            return render(request, 'TalentoHumano/Entidades_CAFE/crear-editar.html',
                          datos_xa_render(self.OPCION, entidad_cafe))

        entidad_cafe.save()
        messages.success(request, 'Se ha agregado la entidad {0}'.format(entidad_cafe.nombre))
        return redirect(reverse('TalentoHumano:entidades-index'))


class EntidadCAFEEditarView(View):
    OPCION = 'editar'

    def get(self, request, id):
        entidad_cafe = EntidadesCAFE.objects.get(id=id)
        return render(request, 'TalentoHumano/Entidades_CAFE/crear-editar.html', datos_xa_render(self.OPCION,
                                                                                                 entidad_cafe))

    def post(self, request, id):
        update_fields = ['tipo_entidad_id', 'nombre', 'direccion', 'nombre_contacto', 'telefono_contacto',
                         'correo', 'direccion_web']

        entidad_cafe = EntidadesCAFE.from_dictionary(request.POST)
        entidad_cafe.id = int(id)

        try:
            entidad_cafe.full_clean(validate_unique=False)
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, entidad_cafe)
            datos['errores'] = errores.message_dict
            return render(request, 'TalentoHumano/Entidades_CAFE/crear-editar.html', datos)

        if EntidadesCAFE.objects.filter(nombre=entidad_cafe.nombre).lower.exclude(id=id).exists():
            messages.warning(request, 'Ya existe una entidad con nombre {0}'.format(entidad_cafe.nombre))
            return render(request, 'TalentoHumano/Entidades_CAFE/crear-editar.html', datos_xa_render(self.OPCION,
                                                                                                     entidad_cafe))

        entidad_cafe_db = EntidadesCAFE.objects.get(id=id)
        if entidad_cafe_db.comparar(entidad_cafe):
            messages.success(request, 'No se hicieron cambios en la entidad {0}'.format(entidad_cafe.nombre))
            return redirect(reverse('TalentoHumano:entidades-index'))

        else:

            entidad_cafe.save(update_fields=update_fields)
            messages.success(request, 'Se ha actualizado la entidad {0}'.format(entidad_cafe.nombre))

            return redirect(reverse('TalentoHumano:entidades-index'))

#
# class TerceroEliminarView(View):
#     def post(self, request, id):
#         try:
#             tercero = Tercero.objects.get(id=id)
#             tercero.delete()
#             messages.success(request, 'Se ha eliminado el tercero {0}'.format(tercero.nombre))
#             return JsonResponse({"Mensaje": "OK"})
#
#         except IntegrityError:
#             tercero = Tercero.objects.get(id=id)
#             messages.warning(request, 'No se puede eliminar el tercero {0}'.format(tercero.nombre) +
#                              ' porque ya se encuentra asociado a otros módulos')
#             return JsonResponse({"Mensaje": "No se puede eliminar"})

# region Métodos de ayuda


def datos_xa_render(opcion: str, entidad: EntidadesCAFE = None) -> dict:
    """
    Datos necesarios para la creación de los html de Entidades CAFE.
    :param opcion: valor de la acción a realizar 'crear' o 'editar'
    :param entidad: Es opcional si se requiere pre cargar datos.
    :return: Un diccionario con los datos.
    """

    tipos_entidades = TipoEntidadesCAFE.objects.get_xa_select_activos()

    datos = {'tipos_entidades': tipos_entidades, 'opcion': opcion}

    if entidad:
        datos['entidad_cafe'] = entidad

    return datos
# endregion
