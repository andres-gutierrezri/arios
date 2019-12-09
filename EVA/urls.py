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
from django.urls import path, include
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

    path('correo/', include('django.contrib.auth.urls')),
    path('password-reset', auth_views.PasswordResetView.as_view(
            template_name='TalentoHumano/correo/password_reset.html',
            html_email_template_name="accounts/password_reset_complete.html",
            email_template_name='accounts/password_reset_email.html',
            subject_template_name="accounts/password_reset_subject.txt",
            ), name="password_reset"),
    path('password-reset/done',
         auth_views.PasswordResetDoneView.as_view(template_name='TalentoHumano/correo/password_reset_done.html'),
         name="password_reset_done"),

    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='TalentoHumano/correo/password_reset_complete.html')
         , name="password_reset_complete"),

    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='TalentoHumano/correo/password_reset_confirm.html'),
         name="password_reset_confirm"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
