from datetime import datetime
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError

from EVA.views.index import AbstractEvaLoggedView
from Notificaciones.models.models import EventoDesencadenador
from Notificaciones.views.views import crear_notificacion_por_evento
from TalentoHumano.models import EntidadesCAFE, TipoEntidadesCAFE


class EntidadCAFEIndexView(AbstractEvaLoggedView):
    def get(self, request, id_entidad):
        id_entidad = int(id_entidad)
        entidades_cafe = EntidadesCAFE.objects.all() if id_entidad == 0 else \
            EntidadesCAFE.objects.filter(tipo_entidad_id=id_entidad)
        return render(request, 'TalentoHumano/Entidades_CAFE/index.html', {'entidades_cafe': entidades_cafe,
                                                                           'fecha': datetime.now(),
                                                                           'tipos_entidades': tipos_entidades_filtro,
                                                                           'id_entidad': id_entidad,
                                                                           'menu_actual': 'entidades-cafe'})


class EntidadCAFECrearView(AbstractEvaLoggedView):
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
            messages.warning(request, 'Ya existe una  {0}'.format(entidad_cafe.tipo_entidad) + ' con nombre {0}'
                             .format(entidad_cafe.nombre))
            return render(request, 'TalentoHumano/Entidades_CAFE/crear-editar.html',
                          datos_xa_render(self.OPCION, entidad_cafe))

        entidad_cafe.save()
        crear_notificacion_por_evento(EventoDesencadenador.ENTIDADES_CAFE, entidad_cafe.id, entidad_cafe.nombre)
        messages.success(request, 'Se ha agregado la  {0}'.format(entidad_cafe.tipo_entidad) + ' ' +
                         '{0}'.format(entidad_cafe.nombre))
        return redirect(reverse('TalentoHumano:entidades-cafe-index', args=[0]))


class EntidadCAFEEditarView(AbstractEvaLoggedView):
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

        if EntidadesCAFE.objects.filter(nombre__iexact=entidad_cafe.nombre).exclude(id=id).exists():
            messages.warning(request, 'Ya existe una  {0}'.format(entidad_cafe.tipo_entidad) + ' con nombre {0}'
                             .format(entidad_cafe.nombre))
            return render(request, 'TalentoHumano/Entidades_CAFE/crear-editar.html', datos_xa_render(self.OPCION,
                                                                                                     entidad_cafe))

        entidad_cafe_db = EntidadesCAFE.objects.get(id=id)
        if entidad_cafe_db.comparar(entidad_cafe):
            messages.success(request, 'No se hicieron cambios en la  {0}'.format(entidad_cafe.tipo_entidad) + ' ' +
                             '{0}'.format(entidad_cafe.nombre))
            return redirect(reverse('TalentoHumano:entidades-cafe-index', args=[0]))

        else:

            entidad_cafe.save(update_fields=update_fields)
            messages.success(request, 'Se ha actualizado la  {0}'.format(entidad_cafe.tipo_entidad) + ' ' +
                             '{0}'.format(entidad_cafe.nombre))

            return redirect(reverse('TalentoHumano:entidades-cafe-index', args=[0]))


class EntidadCAFEEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        entidad_cafe = EntidadesCAFE.objects.get(id=id)
        try:
            entidad_cafe.delete()
            messages.success(request, 'Se ha eliminado la  {0}'.format(entidad_cafe.tipo_entidad) + ' ' +
                             '{0}'.format(entidad_cafe.nombre))
            return JsonResponse({"estado": "OK"})

        except IntegrityError:
            return JsonResponse({"estado": "error",
                                 "mensaje": "No se puede eliminar la {0} {1} porque ya "
                                            "se encuentra asociado a otro módulo".format(entidad_cafe.tipo_entidad,
                                                                                         entidad_cafe.nombre)})

# region Métodos de ayuda


def datos_xa_render(opcion: str, entidad: EntidadesCAFE = None) -> dict:
    """
    Datos necesarios para la creación de los html de Entidades CAFE.
    :param opcion: valor de la acción a realizar 'crear' o 'editar'
    :param entidad: Es opcional si se requiere pre cargar datos.
    :return: Un diccionario con los datos.
    """

    tipos_entidades = TipoEntidadesCAFE.objects.get_xa_select_activos()

    datos = {'tipos_entidades': tipos_entidades, 'opcion': opcion, 'menu_actual': 'entidades-cafe'}

    if entidad:
        datos['entidad_cafe'] = entidad

    return datos
# endregion


def tipos_entidades_filtro():
    tipo_entidades = TipoEntidadesCAFE.objects.filter(estado=True)
    lista_tipo_entidades = [{'campo_valor': 0, 'campo_texto': 'Todos'}]
    for tipo_entidad in tipo_entidades:
        lista_tipo_entidades.append({'campo_valor': tipo_entidad.id, 'campo_texto': tipo_entidad.nombre})

    return lista_tipo_entidades
