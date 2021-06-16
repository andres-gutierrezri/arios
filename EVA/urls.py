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
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from EVA.views.index import IndexView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='eva-index'),
    path('administracion/', include('Administracion.urls', namespace='administracion')),
    path('proyectos/', include('Proyectos.urls', namespace='proyectos')),
    path('talento-humano/', include('TalentoHumano.urls', namespace='talento-humano')),
    path('sgi/', include('SGI.urls', namespace='sgi')),
    path('notificaciones/', include('Notificaciones.urls', namespace='notificaciones')),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='Administracion/Autenticacion/password_reset_complete.html')
         , name="password_reset_complete"),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='Administracion/Autenticacion/password_reset_confirm.html'),
         name="password_reset_confirm"),
    path('financiero/', include('Financiero.urls', namespace='financiero')),
    path('gestion-documental/', include('GestionDocumental.urls', namespace='gestion-documental')),
    path('gestion-actividades/', include('GestionActividades.urls', namespace='gestion-actividades')),
    path('password-assign-proveedor/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView
         .as_view(success_url=reverse_lazy('password_assign_complete_proveedor'),
                  template_name='Administracion/Tercero/Proveedor/Autenticacion/password_assign.html'),
         name="password_assign_proveedor",),
    path('password-assign-complete-proveedor/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='Administracion/Tercero/Proveedor/Autenticacion/password_assign_complete.html'),
         name="password_assign_complete_proveedor",),
    path('password-reset-confirm-proveedor/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView
         .as_view(success_url=reverse_lazy('password_reset_complete_proveedor'),
                  template_name='Administracion/Tercero/Proveedor/Autenticacion/password_reset_confirm.html'),
         name="password_reset_confirm_proveedor"),
    path('password-reset-complete-proveedor/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='Administracion/Tercero/Proveedor/Autenticacion/password_reset_complete.html'),
         name="password_reset_complete_proveedor",),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
