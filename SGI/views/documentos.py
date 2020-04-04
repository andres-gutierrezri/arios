
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db import IntegrityError
import os.path

from Administracion.models import Proceso
from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from SGI.models import Documento, GrupoDocumento, Archivo
from SGI.models.documentos import EstadoArchivo


class IndexView(AbstractEvaLoggedView):
    def get(self, request, id):
        empresa_id = get_id_empresa_global(request)
        procesos = Proceso.objects.filter(empresa_id=empresa_id).order_by('nombre')
        if procesos.filter(id=id):
            documentos = Documento.objects.filter(proceso_id=id, proceso__empresa_id=empresa_id).order_by('codigo')
            proceso = procesos.get(id=id)
            grupo_documentos = GrupoDocumento.objects.filter(empresa_id=empresa_id).order_by('nombre')
            return render(request, 'SGI/documentos/index.html', {'documentos': documentos, 'procesos': procesos,
                                                                 'grupo_documentos': grupo_documentos,
                                                                 'proceso': proceso
                                                                 })
        else:
            return redirect(reverse('SGI:index'))


class DocumentosCrearView(AbstractEvaLoggedView):
    OPCION = 'crear'

    def get(self, request, id_proceso, id_grupo):
        proceso = Proceso.objects.get(id=id_proceso)
        grupo_documento = GrupoDocumento.objects.get(id=id_grupo)
        return render(request, 'SGI/documentos/crear-editar.html',
                      datos_xa_render(self.OPCION, proceso=proceso, grupo_documento=grupo_documento,
                                      empresa=get_id_empresa_global(request)))

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
            datos = datos_xa_render(self.OPCION, documento, proceso=proceso, grupo_documento=grupo_documento,
                                    empresa=get_id_empresa_global(request))
            datos['errores'] = errores.message_dict
            if '__all__' in errores.message_dict:
                for mensaje in errores.message_dict['__all__']:
                    if mensaje.find("Código") > 0:
                        messages.warning(request, 'Ya existe un documento con código {0}'.format(documento.codigo))
                        break
                    elif mensaje.find('Nombre') > 0:
                        messages.warning(request, 'Ya existe un documento con nombre {0}'.format(documento.nombre))
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
                                      documento=documento, empresa=get_id_empresa_global(request)))

    def post(self, request,  id_proceso, id_grupo, id_documento):
        documento = Documento.from_dictionary(request.POST)
        documento.id = id_documento
        documento.grupo_documento_id = id_grupo
        documento.proceso_id = id_proceso
        proceso = Proceso.objects.get(id=id_proceso)
        grupo_documento = GrupoDocumento.objects.get(id=id_grupo)

        try:
            documento.clean_fields(exclude=['cadena_aprobacion', 'version_actual'])
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, documento, proceso=proceso, grupo_documento=grupo_documento,
                                    empresa=get_id_empresa_global(request))
            datos['errores'] = errores.message_dict

        documento_db = Documento.objects.get(id=id_documento)

        if documento_db.comparar(documento, campos=['nombre', 'codigo']):
            messages.success(request, 'No se hicieron cambios en el documento {0}'.format(documento.nombre))
            return redirect(reverse('SGI:documentos-index', args=[id_proceso]))

        documento_db.nombre = documento.nombre
        documento_db.codigo = documento.codigo

        try:
            documento_db.validate_unique()
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, documento, proceso=proceso, grupo_documento=grupo_documento,
                                    empresa=get_id_empresa_global(request))
            datos['errores'] = errores.message_dict
            if '__all__' in errores.message_dict:
                for mensaje in errores.message_dict['__all__']:
                    if 'Código' in mensaje:
                        messages.warning(request, 'Ya existe un documento con código {0}'.format(documento.codigo))
                        break
                    elif 'Nombre' in mensaje:
                        messages.warning(request, 'Ya existe un documento con nombre {0}'.format(documento.nombre))
                        break

            return render(request, 'SGI/documentos/crear-editar.html', datos)

        documento_db.save(update_fields=['nombre', 'codigo'])
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
            messages.error(request, 'Este documento no puede ser eliminado porque tiene archivos asociados')
            return JsonResponse({"Mensaje": "ERROR"})


class ArchivoCargarView(AbstractEvaLoggedView):
    OPCION = 'cargar'

    def get(self, request, id_proceso, id_grupo, id_documento):
        proceso = Proceso.objects.get(id=id_proceso)
        grupo_documento = GrupoDocumento.objects.get(id=id_grupo)
        documento = Documento.objects.get(id=id_documento)

        if documento.version_actual > 0:
            version = documento.version_minima_siguiente
        else:
            version = 1

        return render(request, 'SGI/documentos/cargar-documento.html',
                      datos_xa_render(self.OPCION, proceso=proceso, grupo_documento=grupo_documento,
                                      documento=documento, version=version, empresa=get_id_empresa_global(request)))

    def post(self, request, id_proceso, id_grupo, id_documento):
        archivo = Archivo.from_dictionary(request.POST)
        archivo.estado_id = EstadoArchivo.APROBADO
        archivo.documento_id = id_documento
        archivo.documento.proceso.id = id_proceso
        archivo.documento.grupo_documento_id = id_grupo
        documento = Documento.objects.get(id=id_documento)

        archivo.archivo = request.FILES.get('archivo', None)
        archivo_db = Archivo.objects.filter(documento_id=id_documento, estado=EstadoArchivo.APROBADO)
        if archivo_db:
            if float(archivo.version) <= documento.version_actual:
                messages.error(request, 'La versión del documento debe ser mayor a la actual {0}'
                               .format(documento.version_actual))
                return redirect(reverse('SGI:documentos-index', args=[id_proceso]))
            for archv in archivo_db:
                archv.estado_id = EstadoArchivo.OBSOLETO
                archv.save(update_fields=['estado_id'])

        try:
            archivo.full_clean(exclude=['cadena_aprobacion', 'hash'])
        except ValidationError as errores:
            if 'archivo' in errores.message_dict:
                for mensaje in errores.message_dict['archivo']:
                    if mensaje.startswith('Ya existe'):
                        messages.warning(request, 'Por favor cargue un archivo al documento {0}'
                                         .format(archivo.documento.nombre))
                        break
            else:
                messages.error(request, 'Ha ocurrido un error cargando el archivo')
            return redirect(reverse('SGI:documentos-index', args=[id_proceso]))

        archivo.save()
        documento.version_actual = archivo.version
        documento.save(update_fields=['version_actual'])
        messages.success(request, 'Se ha cargado un archivo al documento {0}'.format(archivo.documento.nombre))
        return redirect(reverse('SGI:documentos-index', args=[id_proceso]))


class VerDocumentoView(AbstractEvaLoggedView):
    def get(self, request, id):
        archivo = Archivo.objects.filter(id=id)

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
            response['Content-Disposition'] = 'inline; filename="{0} {1} v{2:.1f}{3}"'\
                .format(archivo.documento.codigo, archivo.documento.nombre,
                        archivo.documento.version_actual, extension)

            return response
        else:
            messages.warning(request, 'Este documento no tiene archivos disponibles')
            return redirect(reverse('SGI:documentos-index', args=[id_proceso]))


# region Métodos de ayuda


def datos_xa_render(opcion: str = None, documento: Documento = None, proceso: Proceso = None, empresa: int = None,
                    grupo_documento: GrupoDocumento = None, archivo: Archivo = None, version: float = 1) -> dict:
    """
    Datos necesarios para la creación de los html de Documento.
    :param opcion: valor de la acción a realizar 'crear' o 'editar'
    :param documento: Es opcional si se requiere pre cargar datos.
    :param proceso: Necesario para la ubicación del proceso al que pertenece el documento.
    :param grupo_documento: Necesario para la ubicación del grupo de documentos al que pertenece.
    :param archivo: Es opcional si se requiere pre cargar datos.
    :return: Un diccionario con los datos.
    """
    if empresa:
        procesos = Proceso.objects.filter(empresa_id=empresa).order_by('nombre')
    else:
        procesos = Proceso.objects.all().order_by('nombre')

    grupos_documentos = GrupoDocumento.objects.get_xa_select_activos().order_by('nombres')

    datos = {'procesos': procesos, 'grupos_documentos': grupos_documentos, 'opcion': opcion, 'version': version}
    if documento:
        datos['documento'] = documento
    if proceso:
        datos['proceso'] = proceso
    if grupo_documento:
        datos['grupo_documento'] = grupo_documento
    if archivo:
        datos['archivo'] = archivo
    if version:
        datos['version'] = version

    return datos

# endregion
