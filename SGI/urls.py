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
from SGI.views import sgi, documentos

app_name = 'SGI'

urlpatterns = [
    path('index/', sgi.Index.as_view(), name='index'),
    path('procesos/<int:id>/grupos-documentos', documentos.IndexView.as_view(), name='documentos-index'),
    path('procesos/<int:id_proceso>/grupos-documentos/<int:id_grupo>/documentos/add',
         documentos.DocumentosCrearView.as_view(), name='documentos-crear'),
    path('procesos/<int:id_proceso>/grupos-documentos/<int:id_grupo>/documentos/<int:id_documento>/cargar',
         documentos.ArchivoCargarView.as_view(), name='documentos-cargar'),
    path('procesos/<int:id_proceso>/ver-documento/<int:id_documento>',
         documentos.VerDocumentoView.as_view(), name='documentos-ver'),
]
