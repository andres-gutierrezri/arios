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
from GestionDocumental.views import views, consecutivo_documento, consecutivo_contrato

app_name = 'GestionDocumental'

urlpatterns = [
    path('index/', views.PrincipalView.as_view(), name='index'),
    path('consecutivo-oficios/<int:id>/index', consecutivo_documento.ConsecutivoOficiosView.as_view(),
         name='consecutivo-oficios-index'),
    path('consecutivo-oficios/add', consecutivo_documento.ConsecutivoOficiosCrearView.as_view(),
         name='consecutivo-oficios-crear'),
    path('consecutivo-contratos/<int:id>/index', consecutivo_contrato.ConsecutivoContratoView.as_view(),
         name='consecutivo-contratos-index'),
    path('consecutivo-contratos/add', consecutivo_contrato.ConsecutivoContratoCrearView.as_view(),
         name='consecutivo-contratos-crear'),
]