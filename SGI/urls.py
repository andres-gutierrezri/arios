"""EVA URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from SGI.views import sgi, documentos, cadena_aprobacion
from SGI.views.reportes import ReportesDescargarView, ReportesView

app_name = 'SGI'

urlpatterns = [
    path('index/', sgi.Index.as_view(), name='index'),
    path('procesos/<int:id>/grupos-documentos', documentos.IndexView.as_view(), name='documentos-index'),
    path('procesos/<int:id_proceso>/grupos-documentos/<int:id_grupo>/documentos/add',
         documentos.DocumentosCrearView.as_view(), name='documentos-crear'),
    path('procesos/<int:id_proceso>/grupos-documentos/<int:id_grupo>/documentos/<int:id_documento>/cargar',
         documentos.ArchivoCargarView.as_view(), name='documentos-cargar'),
    path('procesos/ver-documento/<int:id>', documentos.VerDocumentoView.as_view(), name='documentos-ver'),
    path('procesos/<int:id_proceso>/grupos-documentos/<int:id_grupo>/documentos/<int:id_documento>',
         documentos.DocumentosEditarView.as_view(), name='documentos-editar'),
    path('documentos/<int:id>/delete', documentos.DocumentosEliminarView.as_view(), name='documentos-eliminar'),
    path('documentos/archivo/<int:id>/delete', documentos.ArchivosEliminarView.as_view(), name='archivos-eliminar'),
    path('cadenas_aprobacion', cadena_aprobacion.CadenaAprobacionView.as_view(), name='cadenas-aprobacion-ver'),
    path('cadenas_aprobacion/add', cadena_aprobacion.CadenaAprobacionCrearView.as_view(),
         name='cadenas-aprobacion-crear'),
    path('cadenas_aprobacion/<int:id>', cadena_aprobacion.CadenaAprobacionEditarView.as_view(),
         name='cadenas-aprobacion-editar'),
    path('cadenas_aprobacion/<int:id>/delete', cadena_aprobacion.CadenaAprobacionEliminarView.as_view(),
         name='cadenas-aprobacion-eliminar'),
    path('cadenas_aprobacion/detalle/<int:id>', cadena_aprobacion.CadenaAprobacionDetalleView.as_view(),
         name='cadenas-aprobacion-detalle'),
    path('aprobacion_documentos', cadena_aprobacion.AprobacionDocumentoView.as_view(),
         name='aprobacion-documentos-ver'),
    path('aprobacion_documentos/<int:id>', cadena_aprobacion.AccionAprobacionDocumentosView.as_view(),
         name='aprobacion-documentos-accion'),
    path('solicitudes_aprobacion', cadena_aprobacion.SolicitudesAprobacionDocumentoView.as_view(),
         name='solicitudes-aprobacion'),
    path('solicitudes_aprobacion/detalle/<int:id>', cadena_aprobacion.DetalleSolicitudAprobacionView.as_view(),
         name='detalle-solicitud-aprobacion'),
    path('documentos/buscar', sgi.BuscarDocumentos.as_view(), name='documentos-buscar'),
    path('reportes', ReportesView.as_view(), name='reportes'),
    path('reportes/<int:id>/formato/<str:formato>', ReportesDescargarView.as_view(), name='reportes-descarga'),
]
