from django.shortcuts import render
from Administracion.models import Proceso
from Administracion.utils import get_id_empresa_global
from EVA.views.index import AbstractEvaLoggedView
from SGI.models import Documento, GrupoDocumento, Archivo
from SGI.models.documentos import EstadoArchivo, ResultadosAprobacion


class Index(AbstractEvaLoggedView):
    def get(self, request):
        procesos = Proceso.objects.filter(empresa_id=get_id_empresa_global(request)).order_by('nombre')
        return render(request, 'SGI/index.html', {'procesos': procesos})


class BuscarDocumentos(AbstractEvaLoggedView):
    def post(self, request):
        texto_busqueda = request.POST.get('texto_busqueda', '')
        documentos = Documento.objects.filter(nombre__icontains=texto_busqueda)
        procesos = Proceso.objects.filter(empresa_id=get_id_empresa_global(request)).order_by('nombre')
        grupos_documentos = GrupoDocumento.objects.filter(es_general=False)
        grupos_documentos_generales = GrupoDocumento.objects.filter(es_general=True)
        lista_datos = []
        for pro in procesos:
            lista_grupos = armar_documentos(documentos, grupos_documentos, pro)
            if lista_grupos:
                lista_datos.append({'proceso': pro, 'grupos': lista_grupos})

        lista_grupos_generales = armar_documentos(documentos, grupos_documentos_generales, None)
        if lista_grupos_generales:
            lista_datos.append({'proceso': 'General', 'grupos': lista_grupos_generales})

        # empresa_id = get_id_empresa_global(request)

        archivos = Archivo.objects.filter(documento__nombre__icontains=texto_busqueda, estado_id=EstadoArchivo.APROBADO)
        historial = Archivo.objects.filter(documento__nombre__icontains=texto_busqueda).order_by('-version') \
            .exclude(estado_id=EstadoArchivo.PENDIENTE)
        resultados = ResultadosAprobacion.objects.exclude(estado_id=EstadoArchivo.PENDIENTE)

        # Union de documentos de grupos de documento generales.

        # documentos |= Documento.objects.filter(grupo_documento__es_general=True,
        #                                        grupo_documento__empresa_id=empresa_id)
        # archivos |= Archivo.objects.filter(documento__grupo_documento__es_general=True,
        #                                    documento__grupo_documento__empresa_id=empresa_id,
        #                                    estado_id=EstadoArchivo.APROBADO)
        # historial |= Archivo.objects.filter(documento__grupo_documento__es_general=True,
        #                                     documento__grupo_documento__empresa_id=empresa_id).order_by('-version') \
        #     .exclude(estado_id=EstadoArchivo.PENDIENTE)

        return render(request, 'SGI/documentos/resultado-busqueda-documentos.html',
                      {'procesos': procesos,
                       'procesos_grupos_documentos': lista_datos,
                       'texto_busqueda': texto_busqueda,
                       'archivos': archivos,
                       'historial': historial,
                       'resultados': resultados,
                       'estado': EstadoArchivo,
                       'menu_actual': 'busqueda',
                       })


def armar_documentos(documentos, grupos_documentos, proceso: None):
    lista_grupos = []
    for gru in grupos_documentos:
        lista_documentos = []
        for doc in documentos:
            if proceso == doc.proceso and gru == doc.grupo_documento:
                lista_documentos.append({'documento': doc})
            elif gru == doc.grupo_documento and not proceso:
                lista_documentos.append({'documento': doc})
        if lista_documentos:
            lista_grupos.append({'grupo': gru, 'documentos': lista_documentos})
    return lista_grupos
