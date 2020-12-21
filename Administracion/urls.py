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
from Administracion.views import terceros, administracion, inicio_sesion, empresas, grupos_permisos, procesos
from Administracion.views.Terceros import proveedores, gestion_proveedores
from Administracion.views.seleccion_empresa import SeleccionEmpresaModalView

app_name = 'Administracion'

urlpatterns = [
    path('index/', administracion.PrincipalView.as_view(), name='index'),
    path('terceros/', terceros.TerceroView.as_view(), name='terceros'),
    path('terceros/add', terceros.TerceroCrearView.as_view(), name='terceros-crear'),
    path('terceros/<int:id>/', terceros.TerceroEditarView.as_view(), name='terceros-editar'),
    path('terceros/<int:id>/json', terceros.TerceroDetalleView.as_view(), name='terceros-detalle'),
    path('terceros/<int:id>/delete', terceros.TerceroEliminarView.as_view(), name='terceros-eliminar'),
    path('paises/<int:id>/departamentos/json', administracion.CargarDepartamentosSelectJsonView.as_view(),
         name='departamentos-json'),
    path('departamentos/<int:id>/municipios/json', administracion.CargarMunicipiosSelectJsonView.as_view(),
         name='municipios-json'),
    path('municipios/<int:id>/centros-poblados/json', administracion.CargarCentroPobladoSelectJsonView.as_view(),
         name='centros-poblados-json'),
    path('iniciar-sesion', inicio_sesion.IniciarSesionView.as_view(), name='iniciar-sesion'),
    path('cerrar-sesion', inicio_sesion.CerrarSesion.as_view(), name='cerrar-sesion'),
    path('olvido-contrasena', inicio_sesion.OlvidoContrasenaView.as_view(), name='olvido-contrasena'),
    path('empresas/', empresas.EmpresaView.as_view(), name='empresas'),
    path('empresas/add', empresas.EmpresaCrearView.as_view(), name='empresas-crear'),
    path('empresas/<int:id>/', empresas.EmpresaEditarView.as_view(), name='empresas-editar'),
    path('empresas/<int:id>/delete', empresas.EmpresaEliminarView.as_view(), name='empresas-eliminar'),
    path('empresas/modal-seleccion', SeleccionEmpresaModalView.as_view(), name='empresas-modal-seleccion'),
    path('sub-empresas/', empresas.SubempresaView.as_view(), name='sub-empresas'),
    path('sub-empresas/add', empresas.SubempresaCrearView.as_view(), name='sub-empresas-crear'),
    path('sub-empresas/<int:id>/', empresas.SubempresaEditarView.as_view(), name='sub-empresas-editar'),
    path('sub-empresas/<int:id>/delete', empresas.SubEmpresaEliminarView.as_view(), name='sub-empresas-eliminar'),
    path('grupos-permisos/', grupos_permisos.GruposPermisosView.as_view(), name='grupos-permisos'),
    path('grupos-permisos/add', grupos_permisos.GruposPermisosCrearView.as_view(), name='grupos-permisos-crear'),
    path('grupos-permisos/<int:id>/', grupos_permisos.GruposPermisosEditarView.as_view(), name='grupos-permisos-editar'),
    path('grupos-permisos/<int:id>/delete', grupos_permisos.GruposPermisosEliminarView.as_view(),
         name='grupos-permisos-eliminar'),
    path('procesos', procesos.ProcesosView.as_view(), name='procesos'),
    path('proveedor/index', terceros.IndexProveedorView.as_view(), name='proveedor-index'),
    path('proveedor/iniciar-sesion', terceros.InicioSesionProveedorView.as_view(), name='proveedor-iniciar-sesion'),
    path('proveedor/registro', terceros.RegistroProveedorView.as_view(), name='proveedor-registro'),
    path('proveedor/politica-confidencialidad', terceros.PoliticaDeCofidencialidadView.as_view(),
         name='proveedor-politica-cofidencialidad'),
    path('proveedor/perfil', proveedores.PerfilProveedorView.as_view(), name='proveedor-perfil'),
    path('proveedor/perfil/informacion-basica', proveedores.PerfilInformacionBasicaView.as_view(),
         name='proveedor-perfil-informacion-basica'),
    path('proveedor/perfil/actividades-economicas', proveedores.PerfilActividadesEconomicasView.as_view(),
         name='proveedor-perfil-actividades-economicas'),
    path('proveedor/perfil/entidades-bancarias', proveedores.EntidadesBancariasPerfilView.as_view(),
         name='proveedor-perfil-entidades-bancarias'),
    path('proveedor/perfil/entidad-bancaria/add', proveedores.EntidadBancariaCrearView.as_view(),
         name='proveedor-perfil-entidad-bancaria-crear'),
    path('proveedor/perfil/entidad-bancaria/<int:id>/', proveedores.EntidadBancariaEditarView.as_view(),
         name='proveedor-perfil-entidad-bancaria-editar'),
    path('proveedor/perfil/entidad-bancaria/<int:id>/delete', proveedores.EntidadBancariaEliminarView.as_view(),
         name='proveedor-perfil-entidad-bancaria-eliminar'),
    path('proveedor/perfil/ver-certificacion/<int:id>/', proveedores.VerCertificacionView.as_view(),
         name='proveedor-perfil-ver-certificacion'),
    path('proveedor/perfil/productos-servicios', proveedores.PerfilProductosServiciosView.as_view(),
         name='proveedor-perfil-productos-servicios'),
    path('producto-servicio/<int:id>/subtipos/json', administracion.CargarSubtiposProductoServicio.as_view(),
         name='subtipos-producto-servicio-json'),
    path('subtipo-producto-servicio/<int:id>/producto-servicio/json', administracion.CargarProductosServicios.as_view(),
         name='productos-servicios-json'),
    path('proveedor/perfil/documentos', proveedores.PerfilDocumentosView.as_view(), name='proveedor-perfil-documentos'),
    path('proveedor/perfil/documentos/add', proveedores.DocumentoCrearView.as_view(),
         name='proveedor-perfil-documento-crear'),
    path('proveedor/perfil/documentos/<int:id>/', proveedores.DocumentoEditarView.as_view(),
         name='proveedor-perfil-documento-editar'),
    path('proveedor/perfil/ver-documento/<int:id>/', proveedores.VerDocumentoView.as_view(),
         name='proveedor-perfil-ver-documento'),
    path('proveedor/solicitudes/', proveedores.SolicitudesProveedorView.as_view(),
         name='proveedor-solicitudes'),
    path('proveedor/solicitudes/<int:id>/enviar', proveedores.EnviarSolicitudProveedorView.as_view(),
         name='proveedor-solicitudes-enviar'),
    path('proveedor/solicitudes/<int:id>/pefil', proveedores.PerfilProveedorSolicitud.as_view(),
         name='proveedor-solicitudes-perfil'),
    path('proveedor/solicitudes/<int:id>/aprobar-rechazar', proveedores.ProveedorSolicitudAprobarRechazar.as_view(),
         name='proveedor-solicitudes-aprobar-rechazar'),
    path('proveedor/solicitudes/<int:id>/modificar', proveedores.ProveedorModificarSolicitudView.as_view(),
         name='proveedor-solicitudes-modificar'),
    path('proveedores/index', gestion_proveedores.ProveedorIndexView.as_view(),
         name='proveedor-administracion-index'),
    path('proveedores/<int:id>/cambiar-estado', gestion_proveedores.ActivarDesactivarProveedorView.as_view(),
         name='proveedor-cambiar-estado'),
]
