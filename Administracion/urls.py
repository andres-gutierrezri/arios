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
from Administracion.views import terceros, views, inicio_sesion, empresas
from Administracion.views.seleccion_empresa import SeleccionEmpresaModalView

app_name = 'Administracion'

urlpatterns = [
    path('index/', terceros.PrincipalView.as_view(), name='index'),
    path('terceros/', terceros.TerceroView.as_view(), name='terceros'),
    path('terceros/add', terceros.TerceroCrearView.as_view(), name='terceros-crear'),
    path('terceros/<int:id>/', terceros.TerceroEditarView.as_view(), name='terceros-editar'),
    path('terceros/<int:id>/delete', terceros.TerceroEliminarView.as_view(), name='terceros-eliminar'),
    path('departamentos/<int:id>/municipios/json', views.CargarMunicipiosSelectJsonView.as_view(),
         name='municipios-json'),
    path('municipios/<int:id>/centros-poblados/json', views.CargarCentroPobladoSelectJsonView.as_view(),
         name='centros-poblados-json'),
    path('iniciar-sesion', inicio_sesion.IniciarSesionView.as_view(), name='iniciar-sesion'),
    path('cerrar-sesion', inicio_sesion.CerrarSesion.as_view(), name='cerrar-sesion'),
    path('olvido-contrasena', inicio_sesion.OlvidoContrasenaView.as_view(), name='olvido-contrasena'),
    path('empresas/', empresas.EmpresaView.as_view(), name='empresas'),
    path('empresas/add', empresas.EmpresaCrearView.as_view(), name='empresas-crear'),
    path('empresas/<int:id>/', empresas.EmpresaEditarView.as_view(), name='empresas-editar'),
    path('empresas/<int:id>/delete', empresas.EmpresaEliminarView.as_view(), name='empresas-eliminar'),
    path('empresas/modal-seleccion', SeleccionEmpresaModalView.as_view(), name='empresas-modal-seleccion'),
    path('sub-empresas/', empresas.SubempresaView.as_view(), name='sub-empresas'),
    path('sub-empresas/add', empresas.SubempresaCrearView.as_view(), name='sub-empresas-crear'),
    path('sub-empresas/<int:id>/', empresas.SubempresaEditarView.as_view(), name='sub-empresas-editar'),
    path('sub-empresas/<int:id>/delete', empresas.SubEmpresaEliminarView.as_view(), name='sub-empresas-eliminar'),
]
