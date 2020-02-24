from django.shortcuts import render, redirect, reverse
from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib import messages

from Administracion.models import Proceso
from EVA.views.index import AbstractEvaLoggedView
from SGI.models import Documento, GrupoDocumento


class IndexView(AbstractEvaLoggedView):
    def get(self, request, id):
        documentos = Documento.objects.filter(proceso_id=id)
        procesos = Proceso.objects.all()
        proceso = Proceso.objects.get(id=id)
        grupo_documentos = GrupoDocumento.objects.all()
        return render(request, 'SGI/documentos/index.html', {'documentos': documentos, 'procesos': procesos,
                                                             'grupo_documentos': grupo_documentos, 'proceso': proceso})


class DocumentosCrearView(AbstractEvaLoggedView):
    OPCION = 'crear'

    def get(self, request, id_proceso, id_grupo):

        proceso = Proceso.objects.get(id=id_proceso)
        grupo_documento = GrupoDocumento.objects.get(id=id_grupo)
        return render(request, 'SGI/documentos/crear-editar.html',
                      datos_xa_render(self.OPCION, proceso=proceso, grupo_documento=grupo_documento,
                                      ))

    def post(self, request,  id_proceso, id_grupo):
        documento = Documento.from_dictionary(request.POST)
        proceso = Proceso.objects.get(id=id_proceso)
        grupo_documento = GrupoDocumento.objects.get(id=id_grupo)
        documento.grupo_documento_id = id_grupo
        documento.proceso_id = id_proceso

        try:
            documento.full_clean(exclude=['cadena_aprobacion'])
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, documento, proceso=proceso, grupo_documento=grupo_documento)
            datos['errores'] = errores.message_dict
            if '__all__' in errores.message_dict:
                for mensaje in errores.message_dict['__all__']:
                    if mensaje.startswith('Ya existe'):
                        messages.warning(request, 'Ya existe un documento con código {0} y versión {1}'
                                         .format(documento.codigo, documento.version))
                        break
            return render(request, 'SGI/documentos/crear-editar.html', datos)
        documento.save()
        messages.success(request, 'Se ha creado el documento {0} con versión {1}'
                         .format(documento.nombre, documento.version))
        return redirect(reverse('SGI:documentos-index', args=[id_proceso]))


class ArchivoCargarView(AbstractEvaLoggedView):
    OPCION = 'cargar'

    def get(self, request, id_proceso, id_grupo, id_documento):

        proceso = Proceso.objects.get(id=id_proceso)
        grupo_documento = GrupoDocumento.objects.get(id=id_grupo)
        documento = Documento.objects.get(id=id_documento)
        return render(request, 'SGI/documentos/cargar-documento.html',
                      datos_xa_render(self.OPCION, proceso=proceso, grupo_documento=grupo_documento,
                                      documento=documento))

    def post(self, request, id_proceso, id_grupo, id_documento):
        documento = Documento.from_dictionary(request.POST)
        documento.id = id_documento
        documento.proceso_id = id_proceso
        documento.grupo_documento_id = id_grupo
        proceso = Proceso.objects.get(id=id_proceso)
        grupo_documento = GrupoDocumento.objects.get(id=id_grupo)

        documento.archivo = request.FILES.get('archivo', None)
        print(documento.archivo)

        try:

            documento.full_clean(exclude=['nombre', 'codigo', 'version', 'cadena_aprobacion', 'id', 'fecha_creacion'])
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, documento, proceso, grupo_documento)
            datos['errores'] = errores.message_dict
            if 'archivo' in errores.message_dict:
                for mensaje in errores.message_dict['archivo']:
                    if mensaje.startswith('Ya existe'):
                        messages.warning(request, 'Por favor cargue un archivo al documento {0}'
                                         .format(documento.nombre))
                        datos['errores'] = ''
                        break
            return render(request, 'SGI/documentos/cargar-documento.html', datos)

        documento.save(update_fields=['archivo'])
        messages.success(request, 'Se ha cargado un archivo al documento {0}'.format(documento.nombre))
        return redirect(reverse('SGI:documentos-index', args=[id_proceso]))


# region Métodos de ayuda


def datos_xa_render(opcion: str = None, documento: Documento = None, proceso: Proceso = None,
                    grupo_documento: GrupoDocumento = None ) -> dict:
    """
    Datos necesarios para la creación de los html de Documento.
    :param opcion: valor de la acción a realizar 'crear' o 'editar'
    :param documento: Es opcional si se requiere pre cargar datos.
    :param proceso: Es opcional si se requiere pre cargar datos.
    :param grupo_documento: Es opcional si se requiere pre cargar datos.
    :return: Un diccionario con los datos.
    """
    procesos = Proceso.objects.get_x_estado(estado=True)
    grupos_documentos = GrupoDocumento.objects.get_xa_select_activos()

    datos = {'procesos': procesos, 'grupos_documentos': grupos_documentos, 'opcion': opcion}
    if documento:
        datos['documento'] = documento
    if proceso:
        datos['proceso'] = proceso
    if grupo_documento:
        datos['grupo_documento'] = grupo_documento

    return datos

# endregion
