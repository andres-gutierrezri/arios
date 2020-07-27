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

from Financiero.views import PrincipalView, FacturaCrearView, FacturasView, FacturaEditarView, FacturaDetalleView, \
    FacturaImprimirView
from Financiero.views import subtipos_movimientos

app_name = 'Financiero'

urlpatterns = [
    path('index/', PrincipalView.as_view(), name='index'),
    path('facturas/', FacturasView.as_view(), name='factura-index'),
    path('facturas/add', FacturaCrearView.as_view(), name='factura-crear'),
    path('facturas/<int:id_factura>', FacturaEditarView.as_view(), name='factura-editar'),
    path('facturas/<int:id_factura>/json', FacturaDetalleView.as_view(), name='factura-detalle'),
    path('facturas/<int:id_factura>/imprimir', FacturaImprimirView.as_view(), name='factura-imprimir'),
    path('subtipos-movimientos/', subtipos_movimientos.SubtiposMovimientosView.as_view(), name='subtipo-movimiento-index'),
    path('subtipos-movimientos/add', subtipos_movimientos.SubtipoMovimientoCrearView.as_view(), name='subtipo-movimiento-crear'),
    path('subtipos-movimientos/<int:id>', subtipos_movimientos.SubtipoMovimientoEditarView.as_view(),
         name='subtipo-movimiento-editar'),
    path('subtipos-movimientos/<int:id>/delete', subtipos_movimientos.SubtipoMovimientoEliminarView.as_view(),
         name='subtipo-movimiento-eliminar'),
]
