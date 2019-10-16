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
from Administracion.views import tercero, views

app_name = 'Administracion'

urlpatterns = [
    path('principal/', tercero.principal_view, name='principal'),
    path('terceros/', tercero.tercero_view, name='terceros'),
    path('terceros/add', tercero.TerceroCrearView.as_view(), name='terceros-crear'),
    path('terceros/<int:id>/', tercero.TerceroEditarView.as_view(), name='terceros-editar'),
    path('terceros/<int:id>/delete', tercero.TerceroEliminarView.as_view(), name='terceros-eliminar'),
    path('departamentos/<int:id>/municipios/json', views.CargarMunicipiosSelectJsonView.as_view(),
        name='municipios-json'),
    path('municipios/<int:id>/centro-poblado/json', views.CargarCentroPobladoSelectJsonView.as_view(),
        name='centro-poblado-json'),

]
