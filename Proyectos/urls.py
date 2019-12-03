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
from Proyectos.views import proyectos, contratos

app_name = 'Proyectos'

urlpatterns = [
    path('index/', proyectos.Index.as_view(), name='index'),
    path('contratos/', contratos.ContratoView.as_view(), name='contratos'),
    path('contratos/add', contratos.ContratoCrearView.as_view(), name='contratos-crear'),
    path('contratos/<int:id>/', contratos.ContratoEditarView.as_view(), name='contratos-editar'),
    path('contratos/<int:id>/delete', contratos.ContratoEliminarView.as_view(), name='contratos-eliminar'),
]
