import json
import os
from sqlite3 import IntegrityError

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from Administracion.enumeraciones import TipoPersona, RegimenFiscal, ResponsabilidadesFiscales, Tributos
from Administracion.models import TipoIdentificacion, Pais, Tercero, Departamento, Municipio
from Administracion.models.models import SubtipoProductoServicio, ProductoServicio
from Administracion.models.terceros import ProveedorProductoServicio, TipoDocumentoTercero, DocumentoTercero, \
    SolicitudProveedor, Certificacion
from EVA.General import app_datetime_now
from EVA.General.conversiones import datetime_to_string
from EVA.views.index import AbstractEvaLoggedProveedorView, AbstractEvaLoggedView
from Financiero.models.models import ActividadEconomica, TipoContribuyente, Regimen, ProveedorActividadEconomica, \
    EntidadBancariaTercero, EntidadBancaria, TipoCuentaBancaria
from Notificaciones.models.models import EventoDesencadenador
from Notificaciones.views.views import crear_notificacion_por_evento


class PerfilProveedorView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        proveedor = Tercero.objects.get(usuario=request.user)
        datos_proveedor = generar_datos_proveedor(proveedor)

        total = datos_proveedor['total']

        perfil_activo = True if Certificacion.objects.filter(tercero=proveedor, estado=True) else False

        btn_enviar = True if total == 100 else False
        solicitud_activa = True if SolicitudProveedor.objects.filter(proveedor=proveedor, estado=True) else False
        tipo_nit = True if proveedor.tipo_identificacion.sigla == 'NIT' else False

        return render(request, 'Administracion/Tercero/Proveedor/perfil.html',
                      {'datos_proveedor': datos_proveedor, 'total': total, 'btn_enviar': btn_enviar,
                       'tipo_nit': tipo_nit, 'proveedor_id': proveedor.id,
                       'solicitud_activa': solicitud_activa, 'perfil_activo': perfil_activo,
                       })


class PerfilInformacionBasicaView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        return render(request, 'Administracion/Tercero/Proveedor/informacion_basica.html',
                      datos_xa_render_informacion_basica(request))

    def post(self, request):
        update_fields = ['nombre', 'tipo_identificacion_id', 'identificacion', 'ciudad', 'tipo_persona',
                         'telefono_movil_principal', 'telefono_fijo_auxiliar', 'telefono_movil_auxiliar',
                         'correo_principal', 'correo_auxiliar', 'fecha_inicio_actividad', 'fecha_constitucion',
                         'telefono_fijo_principal']

        exclude = ['centro_poblado', 'direccion', 'telefono']

        proveedor = Tercero.objects.get(usuario=request.user)

        proveedor.nombre = request.POST.get('nombre', '')
        proveedor.tipo_identificacion_id = request.POST.get('tipo_identificacion', '')
        proveedor.identificacion = request.POST.get('identificacion', '')
        proveedor.digito_verificacion = request.POST.get('digito_verificacion', '')
        proveedor.ciudad_id = request.POST.get('municipio', '')

        if 'NIT' in proveedor.tipo_identificacion.sigla:
            update_fields.append('digito_verificacion')
        else:
            exclude.append('digito_verificacion')

        if proveedor.tipo_persona == PERSONA_JURIDICA:
            update_fields.append('nombre_rl')
            update_fields.append('tipo_identificacion_rl')
            update_fields.append('identificacion_rl')
            update_fields.append('lugar_expedicion_rl')
            proveedor.nombre_rl = request.POST.get('nombre_rl', '')
            proveedor.tipo_identificacion_rl_id = request.POST.get('tipo_identificacion_rl', '')
            proveedor.identificacion_rl = request.POST.get('identificacion_rl', '')
            proveedor.lugar_expedicion_rl_id = request.POST.get('municipio_rl', '')
        else:
            exclude.append('tipo_identificacion_rl')

        proveedor.telefono_fijo_principal = request.POST.get('fijo_principal', '')
        proveedor.telefono_movil_principal = request.POST.get('movil_principal', '')
        proveedor.telefono_fijo_auxiliar = request.POST.get('fijo_auxiliar', '')
        proveedor.telefono_movil_auxiliar = request.POST.get('movil_auxiliar', '')
        proveedor.correo_principal = request.POST.get('correo_pincipal', '')
        proveedor.correo_auxiliar = request.POST.get('correo_auxiliar', '')

        proveedor.fecha_inicio_actividad = request.POST.get('fecha_inicio_actividad', '')
        proveedor.fecha_constitucion = request.POST.get('fecha_constitucion', '')
        proveedor.tipo_persona = request.POST.get('tipo_persona', '')

        if not proveedor.fecha_inicio_actividad:
            proveedor.fecha_inicio_actividad = None

        if not proveedor.fecha_constitucion:
            proveedor.fecha_constitucion = None

        try:
            proveedor.full_clean(exclude=exclude)
        except ValidationError as errores:
            if 'identificacion' in errores.message_dict:
                messages.error(self.request, 'El número de identificación ingresado ya se encuentra registrado')
                return render(request, 'Administracion/Tercero/Proveedor/informacion_basica.html',
                              datos_xa_render_informacion_basica(request, proveedor, errores.message_dict))
            messages.error(self.request, 'Ha ocurrido un error al actualizar la información.')
            return redirect(reverse('Administracion:proveedor-perfil'))

        proveedor.save(update_fields=update_fields)
        messages.success(self.request, 'Se ha guardado la información básica correctamente.')
        return redirect(reverse('Administracion:proveedor-perfil'))


class PerfilActividadesEconomicasView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        return render(request, 'Administracion/Tercero/Proveedor/actividades_economicas.html',
                      datos_xa_render_actividades_economicas(request))

    def post(self, request):
        update_fields = ('actividad_principal', 'actividad_secundaria', 'otra_actividad', 'contribuyente_iyc',
                         'numero_resolucion', 'contribuyente_iyc', 'entidad_publica', 'proveedor',
                         'bienes_servicios', 'proveedor')
        proveedor = Tercero.objects.get(usuario=request.user)
        proveedor_ae = ProveedorActividadEconomica.from_dictionary(request.POST)
        proveedor_ae.proveedor = proveedor
        proveedor.regimen_fiscal = request.POST.get('regimen_fiscal')
        responsabilidades = request.POST.getlist('responsabilidades')
        proveedor.responsabilidades_fiscales = ';'.join(responsabilidades) if responsabilidades else ''
        proveedor.tributos = request.POST.get('tributo')

        try:
            registro = ProveedorActividadEconomica.objects.filter(proveedor=proveedor)
            if registro:
                proveedor_ae.id = registro.first().id
                proveedor_ae.save(update_fields=update_fields)
            else:
                proveedor_ae.save()
            proveedor.save(update_fields=('responsabilidades_fiscales', 'regimen_fiscal', 'tributos'))
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
            messages.success(self.request, 'Se han guardado los productos y servicios correctamente.')
        except:
            messages.error(self.request, 'Ha ocurrido un error al guardar los datos')

        return redirect(reverse('Administracion:proveedor-perfil'))


class PerfilDocumentosView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        proveedor = Tercero.objects.get(usuario=request.user)

        if proveedor.tipo_persona == PERSONA_JURIDICA:
            documentos = DocumentoTercero.objects.filter(tercero=proveedor, tipo_documento__aplica_juridica=True)
            tipos_documentos = TipoDocumentoTercero.objects.filter(aplica_juridica=True)
        else:
            documentos = DocumentoTercero.objects.filter(tercero=proveedor, tipo_documento__aplica_natural=True)
            tipos_documentos = TipoDocumentoTercero.objects.filter(aplica_natural=True)

        agregar = verificar_documentos_proveedor(proveedor, documentos)
        return render(request, 'Administracion/Tercero/Proveedor/documentos.html', {'documentos': documentos,
                                                                                    'agregar': agregar,
                                                                                    'n_documentos': len(documentos),
                                                                                    'n_tipos': len(tipos_documentos)})


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
        documento.estado = True
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


class EnviarSolicitudProveedorView(AbstractEvaLoggedView):
    def post(self, request, id):
        try:
            proveedor = Tercero.objects.get(id=id)
            solicitud = SolicitudProveedor.objects.create(proveedor=proveedor, fecha_creacion=app_datetime_now(),
                                                          aprobado=False, estado=True)
            messages.success(self.request, 'Se ha enviado la solicitud correctamente')
            if Certificacion.objects.filter(tercero=proveedor):
                titulo = 'Un proveedor ha modificado su perfil.'
                comentario = 'El proveedor {0} ha modificado su perfil'.format(proveedor.nombre)
                crear_notificacion_por_evento(EventoDesencadenador.SOLICITUD_APROBACION_PROVEEDOR, solicitud.id,
                                              contenido={'titulo': titulo,
                                                         'mensaje': comentario})

            else:
                crear_notificacion_por_evento(EventoDesencadenador.SOLICITUD_APROBACION_PROVEEDOR, solicitud.id)

            return JsonResponse({"estado": "OK"})
        except:
            return JsonResponse({"estado": "ERROR", "mensaje": "Ha ocurrido un error al realizar la solicitud"})


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


class SolicitudesProveedorView(AbstractEvaLoggedView):
    def get(self, request):
        solicitudes = SolicitudProveedor.objects.filter(estado=True)
        return render(request, 'Administracion/Tercero/Proveedor/solicitudes_proveedores.html',
                      {'solicitudes': solicitudes, 'menu_actual': ['proveedores', 'solicitudes_proveedor']})


class PerfilProveedorSolicitud(AbstractEvaLoggedView):
    def get(self, request, id):
        proveedor = Tercero.objects.get(id=id)
        datos_proveedor = generar_datos_proveedor(proveedor)
        solicitud_activa = SolicitudProveedor.objects.filter(proveedor=proveedor, estado=True)

        return render(request, 'Administracion/Tercero/Proveedor/perfil.html',
                      {'datos_proveedor': datos_proveedor, 'solicitud_proveedor': proveedor,
                       'solicitud_activa': solicitud_activa})


APROBADO = 1
RECHAZADO = 2


class ProveedorSolicitudAprobarRechazar(AbstractEvaLoggedView):
    def get(self, request, id):
        proveedor = Tercero.objects.get(id=id)
        opciones = [{'texto': 'Aprobar', 'valor': 1},
                    {'texto': 'Rechazar', 'valor': 2}]
        return render(request, 'Administracion/_common/_modal_aprobar_rechazar_proveedor.html',
                      {'proveedor': proveedor, 'opciones': opciones})

    def post(self, request, id):
        try:
            solicitud = SolicitudProveedor.objects.get(proveedor_id=id, estado=True)
            opcion = request.POST.get('opcion', '')
            comentario = request.POST.get('comentario', '')
            solicitud.aprobado = True if int(opcion) == APROBADO else False
            solicitud.comentarios = comentario
            solicitud.estado = False
            solicitud.save(update_fields=['aprobado', 'comentarios', 'estado'])
            if solicitud.aprobado:
                Certificacion.objects.filter(tercero=solicitud.proveedor).update(estado=False)
                Certificacion.objects.create(tercero=solicitud.proveedor, fecha_crea=app_datetime_now(), estado=True)
            messages.success(self.request, 'Se ha {0} la solicitud correctamente.'
                             .format('aprobado' if solicitud.aprobado else 'rechazado'))

            titulo = 'Solicitud Aprobada' if solicitud.aprobado else 'Solicitud Rechazada'
            crear_notificacion_por_evento(EventoDesencadenador.RESPUESTA_SOLICITUD_PROVEEDOR, solicitud.id,
                                          contenido={'titulo': titulo,
                                                     'mensaje': comentario,
                                                     'usuario': solicitud.proveedor.usuario_id})
        except:
            messages.error(self.request, 'Ha ocurrido un error al realizar la acción.')

        return redirect(reverse('Administracion:proveedor-solicitudes'))


class ProveedorModificarSolicitudView(AbstractEvaLoggedProveedorView):
    def post(self, request, id):
        try:
            SolicitudProveedor.objects.filter(proveedor_id=id).update(estado=False)
            Tercero.objects.filter(id=id).update(estado=False)
            Certificacion.objects.filter(tercero_id=id).update(estado=False)

            messages.success(self.request, 'Ahora puedes modificar tu perfil.')
            return JsonResponse({"estado": "OK"})
        except:
            return JsonResponse({"estado": "ERROR", "mensaje": "Ha ocurrido un error al realizar la solicitud"})


def datos_xa_render_informacion_basica(request, proveedor: Tercero = None, errores=None):
    tipo_identificacion = TipoIdentificacion.objects.get_xa_select_activos()
    tipo_identificacion_personas = TipoIdentificacion.objects.get_xa_select_personas_activos()
    json_tipo_identificacion = TipoIdentificacion.objects.get_activos_like_json()
    paises = Pais.objects.get_xa_select_activos()
    if not proveedor:
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
             'municipios_rl': municipios_rl, 'tipos_persona': TipoPersona.choices, 'errores': errores}
    return datos


PERSONA_JURIDICA = 1
PERSONA_NATURAL = 2


def datos_xa_render_actividades_economicas(request):
    proveedor = Tercero.objects.get(usuario=request.user)
    proveedor_actec = ProveedorActividadEconomica.objects.filter(proveedor=proveedor)
    if proveedor_actec:
        proveedor_actec = proveedor_actec.first()
    actividades_economicas = ActividadEconomica.objects.get_xa_select_actividades_con_codigo()
    datos_regimenes = Regimen.objects.get_activos_like_json()
    entidades_publicas = [{'campo_valor': '1', 'campo_texto': 'Nacional'},
                          {'campo_valor': '2', 'campo_texto': 'Departamental'},
                          {'campo_valor': '3', 'campo_texto': 'Municipal'}]

    entidad_publica = True if PERSONA_JURIDICA == proveedor.tipo_persona else False

    responsabilidades_tercero = proveedor.responsabilidades_fiscales.split(';') \
        if proveedor.responsabilidades_fiscales else []

    datos = {'actividades_economicas': actividades_economicas, 'datos_regimenes': datos_regimenes,
             'entidades_publicas': entidades_publicas, 'proveedor': proveedor_actec,
             'entidad_publica': entidad_publica, 'regimenes_fiscales': RegimenFiscal.choices,
             'responsabilidades': ResponsabilidadesFiscales.choices, 'tributos': Tributos.choices,
             'responsabilidades_tercero': responsabilidades_tercero}
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
    if proveedor.tipo_persona == PERSONA_JURIDICA:
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
    if proveedor.tipo_persona == PERSONA_JURIDICA:
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
    ubicacion = ''
    fecha_exp_rl = ''
    if proveedor.ciudad:
        ubicacion = '{1} - {2} - {0}'.format(proveedor.ciudad.departamento.pais.nombre.capitalize(),
                                             proveedor.ciudad.departamento.nombre.capitalize(),
                                             proveedor.ciudad.nombre.capitalize())
    if proveedor.lugar_expedicion_rl:
        fecha_exp_rl = '{1} - {2} - {0}'.format(proveedor.lugar_expedicion_rl.departamento.pais.nombre.capitalize(),
                                                proveedor.lugar_expedicion_rl.departamento.nombre.capitalize(),
                                                proveedor.lugar_expedicion_rl.nombre.capitalize())
    if 'NIT' in proveedor.tipo_identificacion.sigla:
        proveedor.identificacion = '{0}-{1}'.format(proveedor.identificacion, proveedor.digito_verificacion)

    return [{'nombre_campo': 'Nombre', 'valor_campo': proveedor.nombre},
            {'nombre_campo': 'Tipo de Identificación', 'valor_campo': proveedor.tipo_identificacion.nombre},
            {'nombre_campo': 'Identificación', 'valor_campo': proveedor.identificacion},
            {'nombre_campo': 'Ubicación', 'valor_campo': ubicacion},
            {'nombre_campo': 'Teléfono Fijo Principal', 'valor_campo': proveedor.telefono_fijo_principal},
            {'nombre_campo': 'Teléfono Movil Principal', 'valor_campo': proveedor.telefono_movil_principal},
            {'nombre_campo': 'Teléfono Fijo Auxiliar', 'valor_campo': proveedor.telefono_fijo_auxiliar},
            {'nombre_campo': 'Teléfono Movil Auxiliar', 'valor_campo': proveedor.telefono_movil_auxiliar},
            {'nombre_campo': 'Correo Electrónico Principal', 'valor_campo': proveedor.correo_principal},
            {'nombre_campo': 'Correo Electrónico Auxiliar', 'valor_campo': proveedor.correo_auxiliar},
            {'nombre_campo': 'Tipo de Persona', 'valor_campo': 'Jurídica' if proveedor.tipo_persona == 1 else 'Natural'},
            {'nombre_campo': 'Fecha de Inicio de Actividad', 'tipo_persona': 2, 'validar': True, 'valor_campo':
                datetime_to_string(proveedor.fecha_inicio_actividad) if proveedor.fecha_inicio_actividad else '',
             'tipo_persona_pro': proveedor.tipo_persona},
            {'nombre_campo': 'Fecha de Constitución', 'tipo_persona': 1, 'validar': True, 'valor_campo':
                datetime_to_string(proveedor.fecha_inicio_actividad) if proveedor.fecha_inicio_actividad else '',
             'tipo_persona_pro': proveedor.tipo_persona},
            {'nombre_campo': 'Fecha de Expedición del Documento del Representante Legal', 'valor_campo': fecha_exp_rl,
             'tipo_nit': True, 'validar': True},
            {'nombre_campo': 'Nombre del Representante Legal', 'valor_campo': proveedor.nombre_rl, 'validar': True,
             'tipo_nit': True},
            {'nombre_campo': 'Tipo de Identificación del Representante Legal', 'tipo_nit': True, 'validar': True,
             'valor_campo': proveedor.identificacion_rl},
            {'nombre_campo': 'Identificación del Representante Legal', 'tipo_nit': True, 'validar': True,
             'valor_campo': proveedor.identificacion_rl}
            ]


def generar_datos_actividades_economicas(proveedor):
    ae = ProveedorActividadEconomica.objects.filter(proveedor=proveedor)
    respuesta = ''
    if ae:
        ae = ae.first()
        if ae.entidad_publica == '1':
            entidad_publica = 'Nacional'
        elif ae.entidad_publica == '2':
            entidad_publica = 'Departamental'
        else:
            entidad_publica = 'Municipal'

        reg_fisc = proveedor.regimen_fiscal
        regimen_fiscal = ''
        for d in RegimenFiscal.choices:
            if d[0] == reg_fisc:
                regimen_fiscal = d[1]
                break

        resp_fiscal = proveedor.responsabilidades_fiscales
        datos_resp_fiscal = ''
        for sel in resp_fiscal.split(';'):
            for op in ResponsabilidadesFiscales.choices:
                if op[0] == sel:
                    datos_resp_fiscal += ', ' + op[1] if datos_resp_fiscal else op[1]

        trib = proveedor.tributos
        tributos = ''
        for tr in Tributos.choices:
            if tr[0] == trib:
                tributos = tr[1]
                break
        respuesta = [{'nombre_campo': 'Actividad Principal', 'valor_campo': ae.actividad_principal},
                     {'nombre_campo': 'Actividad Secundaria', 'valor_campo': ae.actividad_secundaria},
                     {'nombre_campo': 'Otra Actividad', 'valor_campo': ae.otra_actividad},
                     {'nombre_campo': 'Régimen Fiscal', 'valor_campo': regimen_fiscal},
                     {'nombre_campo': 'Responsabilidad Fiscal', 'valor_campo': datos_resp_fiscal},
                     {'nombre_campo': 'Tributo', 'valor_campo': tributos},
                     {'nombre_campo': 'Excento de Industria y Comercio: # Res', 'valor_campo': ae.numero_resolucion},
                     {'nombre_campo': 'Contribuyente Industria y Comercio', 'valor_campo': ae.contribuyente_iyc},
                     {'nombre_campo': 'Entidad Pública', 'valor_campo': entidad_publica},
                     {'nombre_campo': 'Bienes y Servicios', 'valor_campo': ae.bienes_servicios},
                     ]
    return respuesta


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


def generar_datos_proveedor(proveedor):
    informacion_basica = generar_datos_informacion_basica(proveedor)
    actividades_economicas = generar_datos_actividades_economicas(proveedor)
    entidades_bancarias = generar_datos_entidades_bancarias(proveedor)
    bienes_servicios = generar_datos_bienes_servicios(proveedor)
    documentos = generar_datos_documentos(proveedor)
    if proveedor.tipo_persona == PERSONA_JURIDICA:
        lista_documentos = len(TipoDocumentoTercero.objects.filter(aplica_juridica=True))
    else:
        lista_documentos = len(TipoDocumentoTercero.objects.filter(aplica_juridica=True))

    total = 0
    total = total + 10 if proveedor.ciudad else total
    total = total + 10 if informacion_basica else total
    total = total + 20 if actividades_economicas else total
    total = total + 20 if entidades_bancarias else total
    total = total + 20 if bienes_servicios else total
    total = total + 20 if len(documentos) == lista_documentos else total

    informacion_basica = {'id': 1, 'nombre': 'Información Básica',
                          'url': '/administracion/proveedor/perfil/informacion-basica',
                          'datos': informacion_basica}
    actividades_economicas = {'id': 2, 'nombre': 'Actividades Económicas',
                              'url': '/administracion/proveedor/perfil/actividades-economicas',
                              'datos': actividades_economicas}
    entidades_bancarias = {'id': 3, 'nombre': 'Entidades Bancarias',
                           'url': '/administracion/proveedor/perfil/entidades-bancarias',
                           'datos': entidades_bancarias}
    bienes_servicios = {'id': 4, 'nombre': 'Productos y Servicios',
                        'url': '/administracion/proveedor/perfil/productos-servicios',
                        'datos': bienes_servicios}
    documentos = {'id': 5, 'nombre': 'Documentos',
                  'url': '/administracion/proveedor/perfil/documentos', 'datos': documentos}

    return {'total': total, 'informacion_basica': informacion_basica, 'actividades_economicas': actividades_economicas,
            'entidades_bancarias': entidades_bancarias, 'bienes_servicios': bienes_servicios, 'documentos': documentos}
