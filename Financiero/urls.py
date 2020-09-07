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
from Financiero.views import subtipos_movimientos, flujo_caja, categorias_movimientos

app_name = 'Financiero'

urlpatterns = [
    path('index/', PrincipalView.as_view(), name='index'),
    path('facturas/', FacturasView.as_view(), name='factura-index'),
    path('facturas/add', FacturaCrearView.as_view(), name='factura-crear'),
    path('facturas/<int:id_factura>', FacturaEditarView.as_view(), name='factura-editar'),
    path('facturas/<int:id_factura>/json', FacturaDetalleView.as_view(), name='factura-detalle'),
    path('facturas/<int:id_factura>/imprimir', FacturaImprimirView.as_view(), name='factura-imprimir'),
    path('subtipos-movimientos/', subtipos_movimientos.SubtiposMovimientosView.as_view(),
         name='subtipo-movimiento-index'),
    path('subtipos-movimientos/add', subtipos_movimientos.SubtipoMovimientoCrearView.as_view(),
         name='subtipo-movimiento-crear'),
    path('subtipos-movimientos/<int:id>', subtipos_movimientos.SubtipoMovimientoEditarView.as_view(),
         name='subtipo-movimiento-editar'),
    path('subtipos-movimientos/<int:id>/delete', subtipos_movimientos.SubtipoMovimientoEliminarView.as_view(),
         name='subtipo-movimiento-eliminar'),
    path('flujo-caja/contratos', flujo_caja.FlujoCajaContratosView.as_view(), name='flujo-caja-contratos'),
    path('flujo-caja/contratos/<int:id>/detalle/<int:tipo>', flujo_caja.FlujoCajaContratosDetalleView.as_view(),
         name='flujo-caja-contratos-detalle'),
    path('flujo-caja/contratos/<int:id_contrato>/add/<int:tipo>', flujo_caja.FlujoCajaContratosCrearView.as_view(),
         name='flujo-caja-contratos-crear'),
    path('flujo-caja/contratos/<int:id_flujo_caja>', flujo_caja.FlujoCajaContratosEditarView.as_view(),
         name='flujo-caja-contratos-editar'),
    path('flujo-caja/contratos/<int:id>/delete', flujo_caja.FlujoCajaContratosEliminarView.as_view(),
         name='subtipo-movimiento-eliminar'),
    path('categorias-movimientos/', categorias_movimientos.CategoriasMovimientosView.as_view(),
         name='categoria-movimiento-index'),
    path('categorias-movimientos/add', categorias_movimientos.CategoriaMovimientoCrearView.as_view(),
         name='categoria-movimiento-crear'),
    path('categorias-movimientos/<int:id>', categorias_movimientos.CategoriaMovimientoEditarView.as_view(),
         name='categoria-movimiento-editar'),
    path('categorias-movimientos/<int:id>/delete', categorias_movimientos.CategoriaMovimientoEliminarView.as_view(),
         name='categoria-movimiento-eliminar'),
    path('flujo-caja/contratos/detalle/<int:id>/historial', flujo_caja.FlujoCajaContratosHistorialView.as_view(),
         name='flujo-caja-detalle-historial'),
]

