
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db import IntegrityError
import os.path

from Administracion.models import Proceso
from EVA.views.index import AbstractEvaLoggedView
from SGI.models import Documento, GrupoDocumento, Archivo
from SGI.models.documentos import EstadoArchivo


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
        documento.version_actual = 0.00

        try:
            documento.full_clean(exclude=['cadena_aprobacion'])
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, documento, proceso=proceso, grupo_documento=grupo_documento)
            datos['errores'] = errores.message_dict
            if '__all__' in errores.message_dict:
                for mensaje in errores.message_dict['__all__']:
                    if mensaje.startswith('Ya existe'):
                        messages.warning(request, 'Ya existe un documento con código {0}'.format(documento.codigo))
                        break
            return render(request, 'SGI/documentos/crear-editar.html', datos)
        documento.save()
        messages.success(request, 'Se ha creado el documento {0} ' .format(documento.nombre))
        return redirect(reverse('SGI:documentos-index', args=[id_proceso]))


class DocumentosEditarView(AbstractEvaLoggedView):
    OPCION = 'editar'

    def get(self, request, id_documento, id_proceso, id_grupo):
        documento = Documento.objects.get(id=id_documento)
        proceso = Proceso.objects.get(id=id_proceso)
        grupo_documento = GrupoDocumento.objects.get(id=id_grupo)
        return render(request, 'SGI/documentos/crear-editar.html',
                      datos_xa_render(self.OPCION, proceso=proceso, grupo_documento=grupo_documento,
                                      documento=documento))

    def post(self, request,  id_proceso, id_grupo, id_documento):
        documento = Documento.from_dictionary(request.POST)
        proceso = Proceso.objects.get(id=id_proceso)
        grupo_documento = GrupoDocumento.objects.get(id=id_grupo)
        documento.grupo_documento_id = id_grupo
        documento.proceso_id = id_proceso
        documento.id = id_documento

        try:
            documento.full_clean(validate_unique=False, exclude=['cadena_aprobacion', 'version_actual'])
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, documento, proceso=proceso, grupo_documento=grupo_documento)
            datos['errores'] = errores.message_dict
            if '__all__' in errores.message_dict:
                for mensaje in errores.message_dict['__all__']:
                    if mensaje.startswith('Ya existe'):
                        messages.warning(request, 'Ya existe un documento con código {0}' .format(documento.codigo))
                        break
            return render(request, 'SGI/documentos/crear-editar.html', datos)

        documento_db = Documento.objects.get(id=id_documento)
        if documento_db.comparar(documento, excluir=['cadena_aprobacion', 'grupo_documento', 'proceso_id',
                                                     'version_actual']):
            messages.success(request, 'No se hicieron cambios en el documento {0}'.format(documento.nombre))
            return redirect(reverse('SGI:documentos-index', args=[id_proceso]))

        documento.save(update_fields=['nombre', 'codigo'])
        messages.success(request, 'Se ha actualizado el documento {0}' .format(documento.nombre))
        return redirect(reverse('SGI:documentos-index', args=[id_proceso]))


class DocumentosEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        try:
            documento = Documento.objects.get(id=id)
            documento.delete()
            messages.success(request, 'Se ha eliminado el documento {0}'.format(documento.nombre))
            return JsonResponse({"Mensaje": "OK"})

        except IntegrityError:
            return JsonResponse({"Mensaje": "Este documento no puede ser eliminado, porque tiene archivos asociados"})


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
        archivo = Archivo.from_dictionary(request.POST)
        archivo.estado_id = EstadoArchivo.APROBADO
        archivo.documento_id = id_documento
        archivo.documento.proceso.id = id_proceso
        archivo.documento.grupo_documento_id = id_grupo
        proceso = Proceso.objects.get(id=id_proceso)
        grupo_documento = GrupoDocumento.objects.get(id=id_grupo)
        documento = Documento.objects.get(id=id_documento)

        archivo.archivo = request.FILES.get('archivo', None)
        archivo_db = Archivo.objects.filter(documento_id=id_documento, estado=EstadoArchivo.APROBADO)
        if archivo_db:
            for archv in archivo_db:
                archv.estado_id = EstadoArchivo.OBSOLETO
                archv.save(update_fields=['estado_id'])

        try:
            archivo.full_clean(exclude=['cadena_aprobacion', 'hash'])
        except ValidationError as errores:
            datos = archivo_xa_render(self.OPCION, archivo, proceso, grupo_documento, documento)
            datos['errores'] = errores.message_dict
            if 'archivo' in errores.message_dict:
                for mensaje in errores.message_dict['archivo']:
                    if mensaje.startswith('Ya existe'):
                        messages.warning(request, 'Por favor cargue un archivo al documento {0}'
                                         .format(archivo.documento.nombre))
                        datos['errores'] = ''
                        break

            return redirect(reverse('SGI:documentos-index', args=[id_proceso]))
            return render(request, 'SGI/documentos/cargar-documento.html', datos)

        archivo.save()
        messages.success(request, 'Se ha cargado un archivo al documento {0}'.format(archivo.documento.nombre))
        return redirect(reverse('SGI:documentos-index', args=[id_proceso]))


class VerDocumentoView(AbstractEvaLoggedView):
    def get(self, request, id_documento, id_proceso):
        archivo = Archivo.objects.filter(documento_id=id_documento, estado_id=EstadoArchivo.APROBADO)
        if archivo:
            archivo = archivo.first()
            extension = os.path.splitext(archivo.archivo.url)[1]

            if extension == '.docx':
                mime_type = 'application/msword'
            elif extension == '.xlsx':
                mime_type = 'application/vnd.ms-excel'
            elif extension == '.pptx':
                mime_type = 'application/vnd.ms-powerpoint'
            else:
                mime_type = 'application/pdf'

            response = HttpResponse(archivo.archivo, content_type=mime_type)
            response['Content-Disposition'] = 'attachment; filename="%s"' % (archivo.documento.codigo + ' V' +
                                                                             str(archivo.documento.version_actual) +
                                                                             extension)

            return response
        else:
            return redirect(reverse('SGI:documentos-index', args=[id_proceso]))


# region Métodos de ayuda


def datos_xa_render(opcion: str = None, documento: Documento = None, proceso: Proceso = None,
                    grupo_documento: GrupoDocumento = None, archivo: Archivo = None) -> dict:
    """
    Datos necesarios para la creación de los html de Documento.
    :param opcion: valor de la acción a realizar 'crear' o 'editar'
    :param documento: Es opcional si se requiere pre cargar datos.
    :param proceso: Es opcional si se requiere pre cargar datos.
    :param grupo_documento: Es opcional si se requiere pre cargar datos.
    :param archivo: Es opcional si se requiere pre cargar datos.
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
    if archivo:
        datos['archivo'] = archivo

    return datos


def archivo_xa_render(opcion: str = None, archivo: Archivo = None, proceso: Proceso = None,
                      grupo_documento: GrupoDocumento = None, documento: Documento = None) -> dict:
    """
    Datos necesarios para la creación de los html de Documento.
    :param opcion: valor de la acción a realizar 'crear' o 'editar'
    :param archivo: Es opcional si se requiere pre cargar datos.
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
    if archivo:
        datos['archivo'] = archivo

    return datos

# endregion
