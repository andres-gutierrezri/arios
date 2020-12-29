from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render

from Administracion.models import Tercero
from Administracion.models.models import ProductoServicio, SubproductoSubservicio
from Administracion.models.terceros import ProveedorProductoServicio
from EVA.views.index import AbstractEvaLoggedView


class ProveedorIndexView(AbstractEvaLoggedView):
    def get(self, request):
        proveedores = ProveedorProductoServicio.objects.distinct('proveedor').filter(proveedor__es_vigente=True)
        producto_servicio_filtro = request.GET.getlist('producto_servicio_', [])
        tipo_producto_servicio = request.GET.get('tipo_producto_servicio_', '')
        subtipo_producto_servicio = request.GET.get('subtipo_producto_servicio_', '')

        productos_servicios = ProveedorProductoServicio.objects.all()
        lista_proveedores = []
        subtipos = []
        pro_serv = []
        if producto_servicio_filtro:
            for sl in producto_servicio_filtro:
                for ps in productos_servicios:
                    if int(sl) == ps.producto_servicio_id:
                        existe = False
                        for ls in lista_proveedores:
                            if ls['id'] == ps.proveedor.id:
                                existe = True
                        if not existe:
                            lista_proveedores.append(construir_lista_proveedores(ps))

                proveedores.filter(producto_servicio_id=sl)

            messages.success(request, 'Se han encontrado {0} coincidencias'.format(len(lista_proveedores)))
            es_servicio = True if tipo_producto_servicio == 1 else False
            subtipos = ProductoServicio.objects.get_xa_select_activos().filter(es_servicio=es_servicio)
            pro_serv = SubproductoSubservicio.objects.get_xa_select_activos()\
                .filter(producto_servicio__es_servicio=es_servicio)

            tipo_producto_servicio = int(tipo_producto_servicio)
            subtipo_producto_servicio = int(subtipo_producto_servicio)
        else:
            for pr in proveedores:
                lista_proveedores.append(construir_lista_proveedores(pr))
        valor_producto_servicio = []
        for ps in producto_servicio_filtro:
            valor_producto_servicio.append(int(ps))
        tipos_productos_servicios = [{'campo_valor': 1, 'campo_texto': 'Producto'},
                                     {'campo_valor': 2, 'campo_texto': 'Servicio'}]
        return render(request, 'Administracion/Tercero/Proveedor/index.html',
                      {'proveedores': lista_proveedores,
                       'menu_actual': ['proveedores', 'proveedores'],
                       'tipos_productos_servicios': tipos_productos_servicios,
                       'valor_tipo_producto_servicio': tipo_producto_servicio,
                       'valor_subtipo_producto_servicio': subtipo_producto_servicio,
                       'valor_producto_servicio': valor_producto_servicio,
                       'subtipos': subtipos, 'pro_serv': pro_serv, 'productos_servicios': productos_servicios})


def construir_lista_proveedores(ps):
    return {'id': ps.proveedor.id, 'nombre': ps.proveedor.nombre,
            'identificacion': '{0} {1}'.format(ps.proveedor.tipo_identificacion,
                                               ps.proveedor.identificacion),
            'ubicacion': '{0}-{1}-{2}'.format(
                ps.proveedor.ciudad.departamento.pais,
                ps.proveedor.ciudad.departamento,
                ps.proveedor.ciudad),
            'telefono': ps.proveedor.telefono_movil_principal,
            'correo': ps.proveedor.correo_principal,
            'estado': ps.proveedor.estado,
            'fecha_creacion': ps.proveedor.fecha_creacion}


class ActivarDesactivarProveedorView(AbstractEvaLoggedView):
    def post(self, request, id):
        try:
            proveedor = Tercero.objects.get(id=id)
            proveedor.estado = False if proveedor.estado else True
            proveedor.save(update_fields=['estado'])
            texto = 'activado' if proveedor.estado else 'desactivado'
            messages.success(request, 'Se ha ' + texto + ' el proveedor correctamente')
            return JsonResponse({"estado": "OK"})

        except IntegrityError:
            return JsonResponse({"estado": "error",
                                 "mensaje": "Ha ocurrido un error al realizar la acción"})
