import ast
import json
import os
from sqlite3 import IntegrityError

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from Administracion.enumeraciones import TipoPersona, RegimenFiscal, \
    EstadosProveedor, TipoContribuyente
from Administracion.models import TipoIdentificacion, Pais, Tercero, Departamento, Municipio
from Administracion.models.models import SubproductoSubservicio, ProductoServicio
from Administracion.models.terceros import ProveedorProductoServicio, TipoDocumentoTercero, DocumentoTercero, \
    SolicitudProveedor, Certificacion
from EVA.General import app_datetime_now, obtener_reporte
from EVA.General.conversiones import datetime_to_string
from EVA.views.index import AbstractEvaLoggedProveedorView, AbstractEvaLoggedView
from Financiero.enumeraciones import TipoCuentaBancaria
from Financiero.models.models import ActividadEconomica, ProveedorActividadEconomica, \
    EntidadBancariaTercero, EntidadBancaria
from Notificaciones.models.models import EventoDesencadenador, DestinatarioNotificacion
from Notificaciones.views.views import crear_notificacion_por_evento


class PerfilProveedorView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        proveedor = filtro_estado_proveedor(request)
        datos_proveedor = generar_datos_proveedor(proveedor)
        total = datos_proveedor['total']
        datos_estado = {}

        for ep in EstadosProveedor.choices:
            if proveedor.estado_proveedor == int(ep[0]):
                datos_estado = {'estado': proveedor.estado, 'estado_descripcion': ep[1]}

        certificaciones = Certificacion.objects.filter(tercero=proveedor).order_by('-id')
        if not certificaciones and not proveedor.es_vigente:
            certificaciones = Certificacion.objects\
                .filter(tercero__usuario=proveedor.usuario).order_by('-id')

        rechazos = DestinatarioNotificacion\
            .objects.filter(usuario=proveedor.usuario).order_by('-id')[:1]

        if certificaciones:
            datos_estado.update({'ultima_act': certificaciones.first().fecha_crea})

        if rechazos and not proveedor.estado:
            if 'Rechazada' in rechazos.first().notificacion.titulo:
                datos_estado.update({'estado_solicitud': rechazos.first().notificacion.mensaje})

        perfil_activo = True if Certificacion.objects.filter(tercero=proveedor, estado=True) else False
        btn_enviar = True if total == 100 else False
        solicitud_activa = True if SolicitudProveedor.objects.filter(proveedor=proveedor, estado=True) else False

        return render(request, 'Administracion/Tercero/Proveedor/perfil.html',
                      {'datos_proveedor': datos_proveedor, 'total': total, 'btn_enviar': btn_enviar,
                       'proveedor_id': proveedor.id, 'tipo_persona_pro': proveedor.tipo_persona,
                       'solicitud_activa': solicitud_activa, 'perfil_activo': perfil_activo,
                       'datos_estado': datos_estado, 'menu_actual': 'perfil'
                       })


class PerfilInformacionBasicaView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        return render(request, 'Administracion/Tercero/Proveedor/informacion_basica.html',
                      datos_xa_render_informacion_basica(request))

    def post(self, request):
        update_fields = ['nombre', 'tipo_identificacion_id', 'identificacion', 'ciudad', 'tipo_persona',
                         'telefono_movil_principal', 'telefono_fijo_auxiliar', 'telefono_movil_auxiliar',
                         'correo_principal', 'correo_auxiliar', 'fecha_inicio_actividad', 'fecha_constitucion',
                         'telefono_fijo_principal', 'estado_proveedor']

        exclude = ['centro_poblado', 'direccion', 'telefono']

        proveedor = filtro_estado_proveedor(request)

        proveedor.nombre = request.POST.get('nombre', '')
        proveedor.tipo_identificacion_id = request.POST.get('tipo_identificacion', '')
        proveedor.identificacion = request.POST.get('identificacion', '')
        proveedor.digito_verificacion = request.POST.get('digito_verificacion', '')
        proveedor.ciudad_id = request.POST.get('municipio', '')
        proveedor.estado_proveedor = EstadosProveedor.DILIGENCIAMIENTO_PERFIL
        proveedor.tipo_persona = request.POST.get('tipo_persona', '')

        if 'NIT' in proveedor.tipo_identificacion.sigla:
            update_fields.append('digito_verificacion')
        else:
            exclude.append('digito_verificacion')
        if int(proveedor.tipo_persona) == PERSONA_JURIDICA:
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
                         'bienes_servicios', 'proveedor', 'tipo_contribuyente')
        proveedor = filtro_estado_proveedor(request)
        proveedor_ae = ProveedorActividadEconomica.from_dictionary(request.POST)
        proveedor_ae.proveedor = proveedor
        proveedor.regimen_fiscal = request.POST.get('regimen_fiscal')

        try:
            registro = ProveedorActividadEconomica.objects.filter(proveedor=proveedor)
            if registro:
                proveedor_ae.id = registro.first().id
                proveedor_ae.save(update_fields=update_fields)
            else:
                proveedor_ae.save()
            proveedor.save(update_fields=['regimen_fiscal'])
            messages.success(self.request, 'Se ha guardado la información de actividades económicas correctamente.')
            return redirect(reverse('Administracion:proveedor-perfil'))
        except:
            messages.error(self.request, 'Ha ocurrido un error al actualizar la información.')
            return redirect(reverse('Administracion:proveedor-perfil'))


class EntidadesBancariasPerfilView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        tercero = filtro_estado_proveedor(request)
        entidades_bancarias = EntidadBancariaTercero.objects.filter(tercero=tercero)
        return render(request, 'Administracion/Tercero/Proveedor/entidades_bancarias.html',
                      {'entidades_bancarias': entidades_bancarias, 'fecha': app_datetime_now()})


class EntidadBancariaCrearView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        return render(request,
                      'Administracion/_common/_modal_gestionar_entidad_bancaria.html',
                      datos_xa_render_entidades_bancarias(request))

    def post(self, request):
        entidad_proveedor = EntidadBancariaTercero.from_dictionary(request.POST)
        entidad_proveedor.tercero = filtro_estado_proveedor(request)
        entidad_proveedor.certificacion = request.FILES.get('certificacion', '')
        entidad_proveedor.numero_cuenta = request.POST.get('numero_cuenta', '')
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
        update_fields = ['tipo_cuenta', 'entidad_bancaria', 'numero_cuenta']
        entidad_proveedor = EntidadBancariaTercero.from_dictionary(request.POST)
        entidad_proveedor.id = id
        entidad_proveedor.certificacion = request.FILES.get('certificacion', '')
        entidad_proveedor.tercero = filtro_estado_proveedor(request)
        entidad_proveedor.numero_cuenta = request.POST.get('numero_cuenta', '')
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
            response['Content-Disposition'] = 'inline; filename="{0} - Cuenta {1}{2}"'\
                .format(entidad_bancaria.entidad_bancaria.nombre,
                        'Corriente' if entidad_bancaria.tipo_cuenta == 1 else 'de Ahorros', extension)
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
        proveedor = filtro_estado_proveedor(request)
        try:
            ProveedorProductoServicio.objects.filter(proveedor=proveedor).delete()
            lista_selecciones = []
            if contador:
                cn = 0
                while cn < int(contador):
                    datos = request.POST.getlist('subproducto_subservicio_{0}'.format(cn), '')
                    if datos != '':
                        for dt in datos:
                            lista_selecciones.append(dt)
                    cn += 1
            else:
                datos = request.POST.getlist('producto_servicio_0', '')
                if datos != '':
                    for dt in datos:
                        lista_selecciones.append(dt)

            for lista_selec in set(lista_selecciones):
                ProveedorProductoServicio.objects.create(proveedor=proveedor,
                                                         subproducto_subservicio_id=lista_selec)

            messages.success(self.request, 'Se han guardado los productos y servicios correctamente.')
        except:
            messages.error(self.request, 'Ha ocurrido un error al guardar los datos')

        return redirect(reverse('Administracion:proveedor-perfil'))


class PerfilDocumentosView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        proveedor = filtro_estado_proveedor(request)

        if proveedor.tipo_persona == PERSONA_JURIDICA:
            documentos = DocumentoTercero.objects.filter(tercero=proveedor,
                                                         tipo_documento__aplica_juridica=True)
            tipos_documentos = TipoDocumentoTercero.objects.filter(aplica_juridica=True)
        else:
            documentos = DocumentoTercero.objects.filter(tercero=proveedor,
                                                         tipo_documento__aplica_natural=True)
            tipos_documentos = TipoDocumentoTercero.objects.filter(aplica_natural=True)

        agregar = verificar_documentos_proveedor(proveedor, documentos)
        porcentaje = 100 / len(tipos_documentos) * len(documentos)
        n_doc_oblig = 0
        n_tip_oblig = 0
        for doc in documentos:
            if doc.tipo_documento.obligatorio:
                n_doc_oblig += 1
        for tip_doc in tipos_documentos:
            if tip_doc.obligatorio:
                n_tip_oblig += 1

        return render(request, 'Administracion/Tercero/Proveedor/documentos.html', {'documentos': documentos,
                                                                                    'agregar': agregar,
                                                                                    'n_documentos': len(documentos),
                                                                                    'n_doc_oblig': n_doc_oblig,
                                                                                    'porcentaje': porcentaje,
                                                                                    'n_tip_oblig': n_tip_oblig,
                                                                                    'n_tipos': len(tipos_documentos)})


class DocumentoCrearView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        return render(request, 'Administracion/_common/_modal_gestionar_documento.html',
                      datos_xa_render_documentos(request))

    def post(self, request):
        proveedor = filtro_estado_proveedor(request)
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

    def post(self, request, id):
        documento = DocumentoTercero.objects.get(id=id)
        documento.documento = request.FILES.get('documento', '')
        try:
            documento.save(update_fields=['documento'])
        except:
            return JsonResponse({"estado": "error", "mensaje": "Ha ocurrido un error al guardar la información"})

        messages.success(self.request, 'Se ha cargado el documento {0} correctamente.'
                         .format(documento.tipo_documento.nombre))
        return JsonResponse({"estado": "OK"})


class PerfilDocumentosAdicionalesView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        proveedor = filtro_estado_proveedor(request)
        documentos = DocumentoTercero.objects.filter(tercero=proveedor, tipo_documento=None)
        return render(request, 'Administracion/Tercero/Proveedor/documentos.html', {'documentos': documentos,
                                                                                    'agregar_adicional': True})


class DocumentoAdicionalCrearView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        return render(request, 'Administracion/_common/_modal_gestionar_documento.html', {'documento_adicional': True})

    def post(self, request):
        proveedor = filtro_estado_proveedor(request)
        documento = DocumentoTercero()
        documento.nombre = request.POST.get('nombre', '')
        documento.tercero = proveedor
        documento.documento = request.FILES.get('documento', '')
        documento.estado = True
        try:
            documento.save()
        except:
            return JsonResponse({"estado": "error", "mensaje": "Ha ocurrido un error al guardar la información"})

        messages.success(self.request, 'Se ha cargado el documento {0} correctamente.'
                         .format(documento.nombre))
        return JsonResponse({"estado": "OK"})


class DocumentoAdicionalEditarView(AbstractEvaLoggedProveedorView):
    def get(self, request, id):
        documento = DocumentoTercero.objects.get(id=id)
        return render(request, 'Administracion/_common/_modal_gestionar_documento.html',
                      {'documento_adicional': True, 'documento': documento})

    def post(self, request, id):
        documento = DocumentoTercero.objects.get(id=id)
        documento.nombre = request.POST.get('nombre', '')
        documento.documento = request.FILES.get('documento', '')
        try:
            documento.save(update_fields=['documento', 'nombre'])
        except:
            return JsonResponse({"estado": "error", "mensaje": "Ha ocurrido un error al guardar la información"})

        messages.success(self.request, 'Se ha cargado el documento {0} correctamente.'
                         .format(documento.nombre))
        return JsonResponse({"estado": "OK"})


class DocumentoAdicionalEliminarView(AbstractEvaLoggedProveedorView):
    def post(self, request, id):
        documento = DocumentoTercero.objects.get(id=id)
        try:
            documento.delete()
            messages.success(request, 'Se ha eliminado el documento correctamente')
            return JsonResponse({"estado": "OK"})

        except IntegrityError:
            return JsonResponse({"estado": "error",
                                 "mensaje": "Ha ocurrido un error al realizar la acción"})


class EnviarSolicitudProveedorView(AbstractEvaLoggedView):
    def post(self, request, id):
        try:
            proveedor = Tercero.objects.get(id=id)
            proveedor.estado_proveedor = EstadosProveedor.SOLICITUD_ENVIADA
            proveedor.estado = False
            if SolicitudProveedor.objects.filter(proveedor=proveedor, estado=True):
                messages.warning(self.request, 'Ya se ha enviado una solicitud.')
            else:
                solicitud = SolicitudProveedor.objects.create(proveedor=proveedor, fecha_creacion=app_datetime_now(),
                                                              aprobado=False, estado=True)
                proveedor.save(update_fields=['estado_proveedor', 'estado'])
                messages.success(self.request, 'Se ha enviado la solicitud correctamente')
                if Certificacion.objects.filter(tercero__usuario=proveedor.usuario):
                    cambios = generar_comentario_cambios_tarjeta_solicitud(proveedor)
                    proveedor.modificaciones = cambios
                    proveedor.save(update_fields=['modificaciones'])
                    titulo = 'El proveedor {0} ha modificado su perfil.'.format(proveedor.nombre)

                    crear_notificacion_por_evento(EventoDesencadenador.SOLICITUD_APROBACION_PROVEEDOR, solicitud.id,
                                                  contenido={'titulo': titulo,
                                                             'mensaje': cambios['comentario']})

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
                .format(documento.tercero.nombre,
                        documento.tipo_documento.nombre if documento.tipo_documento else documento.nombre, extension)
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
        modificaciones_perfil = ''
        modificaciones_tarjetas = ''
        if proveedor.modificaciones:
            cambios = ast.literal_eval(proveedor.modificaciones)
            modificaciones_tarjetas = cambios['modificaciones_tarjetas']
            modificaciones_perfil = {'id': 0, 'nombre': 'Modificaciones Recientes',
                                     'datos': [{'nombre_campo': 'Cambios',
                                               'valor_campo': cambios['comentario']}]}

        return render(request, 'Administracion/Tercero/Proveedor/perfil.html',
                      {'datos_proveedor': datos_proveedor, 'solicitud_proveedor': proveedor,
                       'solicitud_activa': solicitud_activa, 'tipo_persona_pro': proveedor.tipo_persona,
                       'modificaciones_perfil': modificaciones_perfil,
                       'modificaciones_tarjetas': modificaciones_tarjetas})


APROBADO = 1
RECHAZADO = 2


class ProveedorSolicitudAprobarRechazar(AbstractEvaLoggedView):
    def get(self, request, id):
        proveedor = Tercero.objects.get(id=id)
        opciones = [{'texto': 'Aprobar', 'valor': 1},
                    {'texto': 'Rechazar', 'valor': 2}]
        return render(request, 'Administracion/_common/_modal_aprobar_rechazar_proveedor.html',
                      {'proveedor': proveedor, 'opciones': opciones})

    @transaction.atomic
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

                proveedor_anterior = Tercero.objects.filter(usuario=solicitud.proveedor.usuario)

                if len(proveedor_anterior) == 2:
                    proveedor_anterior = proveedor_anterior.get(es_vigente=True)
                    Certificacion.objects.filter(tercero=proveedor_anterior).update(tercero=id, estado=False)
                    proveedor_anterior.delete()

                Tercero.objects.filter(id=id).update(estado=True, es_vigente=True,
                                                     estado_proveedor=EstadosProveedor.ACTIVO)
            else:
                Tercero.objects.filter(id=id).update(estado_proveedor=EstadosProveedor.RECHAZADO)

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
    @transaction.atomic
    def post(self, request, id):
        try:
            SolicitudProveedor.objects.filter(proveedor_id=id).update(estado=False)
            Tercero.objects.filter(id=id).update(estado_proveedor=EstadosProveedor.EDICION_PERFIL)

            tercero = Tercero.objects.get(id=id)
            doble_tercero = duplicar_registro_proveedor(tercero)
            duplicar_registro_proveedor(ProveedorActividadEconomica.objects.get(proveedor_id=id),
                                        doble_tercero)
            for doc in DocumentoTercero.objects.filter(tercero_id=id):
                duplicar_registro_proveedor(doc, doble_tercero)
            for ib in EntidadBancariaTercero.objects.filter(tercero_id=id):
                duplicar_registro_proveedor(ib, doble_tercero)
            for ps in ProveedorProductoServicio.objects.filter(proveedor_id=id):
                duplicar_registro_proveedor(ps, doble_tercero)

            messages.success(self.request, 'Ahora puedes modificar tu perfil.')
            return JsonResponse({"estado": "OK"})

        except:
            return JsonResponse({"estado": "ERROR", "mensaje": "Ha ocurrido un error al realizar la solicitud"})


class CertificacionesView(AbstractEvaLoggedProveedorView):
    def get(self, request):
        proveedor = Tercero.objects.get(usuario=request.user, es_vigente=True)
        certificaciones = Certificacion.objects.filter(tercero=proveedor)
        return render(request, 'Administracion/Tercero/Proveedor/certificaciones.html',
                      {'certificaciones': certificaciones,
                       'fecha': app_datetime_now(),
                       'menu_actual': 'certificaciones'})


class GenerarCertificacionView(AbstractEvaLoggedProveedorView):
    def get(self, request, id):
        reporte = obtener_reporte('CertificadoProveedor.pdf', {'id_certificado': id})
        if reporte:
            http_response = HttpResponse(reporte, 'application/pdf')
            http_response['Content-Disposition'] = 'inline; filename="Certificado de proveedor.pdf"'
            return http_response
        else:
            messages.error(self.request, 'No se pudo generar la certificación')
            return redirect(reverse('Administracion:proveedor-certificaciones'))


@transaction.atomic
def duplicar_registro_proveedor(objeto, duplicado=None):
    if duplicado:
        objeto.tercero = duplicado
        objeto.proveedor = duplicado
    else:
        objeto.es_vigente = False
    objeto.id = None
    objeto.save()
    return objeto


def filtro_estado_proveedor(request):
    proveedor = Tercero.objects.filter(usuario=request.user)

    if proveedor.first().estado_proveedor == int(EstadosProveedor.EDICION_PERFIL):
        proveedor = proveedor.filter(es_vigente=False)
    else:
        proveedor = proveedor.filter(es_vigente=True)
    return proveedor.first()


def datos_xa_render_informacion_basica(request, proveedor: Tercero = None, errores=None):
    tipo_identificacion = TipoIdentificacion.objects.get_xa_select_activos()
    tipo_identificacion_personas = TipoIdentificacion.objects.get_xa_select_personas_activos()
    json_tipo_identificacion = TipoIdentificacion.objects.get_activos_like_json()
    paises = Pais.objects.get_xa_select_activos()
    if not proveedor:
        proveedor = filtro_estado_proveedor(request)

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
    proveedor = filtro_estado_proveedor(request)
    proveedor_actec = ProveedorActividadEconomica.objects.filter(proveedor=proveedor)
    if proveedor_actec:
        proveedor_actec = proveedor_actec.first()
    actividades_economicas = ActividadEconomica.objects.get_xa_select_actividades_con_codigo()
    entidades_publicas = [{'campo_valor': '1', 'campo_texto': 'Nacional'},
                          {'campo_valor': '2', 'campo_texto': 'Departamental'},
                          {'campo_valor': '3', 'campo_texto': 'Municipal'}]

    entidad_publica = True if PERSONA_JURIDICA == proveedor.tipo_persona else False

    datos = {'actividades_economicas': actividades_economicas,
             'entidades_publicas': entidades_publicas, 'proveedor': proveedor_actec,
             'entidad_publica': entidad_publica, 'regimenes_fiscales': RegimenFiscal.choices,
             'tipos_contribuyentes': TipoContribuyente.choices}
    return datos


def datos_xa_render_entidades_bancarias(request, objeto=None):
    proveedor = filtro_estado_proveedor(request)
    datos = EntidadBancariaTercero.objects.filter(tercero=proveedor)
    datos_proveedor = []
    if datos:
        for d in datos:
            datos_proveedor.append({'tipo_cuenta_id': d.tipo_cuenta,
                                    'tipo_cuenta_nombre': 'Cuenta Corriente'
                                    if d.tipo_cuenta == 1 else 'Cuenta de Ahorros',
                                    'entidad_bancaria_id': d.entidad_bancaria_id,
                                    'entidad_bancaria_nombre': d.entidad_bancaria.nombre,
                                    'id': d.id})
        datos_proveedor = json.dumps(datos_proveedor)

    entidades_bancarias = EntidadBancaria.objects.get_xa_select_activos()
    datos = {'entidades_bancarias': entidades_bancarias, 'tipos_cuentas': TipoCuentaBancaria.choices,
             'datos_proveedor': datos_proveedor, 'objeto': objeto}
    return datos


def datos_xa_render_productos_servicios(request):
    tipos_productos_servicios = [{'campo_valor': 1, 'campo_texto': 'Producto'},
                                 {'campo_valor': 2, 'campo_texto': 'Servicio'}]
    productos_servicios = ProductoServicio.objects.get_xa_select_activos()
    subproductos_subservicios = ProductoServicio.objects.get_xa_select_activos()
    proveedor = filtro_estado_proveedor(request)
    selecciones = ProveedorProductoServicio.objects.filter(proveedor=proveedor)
    lista_selecciones = []
    contador = 0
    for dt in selecciones:
        coincidencia = False
        for ls in lista_selecciones:
            if dt.subproducto_subservicio.producto_servicio_id == ls['producto_servicio']:
                coincidencia = True
        if not coincidencia:
            subpro_subserv = ProveedorProductoServicio\
                .objects.filter(proveedor=proveedor, subproducto_subservicio__producto_servicio=dt.
                                subproducto_subservicio.producto_servicio)
            lista_subpro_subser = []
            for ps in subpro_subserv:
                lista_subpro_subser.append(ps.subproducto_subservicio_id)
            lista_selecciones\
                .append({'tipo_producto_servicio': 2 if dt.subproducto_subservicio.producto_servicio.es_servicio else 1,
                         'nombre_tipos': 'tipo_producto_servicio_{0}'.format(contador),
                         'onchange_tipos': 'cambioTipoProductoServicio({0})'.format(contador),
                         'producto_servicio': dt.subproducto_subservicio.producto_servicio_id,
                         'nombre_producto_servicio': 'producto_servicio_{0}'.format(contador),
                         'onchange_producto_servicio': 'cambioProductoServicio({0})'.format(contador),
                         'datos_productos_servicios': ProductoServicio.objects.get_xa_select_activos()
                        .filter(es_servicio=dt.subproducto_subservicio.producto_servicio.es_servicio),
                         'subproductos_subservicios': lista_subpro_subser,
                         'nombre_subproducto_subservicio': 'subproducto_subservicio_{0}'.format(contador),
                         'datos_subproductos_subservicios': SubproductoSubservicio.objects.get_xa_select_activos()
                        .filter(producto_servicio=dt.subproducto_subservicio.producto_servicio),
                         'contador': contador})
            contador += 1

    datos = {'tipos_productos_servicios': tipos_productos_servicios,
             'productos_servicios': productos_servicios,
             'subproductos_subservicios': subproductos_subservicios,
             'selecciones': lista_selecciones,
             'contador': contador}
    return datos


def datos_xa_render_documentos(request, documento: DocumentoTercero = None):
    proveedor = filtro_estado_proveedor(request)
    if proveedor.tipo_persona == PERSONA_JURIDICA:
        tipos_documentos = TipoDocumentoTercero.objects.get_xa_select_con_opcionales_aplica_juridica()
    else:
        tipos_documentos = TipoDocumentoTercero.objects.get_xa_select_con_opcionales_aplica_natural()
    proveedor_vigente = Tercero.objects.filter(usuario=request.user)
    if len(proveedor_vigente) > 1:
        documentos_actuales = DocumentoTercero.objects.filter(tercero__usuario=request.user, tercero__es_vigente=False)
    else:
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
    lugar_exp_rl = ''
    if proveedor.ciudad:
        ubicacion = '{1} - {2} - {0}'.format(proveedor.ciudad.departamento.pais.nombre.capitalize(),
                                             proveedor.ciudad.departamento.nombre.capitalize(),
                                             proveedor.ciudad.nombre.capitalize())
    if proveedor.lugar_expedicion_rl:
        lugar_exp_rl = '{1} - {2} - {0}'.format(proveedor.lugar_expedicion_rl.departamento.pais.nombre.capitalize(),
                                                proveedor.lugar_expedicion_rl.departamento.nombre.capitalize(),
                                                proveedor.lugar_expedicion_rl.nombre.capitalize())
    if 'NIT' in proveedor.tipo_identificacion.sigla:
        proveedor.identificacion = '{0}-{1}'.format(proveedor.identificacion, proveedor.digito_verificacion)

    return [{'nombre_campo': 'Nombre', 'valor_campo': proveedor.nombre},
            {'nombre_campo': 'Identificación', 'valor_campo':
                '{0} {1}'.format(proveedor.tipo_identificacion.sigla, proveedor.identificacion)},
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
            {'nombre_campo': 'Lugar de Expedición del Documento del Representante Legal', 'valor_campo': lugar_exp_rl,
             'tipo_persona': 1, 'validar': True},
            {'nombre_campo': 'Nombre del Representante Legal', 'valor_campo': proveedor.nombre_rl, 'validar': True,
             'tipo_persona': 1},
            {'nombre_campo': 'Identificación del Representante Legal', 'tipo_persona': 1, 'validar': True,
             'valor_campo':
                 '{0} {1}'.format(proveedor.tipo_identificacion_rl.sigla if proveedor.tipo_identificacion_rl else '',
                                  proveedor.identificacion_rl) if proveedor.tipo_identificacion_rl else ''}
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

        tip_cont = ae.tipo_contribuyente
        tipo_contribuyente = ''
        for tc in TipoContribuyente.choices:
            if tc[0] == tip_cont:
                tipo_contribuyente = tc[1]
                break

        respuesta = [{'nombre_campo': 'Actividad Principal', 'valor_campo': ae.actividad_principal},
                     {'nombre_campo': 'Actividad Secundaria', 'valor_campo': ae.actividad_secundaria},
                     {'nombre_campo': 'Otra Actividad', 'valor_campo': ae.otra_actividad},
                     {'nombre_campo': 'Régimen Fiscal', 'valor_campo': regimen_fiscal},
                     {'nombre_campo': 'Tipo de Contribuyente', 'valor_campo': tipo_contribuyente},
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
        for tc in TipoCuentaBancaria.choices:
            if eb.tipo_cuenta == int(tc[0]):
                lista_entidades\
                    .append({'nombre_campo': tc[1],
                             'valor_campo': '{0} - N. {1}'.format(eb.entidad_bancaria, eb.numero_cuenta),
                             'archivo': '/administracion/proveedor/perfil/ver-certificacion/{0}/'.format(eb.id)})
    return lista_entidades


def generar_datos_bienes_servicios(proveedor):
    productos_servicios = ProveedorProductoServicio.objects.filter(proveedor=proveedor)
    productos = productos_servicios.filter(subproducto_subservicio__producto_servicio__es_servicio=False)
    servicios = productos_servicios.filter(subproducto_subservicio__producto_servicio__es_servicio=True)

    l_productos = obtener_pro_ser_con_sub(productos)
    l_servicios = obtener_pro_ser_con_sub(servicios)

    lista_productos_servicios = ''
    if l_productos or l_servicios:
        lista_productos_servicios = [{'nombre_campo': 'Productos', 'valor_campo': l_productos},
                                     {'nombre_campo': 'Servicios', 'valor_campo': l_servicios}]

    return lista_productos_servicios


def obtener_pro_ser_con_sub(objeto):
    lista_datos = []
    for ob in objeto.distinct('subproducto_subservicio__producto_servicio'):
        lista_subdatos = []
        for sub_ob in objeto:
            if sub_ob.subproducto_subservicio.producto_servicio == ob.subproducto_subservicio.producto_servicio:
                lista_subdatos.append(sub_ob.subproducto_subservicio.nombre)
        lista_datos.append({'objeto': ob.subproducto_subservicio.producto_servicio.nombre, 'sub': lista_subdatos})
    return lista_datos


def generar_datos_documentos(proveedor):
    documentos = DocumentoTercero.objects.filter(tercero=proveedor)
    if proveedor.tipo_persona == PERSONA_JURIDICA:
        documentos = documentos.filter(tipo_documento__aplica_juridica=True)
    else:
        documentos = documentos.filter(tipo_documento__aplica_natural=True)
    lista_documentos = []
    for doc in documentos:
        lista_documentos\
            .append({'nombre_campo': doc.tipo_documento, 'valor_campo': 'Ver',
                     'archivo': '/administracion/proveedor/perfil/ver-documento/{0}/'.format(doc.id)})
    return lista_documentos


def generar_datos_documentos_adicionales(proveedor):
    documentos = DocumentoTercero.objects.filter(tercero=proveedor, tipo_documento=None)
    lista_documentos = []
    for doc in documentos:
        lista_documentos\
            .append({'nombre_campo': doc.nombre, 'valor_campo': 'Ver',
                     'archivo': '/administracion/proveedor/perfil/ver-documento/{0}/'.format(doc.id)})
    return lista_documentos


def generar_datos_proveedor(proveedor):
    informacion_basica = generar_datos_informacion_basica(proveedor)
    actividades_economicas = generar_datos_actividades_economicas(proveedor)
    entidades_bancarias = generar_datos_entidades_bancarias(proveedor)
    bienes_servicios = generar_datos_bienes_servicios(proveedor)
    documentos = generar_datos_documentos(proveedor)
    documentos_adicionales = generar_datos_documentos_adicionales(proveedor)
    if proveedor.tipo_persona == PERSONA_JURIDICA:
        lista_documentos = TipoDocumentoTercero.objects.filter(aplica_juridica=True)
    else:
        lista_documentos = TipoDocumentoTercero.objects.filter(aplica_juridica=True)
    n_tipos = 0
    n_documentos = 0

    for ld in lista_documentos:
        if ld.obligatorio:
            n_tipos += 1

    docs = DocumentoTercero.objects.filter(tercero=proveedor)
    for doc in docs:
        if proveedor.tipo_persona == TipoPersona.NATURAL:
            if doc.tipo_documento:
                if doc.tipo_documento.obligatorio:
                    n_documentos += 1
        else:
            if doc.tipo_documento:
                if doc.tipo_documento.obligatorio:
                    n_documentos += 1

    total = 0
    total = total + 10 if proveedor.ciudad else total
    total = total + 10 if informacion_basica else total
    total = total + 20 if actividades_economicas else total
    total = total + 20 if entidades_bancarias else total
    total = total + 20 if bienes_servicios else total
    total = total + 20 if n_documentos == n_tipos else total

    cambios = ast.literal_eval(proveedor.modificaciones)['modificaciones_tarjetas']

    informacion_basica = {'id': 1, 'nombre': 'Información Básica', 'modificado': True if 1 in cambios else False,
                          'url': '/administracion/proveedor/perfil/informacion-basica',
                          'datos': informacion_basica, 'completo': True if proveedor.ciudad else False}
    actividades_economicas = {'id': 2, 'nombre': 'Actividades Económicas', 'modificado': True if 2 in cambios else False,
                              'url': '/administracion/proveedor/perfil/actividades-economicas',
                              'datos': actividades_economicas, 'completo': True if actividades_economicas else False}
    documentos = {'id': 3, 'nombre': 'Documentos', 'url': '/administracion/proveedor/perfil/documentos',
                  'datos': documentos, 'completo': True if documentos else False,
                  'modificado': True if 3 in cambios else False}
    entidades_bancarias = {'id': 4, 'nombre': 'Información Bancaria', 'modificado': True if 4 in cambios else False,
                           'url': '/administracion/proveedor/perfil/entidades-bancarias',
                           'datos': entidades_bancarias, 'completo': True if entidades_bancarias else False}
    bienes_servicios = {'id': 5, 'nombre': 'Productos y Servicios', 'modificado': True if 5 in cambios else False,
                        'url': '/administracion/proveedor/perfil/productos-servicios',
                        'datos': bienes_servicios, 'completo': True if bienes_servicios else False}
    documentos_adicionales = {'id': 6, 'nombre': 'Certificaciones y Documentos Adicionales',
                              'url': '/administracion/proveedor/perfil/documentos-adicionales',
                              'datos': documentos_adicionales, 'modificado': True if 6 in cambios else False,
                              'completo': True}

    return {'total': total, 'informacion_basica': informacion_basica, 'actividades_economicas': actividades_economicas,
            'entidades_bancarias': entidades_bancarias, 'bienes_servicios': bienes_servicios, 'documentos': documentos,
            'documentos_adicionales': documentos_adicionales}


def generar_comentario_cambios_tarjeta_solicitud(proveedor):
    proveedor = Tercero.objects.filter(usuario=proveedor.usuario)
    proveedor_vigente = proveedor.get(es_vigente=True)
    proveedor_editado = proveedor.get(es_vigente=False)
    modificaciones = ''
    lista_tarjeta_modificaciones = []
    if not proveedor_vigente.comparar(proveedor_editado, excluir=['id', 'es_vigente', 'estado', 'fecha_creacion',
                                                                  'fecha_modificacion', 'estado_proveedor',
                                                                  'regimen_fiscal']):
        modificaciones += 'Información Básica, '
        lista_tarjeta_modificaciones.append(1)

    av = ProveedorActividadEconomica.objects.get(proveedor=proveedor_vigente)
    ae = ProveedorActividadEconomica.objects.get(proveedor=proveedor_editado)
    if not av.comparar(ae, excluir=['id', 'proveedor']) or \
            proveedor_vigente.regimen_fiscal != proveedor_editado.regimen_fiscal:
        modificaciones += 'Actividades Económicas, '
        lista_tarjeta_modificaciones.append(2)

    ebv = EntidadBancariaTercero.objects.filter(tercero=proveedor_vigente)
    ebe = EntidadBancariaTercero.objects.filter(tercero=proveedor_editado)

    if validar_cambios_proveedor(ebv, ebe):
        modificaciones += 'Entidades Bancarias, '
        lista_tarjeta_modificaciones.append(4)

    bsv = ProveedorProductoServicio.objects.filter(proveedor=proveedor_vigente)
    bse = ProveedorProductoServicio.objects.filter(proveedor=proveedor_editado)

    if validar_cambios_proveedor(bsv, bse):
        modificaciones += 'Productos y Servicios, '
        lista_tarjeta_modificaciones.append(5)

    drv = DocumentoTercero.objects.filter(tercero=proveedor_vigente, tipo_documento__isnull=False)
    dre = DocumentoTercero.objects.filter(tercero=proveedor_editado, tipo_documento__isnull=False)

    if validar_cambios_proveedor(drv, dre):
        modificaciones += 'Documentos Requeridos, '
        lista_tarjeta_modificaciones.append(3)

    dav = DocumentoTercero.objects.filter(tercero=proveedor_vigente, tipo_documento__isnull=True)
    dae = DocumentoTercero.objects.filter(tercero=proveedor_editado, tipo_documento__isnull=True)

    if validar_cambios_proveedor(dav, dae):
        modificaciones += 'Documentos Adicionales.'
        lista_tarjeta_modificaciones.append(6)

    if modificaciones != '':
        if modificaciones[-1] == ' ':
            temp = len(modificaciones)
            comentario = 'Realizó cambios en {0}.'.format(modificaciones[:temp - 2])
        else:
            comentario = 'Realizó cambios en {0}'.format(modificaciones)
    else:
        comentario = 'No realizó modificaciones en su perfil.'

    return {'comentario': comentario, 'modificaciones_tarjetas': lista_tarjeta_modificaciones}


def validar_cambios_proveedor(objeto_vigente, objeto_editado):
    cambios = False
    if len(objeto_vigente) != len(objeto_editado):
        cambios = True
    else:
        for obv in objeto_vigente:
            coincidencia = False
            for obe in objeto_editado:
                if obv.comparar(obe, excluir=['id', 'proveedor', 'tercero']):
                    coincidencia = True
                    break
            if not coincidencia:
                cambios = True
    return cambios