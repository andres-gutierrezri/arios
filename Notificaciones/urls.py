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
from Notificaciones.views import views, correo_electronico, asignacion, selecion_notificaciones_email

app_name = 'Notificaciones'

urlpatterns = [
    path('ver', views.NotificacionesView.as_view(), name='notificaciones-ver'),
    path('ver-todas', views.NotificacionesVerTodasView.as_view(), name='notificaciones-ver-todas'),
    path('<int:id>/actualizar', views.NotificacionesActualizarView.as_view(),
         name='notificaciones-actualizar'),
    path('enviar-email', correo_electronico.enviar_notificacion_por_email, name='envio-email'),
    path('token/<str:datos>', correo_electronico.TokenCorreoView.as_view(), name='token-correo'),
    path('asignacion/<int:id>', asignacion.AsignacionView.as_view(), name='notificaciones-asignacion'),
    path('seleccion-email/<int:id>', selecion_notificaciones_email.SeleccionNotificacionEmailView.as_view(),
         name='notificaciones-seleccion-email'),
]
