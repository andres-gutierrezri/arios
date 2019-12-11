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
from Administracion.views import terceros, views, inicio_sesion

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
    path('terminar-sesion', inicio_sesion.TerminarSesion.as_view(), name='terminar-sesion'),
    path('olvido-contrasena', inicio_sesion.OlvidoContrasenaView.as_view(), name='olvido-contrasena'),
]
