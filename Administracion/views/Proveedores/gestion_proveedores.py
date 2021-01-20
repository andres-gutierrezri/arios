import json

from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

from Administracion.enumeraciones import EstadosProveedor
from Administracion.models import Tercero
from Administracion.models.models import ProductoServicio, SubproductoSubservicio
from Administracion.models.terceros import ProveedorProductoServicio
from EVA.General.utilidades import paginar, app_datetime_now
from EVA.views.index import AbstractEvaLoggedView

SOLICITUD_ENVIADA = 5


class ProveedorIndexView(AbstractEvaLoggedView):
    def get(self, request):
        tipo_producto_servicio = request.GET.get('tipo_producto_servicio_', '')
        producto_servicio = request.GET.get('producto_servicio_', '')
        subproducto_subservicio = request.GET.getlist('subproducto_subservicio_', [])
        busqueda_avanzada = request.GET.get('busqueda_avanzada', [])
        search = request.GET.get('search', '')
        if busqueda_avanzada:
            subproducto_subservicio = json.loads(busqueda_avanzada)

        productos_servicios = []
        subproductos_subservicios = []
        all_productos_servicios = ProveedorProductoServicio.objects.all()
        proveedores_pro_serv = ProveedorProductoServicio.objects.distinct('proveedor')\
            .filter(proveedor__es_vigente=True)\
            .exclude(proveedor__estado_proveedor=EstadosProveedor.DILIGENCIAMIENTO_PERFIL)

        if search:
            proveedores_pro_serv = proveedores_pro_serv\
                .filter(Q(proveedor__nombre__icontains=search) |
                        Q(proveedor__identificacion__icontains=search) |
                        Q(proveedor__ciudad__nombre__icontains=search) |
                        Q(proveedor__ciudad__departamento__nombre__icontains=search) |
                        Q(proveedor__ciudad__departamento__pais__nombre__icontains=search) |
                        Q(proveedor__telefono_movil_principal__icontains=search) |
                        Q(proveedor__correo_principal__icontains=search))

        resutados_busqueda = ''
        if subproducto_subservicio:
            proveedores_pro_serv = proveedores_pro_serv.filter(subproducto_subservicio_id__in=subproducto_subservicio)
            if proveedores_pro_serv:
                tipo_producto_servicio = 2 if proveedores_pro_serv[0].subproducto_subservicio.producto_servicio\
                    .es_servicio else 1
                producto_servicio = proveedores_pro_serv[0].subproducto_subservicio.producto_servicio_id
                resutados_busqueda = 'Se han encontrado {0} coincidencias'.format(len(proveedores_pro_serv))
                messages.success(request, resutados_busqueda)
            else:
                tipo_producto_servicio = int(tipo_producto_servicio)
                producto_servicio = int(producto_servicio)
                resutados_busqueda = 'No se encontraron coincidencias'
                messages.warning(request, resutados_busqueda)

            es_servicio = tipo_producto_servicio == 2
            productos_servicios = ProductoServicio.objects.get_xa_select_activos().filter(es_servicio=es_servicio)
            subproductos_subservicios = SubproductoSubservicio.objects.get_xa_select_activos()\
                .filter(producto_servicio_id=producto_servicio)

        valor_subproducto_subservicio = []
        for ps in subproducto_subservicio:
            valor_subproducto_subservicio.append(int(ps))
        tipos_productos_servicios = [{'campo_valor': 1, 'campo_texto': 'Producto'},
                                     {'campo_valor': 2, 'campo_texto': 'Servicio'}]

        lista_proveedores_activos = []
        for pps in proveedores_pro_serv:
            coincidencia = False
            for pro in Tercero.objects.filter(es_vigente=False):
                if pps.proveedor.usuario == pro.usuario and pro.estado_proveedor == SOLICITUD_ENVIADA:
                    coincidencia = True
            if not coincidencia:
                lista_proveedores_activos.append(pps)

        label_producto_servicio, label_subproducto_subservicio = ['Servicio', 'Subservicio'] \
            if tipo_producto_servicio == 2 else ['Producto', 'Subproducto']

        page = request.GET.get('page', 1)
        lista_proveedores_activos = paginar(lista_proveedores_activos, page, 10)
        return render(request, 'Administracion/Tercero/Proveedor/index.html',
                      {'proveedores_pro_serv': lista_proveedores_activos,
                       'menu_actual': ['proveedores', 'proveedores'],
                       'tipos_productos_servicios': tipos_productos_servicios,
                       'productos_servicios': productos_servicios,
                       'subproductos_subservicios': subproductos_subservicios,
                       'valor_tipo_producto_servicio': tipo_producto_servicio,
                       'valor_producto_servicio': producto_servicio,
                       'valor_subproducto_subservicio': valor_subproducto_subservicio,
                       'all_productos_servicios': all_productos_servicios,
                       'label_producto_servicio': label_producto_servicio,
                       'label_subproducto_subservicio': label_subproducto_subservicio,
                       'resutados_busqueda': resutados_busqueda,
                       'buscar': search,
                       'fecha': app_datetime_now()})


class ActivarDesactivarProveedorView(AbstractEvaLoggedView):
    def post(self, request, id):
        try:
            proveedor = Tercero.objects.get(id=id)
            proveedor.estado_proveedor = EstadosProveedor.DESACTIVADO_X_ADMINISTRADOR\
                if proveedor.estado else EstadosProveedor.ACTIVO
            proveedor.estado = proveedor.estado is False
            proveedor.save(update_fields=['estado', 'estado_proveedor'])
            texto = 'activado' if proveedor.estado else 'desactivado'
            messages.success(request, 'Se ha ' + texto + ' el proveedor correctamente')
            return JsonResponse({"estado": "OK"})

        except IntegrityError:
            return JsonResponse({"estado": "error",
                                 "mensaje": "Ha ocurrido un error al realizar la acción"})
