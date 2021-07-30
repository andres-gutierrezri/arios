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
from GestionActividades.views import views, grupos_actividades, actividades

app_name = 'GestionActividades'

urlpatterns = [
    path('index/', views.PrincipalView.as_view(), name='index'),
    path('grupos-actividades/index', grupos_actividades.GruposActividadesIndexView.as_view(),
         name='grupos-actividades-index'),
    path('grupos-actividades/add', grupos_actividades.GruposActividadesCrearView.as_view(),
         name='grupos-actividades-crear'),
    path('grupos-actividades/<int:id_grupo>/editar', grupos_actividades.GruposActividadesEditarView.as_view(),
         name='grupos-actividades-editar'),
    path('grupos-actividades/<int:id_grupo>/delete', grupos_actividades.GruposActividadesEliminarView.as_view(),
         name='grupos-actividades-eliminar'),
    path('actividades/index', actividades.ActividadesIndexView.as_view(),
         name='actividades-index'),
    path('actividades/index/<int:id>', actividades.ActividadesIndexView.as_view(),
         name='actividades-index'),
    path('actividades/add', actividades.ActividadesCrearView.as_view(),
         name='actividades-crear'),
    path('actividades/<int:id_actividad>/editar', actividades.ActividadesEditarView.as_view(),
         name='actividades-editar'),
    path('actividades/<int:id_actividad>/actualizar', actividades.ActualizarActividadView.as_view(),
         name='actividades-actualizar'),
    path('actividades/<int:id_actividad>/delete', actividades.ActividadesEliminarView.as_view(),
         name='actividades-eliminar'),
    path('actividades/<int:id_actividad>/cargar', actividades.CargarSoporteView.as_view(),
         name='soportes-cargar'),
    path('actividades/<int:id_actividad>/soportes/<int:id_soporte>/ver-soporte',
         actividades.VerSoporteView.as_view(), name='soportes-ver'),
    path('actividades/<int:id_actividad>/cerrar-reabrir', actividades.CerrarReabrirActividadView.as_view(),
         name='actividades-cerrar-reabrir'),
    path('aprobacion-actividades/solicitudes_aprobacion/index',
         actividades.SolicitudesAprobacionActividadIndexView.as_view(), name='solicitudes-aprobacion-index'),
    path('aprobacion-actividades/<int:id_actividad>/accion', actividades.AccionModificacionesActividadView.as_view(),
         name='accion-modificaciones-actividad'),
    path('aprobacion-actividades/<int:id_actividad>/ver-modificaciones',
         actividades.VerModificacionesActividadView.as_view(), name='ver-modificaciones-actividad'),

]
