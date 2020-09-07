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
    FacturaImprimirView, flujo_caja_general
from Financiero.views import subtipos_movimientos, flujo_caja_contratos, categorias_movimientos, flujo_caja_procesos

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
    path('flujo-caja/contratos', flujo_caja_contratos.FlujoCajaContratosView.as_view(), name='flujo-caja-contratos'),
    path('flujo-caja/contratos/<int:id>/detalle/<int:tipo>', flujo_caja_contratos.FlujoCajaContratosDetalleView.as_view(),
         name='flujo-caja-contratos-detalle'),
    path('flujo-caja/contratos/<int:id_contrato>/add/<int:tipo>', flujo_caja_contratos.FlujoCajaContratosCrearView.as_view(),
         name='flujo-caja-contratos-crear'),
    path('categorias-movimientos/', categorias_movimientos.CategoriasMovimientosView.as_view(),
         name='categoria-movimiento-index'),
    path('categorias-movimientos/add', categorias_movimientos.CategoriaMovimientoCrearView.as_view(),
         name='categoria-movimiento-crear'),
    path('categorias-movimientos/<int:id>', categorias_movimientos.CategoriaMovimientoEditarView.as_view(),
         name='categoria-movimiento-editar'),
    path('categorias-movimientos/<int:id>/delete', categorias_movimientos.CategoriaMovimientoEliminarView.as_view(),
         name='categoria-movimiento-eliminar'),
    path('flujo-caja/procesos', flujo_caja_procesos.FlujoCajaProcesosView.as_view(), name='flujo-caja-procesos'),
    path('flujo-caja/procesos/<int:id>/detalle/<int:tipo>', flujo_caja_procesos.FlujoCajaProcesosDetalleView.as_view(),
         name='flujo-caja-procesos-detalle'),
    path('flujo-caja/procesos/<int:id_proceso>/add/<int:tipo>', flujo_caja_procesos.FlujoCajaProcesosCrearView.as_view(),
         name='flujo-caja-procesos-crear'),
    path('flujo-caja/<int:id_movimiento>', flujo_caja_general.FlujoCajaMovimientoEditarView.as_view(),
         name='flujo-caja-movimiento-editar'),
    path('flujo-caja/movimiento/<int:id_movimiento>/delete', flujo_caja_general.FlujoCajaMovimientoEliminarView.as_view(),
         name='flujo-caja-movimiento-eliminar'),
    path('flujo-caja/movimiento/detalle/<int:id_movimiento>/historial',
         flujo_caja_general.FlujoCajaMovimientoHistorialView.as_view(), name='flujo-caja-movimiento-historial'),
]

