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
from TalentoHumano.views import talento_humano, entidades_cafe, colaboradores, gestion_permisos

app_name = 'TalentoHumano'

urlpatterns = [
    path('index/', talento_humano.Index.as_view(), name='index'),
    path('entidades-cafe/<int:id_entidad>/index', entidades_cafe.EntidadCAFEIndexView.as_view(),
         name='entidades-cafe-index'),
    path('entidades-cafe/add', entidades_cafe.EntidadCAFECrearView.as_view(), name='entidades-cafe-crear'),
    path('entidades-cafe/<int:id>/', entidades_cafe.EntidadCAFEEditarView.as_view(), name='entidades-cafe-editar'),
    path('entidades-cafe/<int:id>/delete', entidades_cafe.EntidadCAFEEliminarView.as_view(),
         name='entidades-cafe-eliminar'),
    path('colaboradores/contratos/<int:id_contrato>/', colaboradores.ColaboradoresIndexView.as_view(),
         name='colaboradores-index'),
    path('colaboradores/add', colaboradores.ColaboradoresCrearView.as_view(), name='colaboradores-crear'),
    path('colaboradores/<int:id>/', colaboradores.ColaboradorEditarView.as_view(), name='colaboradores-editar'),
    path('colaboradores/<int:id>/delete', colaboradores.ColaboradorEliminarView.as_view(),
         name='colaboradores-eliminar'),
    path('colaboradores/<int:id>/perfil', colaboradores.ColaboradoresPerfilView.as_view(),
         name='colaboradores-perfil'),
    path('colaboradores/<int:id>/foto-perfil', colaboradores.ColaboradorCambiarFotoPerfilView.as_view(),
         name='colaboradores-foto-perfil'),
    path('colaboradores/<int:id>/permisos/<int:id_filtro>', gestion_permisos.AsignacionPermisosView.as_view(),
         name='colaboradores-permisos'),
    path('colaboradores/novedad/add/<int:id_usuario>', colaboradores.AgregarNovedadView.as_view(),
         name='colaboradores-novedad-agregar'),
]
