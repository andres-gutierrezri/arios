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
from GestionActividades.views import views, grupo_actividades, actividades

app_name = 'GestionActividades'

urlpatterns = [
    path('index/', views.PrincipalView.as_view(), name='index'),
    path('grupo-actividades/index', grupo_actividades.GruposActividadesIndexView.as_view(),
         name='grupo-actividades-index'),
    path('grupo-actividades/add', grupo_actividades.GruposActividadesCrearView.as_view(),
         name='grupo-actividades-crear'),
    path('grupo-actividades/<int:id_grupo>/editar', grupo_actividades.GruposActividadesEditarView.as_view(),
         name='grupo-actividades-editar'),
    path('actividades/index', actividades.ActividadesIndexView.as_view(),
         name='actividades-index'),
    path('actividades/index/<int:id>', actividades.ActividadesIndexView.as_view(),
         name='actividades-index'),
    path('actividades/add', actividades.ActividadesCrearView.as_view(),
         name='actividades-crear'),
    path('actividades/<int:id_actividad>/editar', actividades.ActividadesEditarView.as_view(),
         name='actividades-editar'),


]
