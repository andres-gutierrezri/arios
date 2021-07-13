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
from GestionDocumental.views import views, consecutivo_documento, consecutivo_contrato, consecutivo_reunion, \
    consecutivo_requerimientos, consecutivo_plantrabajo, consecutivo_viaticoscomisiones, consecutivo_ordenes, \
    consecutivo_actas_contratos

app_name = 'GestionDocumental'

urlpatterns = [
    path('index/', views.PrincipalView.as_view(), name='index'),
    path('consecutivo-oficios/<int:id>/index', consecutivo_documento.ConsecutivoOficiosView.as_view(),
         name='consecutivo-oficios-index'),
    path('consecutivo-oficios/add', consecutivo_documento.ConsecutivoOficiosCrearView.as_view(),
         name='consecutivo-oficios-crear'),
    path('consecutivo-oficios/<int:id>/editar', consecutivo_documento.ConsecutivoOficioEditarView.as_view(),
         name='consecutivo-oficios-editar'),
    path('consecutivo-oficios/<int:id>/delete', consecutivo_documento.ConsecutivoOficiosEliminarView.as_view(),
         name='consecutivo-oficios-eliminar'),
    path('consecutivo-contratos/<int:id>/index', consecutivo_contrato.ConsecutivoContratoView.as_view(),
         name='consecutivo-contratos-index'),
    path('consecutivo-contratos/add', consecutivo_contrato.ConsecutivoContratoCrearView.as_view(),
         name='consecutivo-contratos-crear'),
   path('consecutivo-contratos/<int:id_contrato>/editar', consecutivo_contrato.ConsecutivoContratoEditarView.as_view(),
         name='consecutivo-contratos-editar'),
    path('consecutivo-contratos/<int:id>/delete', consecutivo_contrato.ConsecutivoContratoEliminarView.as_view(),
         name='consecutivo-contratos-eliminar'),
    path('consecutivo-contratos/<int:id_contrato>/cargar', consecutivo_contrato.ArchivoCargarView.as_view(),
         name='consecutivo-contratos-cargar'),
    path('consecutivo-contratos/<int:id_contrato>/ver', consecutivo_contrato.VerArchivoView.as_view(),
         name='consecutivo-contratos-ver'),
    path('consecutivo-reuniones/<int:id>/index', consecutivo_reunion.ConsecutivoReunionView.as_view(),
         name='consecutivo-reuniones-index'),
    path('consecutivo-reuniones/add', consecutivo_reunion.ConsecutivoReunionesCrearView.as_view(),
         name='consecutivo-reuniones-crear'),
    path('consecutivo-reuniones/<int:id_reunion>/editar', consecutivo_reunion.ConsecutivoReunionesEditarView.as_view(),
         name='consecutivo-reuniones-editar'),
    path('consecutivo-reuniones/<int:id>/delete', consecutivo_reunion.ConsecutivoReunionesEliminarView.as_view(),
         name='consecutivo-reuniones-eliminar'),
    path('consecutivo-requerimientos/<int:id>/index', consecutivo_requerimientos.ConsecutivoRequerimientoView.as_view(),
         name='consecutivo-requerimientos-index'),
    path('consecutivo-requerimientos/add', consecutivo_requerimientos.ConsecutivoRequerimientoCrearView.as_view(),
         name='consecutivo-requerimientos-crear'),
    path('consecutivo-requerimientos/<int:id>/editar', consecutivo_requerimientos.
         ConsecutivoRequerimientoEditarView.as_view(), name='consecutivo-requerimientos-editar'),
    path('consecutivo-requerimientos/<int:id>/delete', consecutivo_requerimientos.
         ConsecutivoRequerimientoEliminarView.as_view(), name='consecutivo-requerimientos-delete'),
    path('consecutivo-plantrabajo/<int:id>/index', consecutivo_plantrabajo.ConsecutivoPlanTrabajoView.as_view(),
         name='consecutivo-plantrabajo-index'),
    path('consecutivo-plantrabajo/add', consecutivo_plantrabajo.ConsecutivoPlanTrabajoCrearView.as_view(),
         name='consecutivo-plantrabajo-crear'),
    path('consecutivo-plantrabajo/<int:id>/editar', consecutivo_plantrabajo.ConsecutivoPlanTrabajoEditarView.as_view(),
         name='consecutivo-plantrabajo-editar'),
    path('consecutivo-plantrabajo/<int:id>/delete', consecutivo_plantrabajo.ConsecutivoPlanTrabajoEliminarView.as_view(),
         name='consecutivo-plantrabajo-delete'),
    path('consecutivo-viaticoscomisiones/<int:id>/index', consecutivo_viaticoscomisiones.
         ConsecutivoViaticosComisionesView.as_view(), name='consecutivo-viaticoscomisiones-index'),
    path('consecutivo-viaticoscomisiones/add', consecutivo_viaticoscomisiones.
         ConsecutivoViaticosComisioneCrearView.as_view(), name='consecutivo-viaticoscomisiones-crear'),
    path('consecutivo-viaticoscomisiones/<int:id>/editar', consecutivo_viaticoscomisiones.
         ConsecutivoViaticosComisioneEditarView.as_view(),name='consecutivo-viaticoscomisiones-editar'),
    path('consecutivo-viaticoscomisiones/<int:id>/delete', consecutivo_viaticoscomisiones.
         ConsecutivoViaticosComisioneEliminarView.as_view(), name='consecutivo-viaticoscomisiones-delete'),
    path('consecutivo-ordenestrabajo/<int:id>/index', consecutivo_ordenes.ConsecutivoOrdenesTrabajoView.as_view(),
         name='consecutivo-ordenestrabajo-index'),
    path('consecutivo-ordenestrabajo/add', consecutivo_ordenes.ConsecutivoOrdenesTrabajoCrearView.as_view(),
         name='consecutivo-ordenestrabajo-crear'),
    path('consecutivo-ordenestrabajo/<int:id>/editar', consecutivo_ordenes.ConsecutivoOrdenesTrabajoEditarView.as_view(),
         name='consecutivo-ordenestrabajo-editar'),
    path('consecutivo-ordenestrabajo/<int:id>/delete', consecutivo_ordenes.ConsecutivoOrdenesTrabajoEliminarView.as_view(),
         name='consecutivo-ordenestrabajo-delete')
         name='consecutivo-ordenestrabajo-delete'),
    path('consecutivo-actascontratos/<int:id>/index', consecutivo_actas_contratos.ConsecutivoActasContratosView.as_view(),
         name='consecutivo-actascontratos-index'),
]
