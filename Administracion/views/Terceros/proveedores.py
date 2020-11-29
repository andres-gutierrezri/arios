import json
import os
from sqlite3 import IntegrityError

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from Administracion.models import TipoIdentificacion, Pais, Tercero, Departamento, Municipio
from Administracion.models.models import SubtipoProductoServicio, ProductoServicio
from Administracion.models.terceros import ProveedorProductoServicio, TipoDocumentoTercero, DocumentoTercero
from EVA.General import app_datetime_now
from EVA.General.conversiones import datetime_to_string
from EVA.views.index import AbstractEvaLoggedProveedorView
from Financiero.models.models import ActividadEconomica, TipoContribuyente, Regimen, ProveedorActividadEconomica, \
    EntidadBancariaTercero, EntidadBancaria, TipoCuentaBancaria


class PerfilProveedorView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        proveedor = Tercero.objects.get(usuario=request.user)
        informacion_basica = generar_datos_informacion_basica(proveedor)
        actividades_economicas = generar_datos_actividades_economicas(proveedor)
        entidades_bancarias = generar_datos_entidades_bancarias(proveedor)
        bienes_servicios = generar_datos_bienes_servicios(proveedor)
        documentos = generar_datos_documentos(proveedor)

        total = 0
        total = total + 20 if informacion_basica else total
        total = total + 20 if actividades_economicas else total
        total = total + 20 if entidades_bancarias else total
        total = total + 20 if bienes_servicios else total
        total = total + 20 if documentos else total

        opciones = [{'id': 1, 'nombre': 'Información Básica',
                     'url': '/administracion/proveedor/perfil/informacion-basica', 'datos': informacion_basica},
                    {'id': 2, 'nombre': 'Actividades Económicas',
                     'url': '/administracion/proveedor/perfil/actividades-economicas', 'datos': actividades_economicas},
                    {'id': 3, 'nombre': 'Entidades Bancarias',
                     'url': '/administracion/proveedor/perfil/entidades-bancarias', 'datos': entidades_bancarias},
                    {'id': 4, 'nombre': 'Bienes y Servicios',
                     'url': '/administracion/proveedor/perfil/productos-servicios', 'datos': bienes_servicios},
                    {'id': 5, 'nombre': 'Documentos',
                     'url': '/administracion/proveedor/perfil/documentos', 'datos': documentos},
                    ]
        return render(request, 'Administracion/Tercero/Proveedor/perfil.html',
                      {'opciones': opciones, 'total': total})


class PerfilInformacionBasicaView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        return render(request, 'Administracion/Tercero/Proveedor/informacion_basica.html',
                      datos_xa_render_informacion_basica(request))

    def post(self, request):
        update_fields = ('nombre', 'tipo_identificacion_id', 'identificacion', 'ciudad', 'nombre_rl',
                         'tipo_identificacion_rl', 'identificacion_rl', 'lugar_expedicion_rl', 'telefono_fijo_principal',
                         'telefono_movil_principal', 'telefono_fijo_auxiliar', 'telefono_movil_auxiliar',
                         'correo_principal', 'correo_auxiliar', 'fecha_inicio_actividad', 'fecha_constitucion')

        proveedor = Tercero.objects.get(usuario=request.user)

        proveedor.nombre = request.POST.get('nombre', '')
        proveedor.tipo_identificacion_id = request.POST.get('tipo_identificacion', '')
        proveedor.identificacion = request.POST.get('nit', '')
        proveedor.ciudad_id = request.POST.get('municipio', '')

        proveedor.nombre_rl = request.POST.get('nombre_rl', '')
        proveedor.tipo_identificacion_rl_id = request.POST.get('tipo_identificacion_rl', '')
        proveedor.identificacion_rl = request.POST.get('identificacion_rl', '')
        proveedor.lugar_expedicion_rl_id = request.POST.get('municipio_rl', '')

        proveedor.telefono_fijo_principal = request.POST.get('fijo_principal', '')
        proveedor.telefono_movil_principal = request.POST.get('movil_principal', '')
        proveedor.telefono_fijo_auxiliar = request.POST.get('fijo_auxiliar', '')
        proveedor.telefono_movil_auxiliar = request.POST.get('movil_auxiliar', '')
        proveedor.correo_principal = request.POST.get('correo_pincipal', '')
        proveedor.correo_auxiliar = request.POST.get('correo_auxiliar', '')

        proveedor.fecha_inicio_actividad = request.POST.get('fecha_inicio_actividad', '')
        proveedor.fecha_constitucion = request.POST.get('fecha_constitucion', '')

        if not proveedor.fecha_inicio_actividad:
            proveedor.fecha_inicio_actividad = None

        if not proveedor.fecha_constitucion:
            proveedor.fecha_constitucion = None

        try:
            proveedor.save(update_fields=update_fields)
            messages.success(self.request, 'Se ha guardado la información básica correctamente.')
            return redirect(reverse('Administracion:proveedor-perfil'))
        except:
            messages.error(self.request, 'Ha ocurrido un error al actualizar la información.')
            return redirect(reverse('Administracion:proveedor-perfil'))


class PerfilActividadesEconomicasView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        return render(request, 'Administracion/Tercero/Proveedor/actividades_economicas.html',
                      datos_xa_render_actividades_economicas(request))

    def post(self, request):
        update_fields = ('actividad_principal', 'actividad_secundaria', 'otra_actividad', 'regimen', 'contribuyente_iyc',
                         'tipo_contribuyente', 'numero_resolucion', 'contribuyente_iyc', 'entidad_publica', 'proveedor',
                         'bienes_servicios', 'proveedor')
        proveedor = Tercero.objects.get(usuario=request.user)
        proveedor_ae = ProveedorActividadEconomica.from_dictionary(request.POST)
        proveedor_ae.proveedor = proveedor

        try:
            registro = ProveedorActividadEconomica.objects.filter(proveedor=proveedor)
            if registro:
                proveedor_ae.id = registro.first().id
                proveedor_ae.save(update_fields=update_fields)
            else:
                proveedor_ae.save()
            messages.success(self.request, 'Se ha guardado la información básica correctamente.')
            return redirect(reverse('Administracion:proveedor-perfil'))
        except:
            messages.error(self.request, 'Ha ocurrido un error al actualizar la información.')
            return redirect(reverse('Administracion:proveedor-perfil'))


class EntidadesBancariasPerfilView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        entidades_bancarias = EntidadBancariaTercero.objects.filter(tercero__usuario=request.user)
        return render(request, 'Administracion/Tercero/Proveedor/entidades_bancarias.html',
                      {'entidades_bancarias': entidades_bancarias, 'fecha': app_datetime_now()})


class EntidadBancariaCrearView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        return render(request,
                      'Administracion/_common/_modal_gestionar_entidad_bancaria.html',
                      datos_xa_render_entidades_bancarias(request))

    def post(self, request):
        entidad_proveedor = EntidadBancariaTercero.from_dictionary(request.POST)
        entidad_proveedor.tercero = Tercero.objects.get(usuario=request.user)
        entidad_proveedor.certificacion = request.FILES.get('certificacion', '')
        try:
            entidad_proveedor.save()
        except:
            return JsonResponse({"estado": "error", "mensaje": "Ha ocurrido un error al guardar la información"})

        messages.success(self.request, 'Se ha creado la entidad correctamente.')
        return JsonResponse({"estado": "OK"})


class EntidadBancariaEditarView(AbstractEvaLoggedProveedorView):
    def get(self, request, id):
        entidad_bancaria = EntidadBancariaTercero.objects.get(id=id)
        return render(request,
                      'Administracion/_common/_modal_gestionar_entidad_bancaria.html',
                      datos_xa_render_entidades_bancarias(request, entidad_bancaria))

    def post(self, request, id):
        update_fields = ['tipo_cuenta', 'entidad_bancaria']
        entidad_proveedor = EntidadBancariaTercero.from_dictionary(request.POST)
        entidad_proveedor.id = id
        entidad_proveedor.certificacion = request.FILES.get('certificacion', '')
        entidad_proveedor.tercero = Tercero.objects.get(usuario=request.user)
        try:
            if entidad_proveedor.certificacion:
                update_fields.append('certificacion')
            entidad_proveedor.save(update_fields=update_fields)
        except:
            return JsonResponse({"estado": "error", "mensaje": "Ha ocurrido un error al guardar la información"})

        messages.success(self.request, 'Se ha actualizado la entidad correctamente.')
        return JsonResponse({"estado": "OK"})


class EntidadBancariaEliminarView(AbstractEvaLoggedProveedorView):
    def post(self, request, id):
        entidad_proveedor = EntidadBancariaTercero.objects.get(id=id)
        try:
            entidad_proveedor.delete()
            messages.success(request, 'Se ha eliminado la entidad correctamente')
            return JsonResponse({"estado": "OK"})

        except IntegrityError:
            return JsonResponse({"estado": "error",
                                 "mensaje": "Ha ocurrido un error al realizar la acción Vista"})


class VerCertificacionView(AbstractEvaLoggedProveedorView):
    def get(self, request, id):
        entidad_bancaria = EntidadBancariaTercero.objects.get(id=id)
        if entidad_bancaria.certificacion:
            extension = os.path.splitext(entidad_bancaria.certificacion.url)[1]
            mime_types = {'.docx': 'application/msword', '.xlsx': 'application/vnd.ms-excel',
                          '.pptx': 'application/vnd.ms-powerpoint',
                          '.xlsm': 'application/vnd.ms-excel.sheet.macroenabled.12',
                          '.dwg': 'application/octet-stream'
                          }

            mime_type = mime_types.get(extension, 'application/pdf')

            response = HttpResponse(entidad_bancaria.certificacion, content_type=mime_type)
            response['Content-Disposition'] = 'inline; filename="{0} - {1}{2}"'\
                .format(entidad_bancaria.entidad_bancaria.nombre, entidad_bancaria.tipo_cuenta.nombre, extension)
        else:
            messages.error(self.request, 'Ha ocurrido un error al realizar esta acción.')
            response = redirect(reverse('Administracion:proveedor-perfil-entidades-bancarias'))

        return response


class PerfilProductosServiciosView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        return render(request, 'Administracion/Tercero/Proveedor/productos_servicios.html',
                      datos_xa_render_productos_servicios(request))

    def post(self, request):
        contador = request.POST.get('contador')
        proveedor = Tercero.objects.get(usuario=request.user)
        try:
            ProveedorProductoServicio.objects.filter(proveedor=proveedor).delete()
            if contador:
                cn = 0
                while cn < int(contador):
                    datos = request.POST.getlist('producto_servicio_{0}'.format(cn), '')
                    if datos != '':
                        for dt in datos:
                            ProveedorProductoServicio.objects.create(proveedor=proveedor, producto_servicio_id=dt)
                    cn += 1
            else:
                datos = request.POST.getlist('producto_servicio_0', '')
                if datos != '':
                    for dt in datos:
                        ProveedorProductoServicio.objects.create(proveedor=proveedor, producto_servicio_id=dt)
        except:
            messages.success(self.request, 'Ha ocurrido un error al guardar los datos')

        return redirect(reverse('Administracion:proveedor-perfil'))


class PerfilDocumentosView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        proveedor = Tercero.objects.get(usuario=request.user)

        if proveedor.tipo_identificacion.tipo_nit:
            documentos = DocumentoTercero.objects.filter(tercero=proveedor, tipo_documento__aplica_juridica=True)
        else:
            documentos = DocumentoTercero.objects.filter(tercero=proveedor, tipo_documento__aplica_natural=True)
        agregar = verificar_documentos_proveedor(proveedor, documentos)
        return render(request, 'Administracion/Tercero/Proveedor/documentos.html', {'documentos': documentos,
                                                                                    'agregar': agregar})


class DocumentoCrearView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        return render(request, 'Administracion/_common/_modal_gestionar_documento.html',
                      datos_xa_render_documentos(request))

    def post(self, request):
        proveedor = Tercero.objects.get(usuario=request.user)
        documento = DocumentoTercero()
        documento.tipo_documento_id = request.POST.get('tipo_documento', '')
        documento.tercero = proveedor
        documento.documento = request.FILES.get('documento', '')
        documento.Estado = True
        try:
            documento.save()
        except:
            return JsonResponse({"estado": "error", "mensaje": "Ha ocurrido un error al guardar la información"})

        messages.success(self.request, 'Se ha cargado el documento {0} correctamente.'
                         .format(documento.tipo_documento.nombre))
        return JsonResponse({"estado": "OK"})


class DocumentoEditarView(AbstractEvaLoggedProveedorView):
    def get(self, request, id):
        documento = DocumentoTercero.objects.get(id=id)
        return render(request, 'Administracion/_common/_modal_gestionar_documento.html',
                      datos_xa_render_documentos(request, documento))

    def post(self, request, id):
        update_fields = ['documento']
        documento = DocumentoTercero.objects.get(id=id)
        documento.documento = request.FILES.get('documento', '')
        try:
            documento.save(update_fields=update_fields)
        except:
            return JsonResponse({"estado": "error", "mensaje": "Ha ocurrido un error al guardar la información"})

        messages.success(self.request, 'Se ha cargado el documento {0} correctamente.'
                         .format(documento.tipo_documento.nombre))
        return JsonResponse({"estado": "OK"})


class VerDocumentoView(AbstractEvaLoggedProveedorView):
    def get(self, request, id):
        documento = DocumentoTercero.objects.get(id=id)
        if documento.documento:
            extension = os.path.splitext(documento.documento.url)[1]
            mime_types = {'.docx': 'application/msword', '.xlsx': 'application/vnd.ms-excel',
                          '.pptx': 'application/vnd.ms-powerpoint',
                          '.xlsm': 'application/vnd.ms-excel.sheet.macroenabled.12',
                          '.dwg': 'application/octet-stream'
                          }

            mime_type = mime_types.get(extension, 'application/pdf')

            response = HttpResponse(documento.documento, content_type=mime_type)
            response['Content-Disposition'] = 'inline; filename="{0} - {1}{2}"'\
                .format(documento.tercero.nombre, documento.tipo_documento.nombre, extension)
        else:
            messages.error(self.request, 'Ha ocurrido un error al realizar esta acción.')
            response = redirect(reverse('Administracion:proveedor-perfil-documentos'))

        return response


def datos_xa_render_informacion_basica(request):
    tipo_identificacion = TipoIdentificacion.objects.get_xa_select_activos()
    tipo_identificacion_personas = TipoIdentificacion.objects.get_xa_select_personas_activos()
    json_tipo_identificacion = TipoIdentificacion.objects.get_activos_like_json()
    paises = Pais.objects.get_xa_select_activos()
    proveedor = Tercero.objects.get(usuario=request.user)

    departamentos = ''
    municipios = ''
    departamentos_rl = ''
    municipios_rl = ''

    if proveedor.ciudad:
        departamentos = Departamento.objects.get_xa_select_activos().filter(pais=proveedor.ciudad.departamento.pais)
        municipios = Municipio.objects.get_xa_select_activos().filter(departamento=proveedor.ciudad.departamento)
    if proveedor.lugar_expedicion_rl:
        departamentos_rl = Departamento.objects.get_xa_select_activos() \
            .filter(pais=proveedor.lugar_expedicion_rl.departamento.pais)
        municipios_rl = Municipio.objects.get_xa_select_activos() \
            .filter(departamento=proveedor.lugar_expedicion_rl.departamento)

    datos = {'tipo_identificacion': tipo_identificacion, 'tipo_identificacion_personas': tipo_identificacion_personas,
             'json_tipo_identificacion': json_tipo_identificacion, 'paises': paises, 'proveedor': proveedor,
             'departamentos': departamentos, 'municipios': municipios, 'departamentos_rl': departamentos_rl,
             'municipios_rl': municipios_rl}
    return datos


def datos_xa_render_actividades_economicas(request):
    proveedor = ProveedorActividadEconomica.objects.filter(proveedor__usuario=request.user)
    if proveedor:
        proveedor = proveedor.first()
    actividades_economicas = ActividadEconomica.objects.get_xa_select_actividades_con_codigo()
    regimenes = Regimen.objects.get_xa_select_activos()
    tipos_contribuyente = TipoContribuyente.objects.get_xa_select_activos()
    datos_regimenes = Regimen.objects.get_activos_like_json()
    entidades_publicas = [{'campo_valor': '1', 'campo_texto': 'Nacional'},
                          {'campo_valor': '2', 'campo_texto': 'Departamental'},
                          {'campo_valor': '3', 'campo_texto': 'Municipal'}]

    datos = {'actividades_economicas': actividades_economicas, 'regimenes': regimenes,
             'tipos_contribuyente': tipos_contribuyente, 'datos_regimenes': datos_regimenes,
             'entidades_publicas': entidades_publicas, 'proveedor': proveedor}
    return datos


def datos_xa_render_entidades_bancarias(request, objeto=None):
    datos = EntidadBancariaTercero.objects.filter(tercero__usuario=request.user)
    datos_proveedor = []
    if datos:
        for d in datos:
            datos_proveedor.append({'tipo_cuenta_id': d.tipo_cuenta_id,
                                    'tipo_cuenta_nombre': d.tipo_cuenta.nombre,
                                    'entidad_bancaria_id': d.entidad_bancaria_id,
                                    'entidad_bancaria_nombre': d.entidad_bancaria.nombre,
                                    'id': d.id})
        datos_proveedor = json.dumps(datos_proveedor)

    tipos_cuentas = TipoCuentaBancaria.objects.get_xa_select_activos()
    entidades_bancarias = EntidadBancaria.objects.get_xa_select_activos()
    datos = {'entidades_bancarias': entidades_bancarias, 'tipos_cuentas': tipos_cuentas,
             'datos_proveedor': datos_proveedor, 'objeto': objeto}
    return datos


def datos_xa_render_productos_servicios(request):
    tipos_productos_servicios = [{'campo_valor': 1, 'campo_texto': 'Producto'},
                                 {'campo_valor': 2, 'campo_texto': 'Servicio'}]
    subtipos_productos_servicios = SubtipoProductoServicio.objects.get_xa_select_activos()
    productos_servicios = ProductoServicio.objects.get_xa_select_activos()
    proveedor = Tercero.objects.get(usuario=request.user)
    selecciones = ProveedorProductoServicio.objects.filter(proveedor=proveedor)
    lista_selecciones = []
    contador = 0
    for dt in selecciones:
        coincidencia = False
        for ls in lista_selecciones:
            if dt.producto_servicio.subtipo_producto_servicio_id == ls['subtipo_producto_servicio']:
                coincidencia = True
        if not coincidencia:
            subtipos = ProveedorProductoServicio\
                .objects.filter(proveedor=proveedor, producto_servicio__subtipo_producto_servicio=dt.
                                producto_servicio.subtipo_producto_servicio)
            lista_pro_ser = []
            for st in subtipos:
                lista_pro_ser.append(st.producto_servicio_id)
            lista_selecciones\
                .append({'tipo_producto_servicio': 2 if dt.producto_servicio.subtipo_producto_servicio.es_servicio else 1,
                         'nombre_tipos': 'tipo_producto_servicio_{0}'.format(contador),
                         'onchange_tipos': 'cambioTipoProductoServicio({0})'.format(contador),
                         'subtipo_producto_servicio': dt.producto_servicio.subtipo_producto_servicio_id,
                         'nombre_subtipos': 'subtipo_producto_servicio_{0}'.format(contador),
                         'onchange_subtipos': 'cambioSubtipoProductoServicio({0})'.format(contador),
                         'datos_subtipos': SubtipoProductoServicio.objects.get_xa_select_activos()
                        .filter(es_servicio=dt.producto_servicio.subtipo_producto_servicio.es_servicio),
                         'productos_servicios': lista_pro_ser,
                         'nombre_producto_servicio': 'producto_servicio_{0}'.format(contador),
                         'datos_productos_servicios': ProductoServicio.objects.get_xa_select_activos()
                        .filter(subtipo_producto_servicio=dt.producto_servicio.subtipo_producto_servicio),
                         'contador': contador})
            contador += 1

    datos = {'tipos_productos_servicios': tipos_productos_servicios,
             'subtipos_productos_servicios': subtipos_productos_servicios,
             'productos_servicios': productos_servicios,
             'selecciones': lista_selecciones,
             'contador': contador}
    return datos


def datos_xa_render_documentos(request, documento: DocumentoTercero = None):
    proveedor = Tercero.objects.get(usuario=request.user)
    if proveedor.tipo_identificacion.tipo_nit:
        tipos_documentos = TipoDocumentoTercero.objects.get_xa_select_activos_aplica_juridica()
    else:
        tipos_documentos = TipoDocumentoTercero.objects.get_xa_select_activos_aplica_natural()

    documentos_actuales = DocumentoTercero.objects.filter(tercero__usuario=request.user)
    lista_tipos_documentos = []
    for td in tipos_documentos:
        coincidencia = False
        for da in documentos_actuales:
            if da.tipo_documento_id == td['campo_valor']:
                coincidencia = True
        if not coincidencia:
            lista_tipos_documentos.append(td)

    return {'tipos_documentos': lista_tipos_documentos, 'documento': documento}


def verificar_documentos_proveedor(proveedor, documentos):
    if proveedor.tipo_identificacion.tipo_nit:
        tipos_documentos = TipoDocumentoTercero.objects.filter(aplica_juridica=True)
    else:
        tipos_documentos = TipoDocumentoTercero.objects.filter(aplica_natural=True)
    respuesta = True
    contador = 0
    for td in tipos_documentos:
        for dc in documentos:
            if td == dc.tipo_documento:
                contador += 1
    if contador == len(tipos_documentos):
        respuesta = False
    return respuesta


def generar_datos_informacion_basica(proveedor):
    return [{'nombre_campo': 'Nombre', 'valor_campo': proveedor.nombre},
            {'nombre_campo': 'Tipo de Identificación', 'valor_campo': proveedor.tipo_identificacion.nombre},
            {'nombre_campo': 'Identificación', 'valor_campo': proveedor.identificacion},
            {'nombre_campo': 'Ubicación', 'valor_campo':
                '{1} - {2} - {0}'.format(proveedor.ciudad.departamento.pais.nombre.capitalize(),
                                         proveedor.ciudad.departamento.nombre.capitalize(),
                                         proveedor.ciudad.nombre.capitalize())},
            {'nombre_campo': 'Teléfono Fijo Principal', 'valor_campo': proveedor.telefono_fijo_principal},
            {'nombre_campo': 'Teléfono Movil Principal', 'valor_campo': proveedor.telefono_movil_principal},
            {'nombre_campo': 'Teléfono Fijo Auxiliar', 'valor_campo': proveedor.telefono_fijo_auxiliar},
            {'nombre_campo': 'Teléfono Movil Auxiliar', 'valor_campo': proveedor.telefono_movil_auxiliar},
            {'nombre_campo': 'Correo Electrónico Principal', 'valor_campo': proveedor.correo_principal},
            {'nombre_campo': 'Correo Electrónico Auxiliar', 'valor_campo': proveedor.correo_auxiliar},
            {'nombre_campo': 'Fecha de Inicio de Actividad', 'valor_campo':
                datetime_to_string(proveedor.fecha_inicio_actividad)},
            {'nombre_campo': 'Fecha de Constitución', 'valor_campo':
                datetime_to_string(proveedor.fecha_inicio_actividad)},
            ]


def generar_datos_actividades_economicas(proveedor):
    ae = ProveedorActividadEconomica.objects.get(proveedor=proveedor)
    return [{'nombre_campo': 'Actividad Principal', 'valor_campo': ae.actividad_principal},
            {'nombre_campo': 'Actividad Secundaria', 'valor_campo': ae.actividad_secundaria},
            {'nombre_campo': 'Otra Actividad', 'valor_campo': ae.otra_actividad},
            {'nombre_campo': 'Régimen', 'valor_campo': ae.regimen},
            {'nombre_campo': 'Tipo de Contribuyente', 'valor_campo': ae.tipo_contribuyente},
            {'nombre_campo': 'Excento de Industria y Comercio: # Res', 'valor_campo': ae.numero_resolucion},
            {'nombre_campo': 'Contribuyente Industria y Comercio', 'valor_campo': ae.contribuyente_iyc},
            {'nombre_campo': 'Entidad Pública', 'valor_campo': ae.entidad_publica},
            {'nombre_campo': 'Bienes y Servicios', 'valor_campo': ae.bienes_servicios},
            ]


def generar_datos_entidades_bancarias(proveedor):
    entidades_bancarias = EntidadBancariaTercero.objects.filter(tercero=proveedor)
    lista_entidades = []
    for eb in entidades_bancarias:
        lista_entidades.append({'nombre_campo': eb.tipo_cuenta, 'valor_campo': eb.entidad_bancaria,
                                'archivo': '/administracion/proveedor/perfil/ver-certificacion/{0}/'.format(eb.id)})
    return lista_entidades


def generar_datos_bienes_servicios(proveedor):
    productos_servicios = ProveedorProductoServicio.objects.filter(proveedor=proveedor)
    lista_productos_servicios = []
    for ps in productos_servicios:
        lista_productos_servicios\
            .append({'nombre_campo': 'Servicio' if ps.producto_servicio.subtipo_producto_servicio.es_servicio
                     else "Producto", 'valor_campo': '{0} - {1}'
                    .format(ps.producto_servicio.subtipo_producto_servicio, ps.producto_servicio)})
    return lista_productos_servicios


def generar_datos_documentos(proveedor):
    documentos = DocumentoTercero.objects.filter(tercero=proveedor)
    lista_documentos = []
    for doc in documentos:
        lista_documentos\
            .append({'nombre_campo': doc.tipo_documento, 'valor_campo': 'Ver',
                     'archivo': '/administracion/proveedor/perfil/ver-documento/{0}/'.format(doc.id)})
    return lista_documentos
