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
from TalentoHumano.views import talento_humano, entidades_cafe, colaboradores

app_name = 'TalentoHumano'

urlpatterns = [
    path('index/', talento_humano.index, name='index'),
    path('entidades-index/<int:id_entidad>/', entidades_cafe.EntidadCAFEIndexView.as_view(), name='entidades-index'),
    path('entidades/add', entidades_cafe.EntidadCAFECrearView.as_view(), name='entidades-crear'),
    path('entidades/<int:id>/', entidades_cafe.EntidadCAFEEditarView.as_view(), name='entidades-editar'),
    path('entidades/<int:id>/delete', entidades_cafe.EntidadCAFEEliminarView.as_view(), name='entidades-eliminar'),
    path('colaboradores-index/', colaboradores.ColaboradoresIndexView.as_view(), name='colaboradores-index'),
    path('colaboradores/add', colaboradores.ColaboradoresCrearView.as_view(), name='colaboradores-crear'),
    path('colaboradores/<int:id>/', colaboradores.ColaboradorEditarView.as_view(), name='colaboradores-editar')
]
