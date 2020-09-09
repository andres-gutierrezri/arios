import json
from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import F

from Administracion.utils import get_id_empresa_global
from EVA.General.conversiones import decimal_para_input_number
from EVA.views.index import AbstractEvaLoggedView
from Notificaciones.models.models import EventoDesencadenador
from Notificaciones.views.views import crear_notificacion_por_evento
from Proyectos.models.contratos import Contrato, TipoGarantia, ContratoMunicipio, FormasPago, ContratoVigencia, \
    ContratoIterventoriaSupervisor, ContratoGarantia
from Administracion.models import Tercero, Empresa, TipoContrato, Proceso, Pais, TipoTercero
from TalentoHumano.models import Colaborador


SUPERVISOR = 0
INTERVENTOR = 1


class ContratoView(AbstractEvaLoggedView):
    def get(self, request):
        contratos = Contrato.objects.filter(empresa_id=get_id_empresa_global(request))
        fecha = datetime.now()
        return render(request, 'Proyectos/Contrato/index.html', {'contratos': contratos, 'fecha': fecha,
                                                                 'menu_actual': 'contratos'})


class ContratoCrearView(AbstractEvaLoggedView):
    OPCION = 'crear'

    def get(self, request):
        return render(request, 'Proyectos/Contrato/crear-editar.html', datos_xa_render(self.OPCION))

    def post(self, request):
        contrato = Contrato.from_dictionary(request.POST)
        municipios = request.POST.getlist('municipio_id[]', [])
        supervisores = request.POST.getlist('supervisor_id[]', [])
        interventores = request.POST.getlist('interventor_id[]', [])

        anho_vigencia = request.POST.get('anho_vigencia', '')
        valor_vigencia = request.POST.get('valor_vigencia', '')
        datos_vigencias = request.POST.get('datos_vigencias', '')

        tipo_garantia_id = request.POST.get('tipo_garantia_id', '')
        porcentaje_asegurado = request.POST.get('porcentaje_asegurado', '')
        vigencia_garantia = request.POST.get('vigencia', '')
        garantia_extensiva = request.POST.get('garantia_extensiva', '')
        datos_garantias = request.POST.get('datos_garantias', '')

        recursos_propios = request.POST.get('origen_recurso_id', '')
        contrato.origen_recursos = request.POST.get('origen_recurso', '')

        forma_de_pago = request.POST.get('forma_de_pago_id', None)
        anticipo = request.POST.get('anticipo', None)
        actas_parciales = request.POST.get('actas_parciales', None)
        liquidacion = request.POST.get('liquidacion', None)
        FormasPago.objects.create(contrato=contrato, anticipo=anticipo, actas_parciales=actas_parciales,
                                  liquidacion=liquidacion, forma_pago=forma_de_pago)

        if not contrato.porcentaje_a:
            contrato.porcentaje_a = None
        if not contrato.porcentaje_i:
            contrato.porcentaje_i = None
        if not contrato.porcentaje_u:
             contrato.porcentaje_u = None

        contrato.empresa_id = get_id_empresa_global(request)
        if recursos_propios == 0:
            contrato.recursos_propios = True
            contrato.origen_de_recursos = 'Recursos Propios'
        else:
            contrato.recursos_propios = False

        if municipios:
            for mun in municipios:
                ContratoMunicipio.objects.create(contrato=contrato, municipio_id=mun)

        lista_vigencias = [{"anho": anho_vigencia, "vigencia": valor_vigencia}]
        if datos_vigencias:
            for datos in json.loads(datos_vigencias):
                lista_vigencias.append(datos)
        for vigencia in lista_vigencias:
            ContratoVigencia.objects.create(contrato=contrato, anho=vigencia["anho"], valor=vigencia["vigencia"])

        lista_garantias = [{"tipo_garantia_id": tipo_garantia_id, "porcentaje_asegurado": porcentaje_asegurado,
                            "vigencia_garantia": vigencia_garantia, "garantia_extensiva": garantia_extensiva}]
        if lista_vigencias:
            for datos in json.loads(datos_garantias):
                lista_garantias.append(datos)
        for garantia in lista_garantias:
            ContratoGarantia.objects.create(contrato=contrato, tipo_garantia_id=garantia["tipo_garantia_id"],
                                            porcentaje_asegurado=garantia["porcentaje_asegurado"],
                                            vigencia=garantia["vigencia_garantia"],
                                            extensivas=garantia["garantia_extensiva"])
        if datos_vigencias:
            for datos in json.loads(datos_vigencias):
                lista_vigencias.append(datos)
        for vigencia in lista_vigencias:
            ContratoVigencia.objects.create(contrato=contrato, anho=vigencia["anho"], valor=vigencia["vigencia"])

        for supervisor in supervisores:
            ContratoIterventoriaSupervisor.objects.create(contrato=contrato, tercero_id=supervisor, tipo=SUPERVISOR)

        for interventor in interventores:
            ContratoIterventoriaSupervisor.objects.create(contrato=contrato, tercero_id=interventor, tipo=INTERVENTOR)

        try:
            contrato.full_clean()
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, contrato)
            datos['errores'] = errores.message_dict
            return render(request, 'Proyectos/Contrato/crear-editar.html', datos)

        if Contrato.objects.filter(numero_contrato=contrato.numero_contrato).exists():
            messages.warning(request, 'Ya existe un contrato con número {0}'.format(contrato.numero_contrato))
            return render(request, 'Proyectos/Contrato/crear-editar.html', datos_xa_render(self.OPCION, contrato))

        contrato.save()
        crear_notificacion_por_evento(EventoDesencadenador.CONTRATO, contrato.id, contrato.numero_contrato)
        messages.success(request, 'Se ha agregado el contrato número {0}'.format(contrato.numero_contrato))
        return redirect(reverse('proyectos:contratos'))


class ContratoEditarView(AbstractEvaLoggedView):
    OPCION = 'editar'

    def get(self, request, id):
        contrato = Contrato.objects.get(id=id)
        return render(request, 'Proyectos/Contrato/crear-editar.html', datos_xa_render(self.OPCION, contrato))

    def post(self, request, id):
        update_fields = ['numero_contrato', 'cliente_id', 'anho', 'residente', 'fecha_suscripcion', 'valor',
                         'valor_con_iva', 'valor_sin_iva', 'porcentaje_a', 'porcentaje_i', 'porcentaje_u',
                         'periodicidad_informes', 'plazo_ejecucion', 'tipo_contrato_id', 'empresa', 'proceso_a_cargo_id',
                         'objeto_del_contrato', 'fecha_registro_presupuestal', 'numero_registro_presupuestal',
                         'recursos_propios', 'origen_de_recursos', 'empresa_id']

        contrato = Contrato.from_dictionary(request.POST)
        contrato.empresa_id = get_id_empresa_global(request)
        contrato.id = int(id)
        if not contrato.residente_id:
            contrato.residente_id = None
        if not contrato.proceso_a_cargo_id:
            contrato.proceso_a_cargo_id = None

        municipios = request.POST.getlist('municipio_id[]', [])
        supervisores = request.POST.getlist('supervisor_id[]', [])
        interventores = request.POST.getlist('interventor_id[]', [])
        forma_de_pago = request.POST.get('forma_de_pago_id', None)
        anticipo = request.POST.get('anticipo', None)
        actas_parciales = request.POST.get('actas_parciales', None)
        liquidacion = request.POST.get('liquidacion', None)
        anho_vigencia = request.POST.get('anho_vigencia', '')
        valor_vigencia = request.POST.get('valor_vigencia', '')
        datos_vigencias = request.POST.get('datos_vigencias', '')
        tipo_garantia_id = request.POST.get('tipo_garantia_id', '')
        porcentaje_asegurado = request.POST.get('porcentaje_asegurado', '')
        vigencia_garantia = request.POST.get('vigencia', '')
        garantia_extensiva = request.POST.get('garantia_extensiva', '')
        datos_garantias = request.POST.get('datos_garantias', '')

        FormasPago.objects.filter(contrato=contrato).delete()
        FormasPago.objects.create(contrato=contrato, anticipo=anticipo, actas_parciales=actas_parciales,
                                  liquidacion=liquidacion, forma_pago=forma_de_pago)

        if contrato.recursos_propios == 0:
            contrato.recursos_propios = True
            contrato.origen_de_recursos = 'Recursos Propios'
        else:
            contrato.recursos_propios = False
        if not contrato.porcentaje_a:
            contrato.porcentaje_a = None
        if not contrato.porcentaje_i:
            contrato.porcentaje_i = None
        if not contrato.porcentaje_u:
            contrato.porcentaje_u = None

        lista_vigencias = [{"anho": anho_vigencia, "vigencia": valor_vigencia}]
        if datos_vigencias:
            for datos in json.loads(datos_vigencias):
                lista_vigencias.append(datos)

        ContratoVigencia.objects.filter(contrato=contrato).delete()
        for vigencia in lista_vigencias:
            ContratoVigencia.objects.create(contrato=contrato, anho=vigencia["anho"], valor=vigencia["vigencia"])

        valor_garantia_extensiva = False
        if garantia_extensiva == "on":
            valor_garantia_extensiva = True

        lista_garantias = [{"tipo_garantia": tipo_garantia_id, "porcentaje_asegurado": porcentaje_asegurado,
                            "vigencia_garantia": vigencia_garantia, "garantia_extensiva": valor_garantia_extensiva}]
        if datos_garantias:
            for datos in json.loads(datos_garantias):
                lista_garantias.append(datos)
        ContratoGarantia.objects.filter(contrato=contrato).delete()
        for garantia in lista_garantias:
            ContratoGarantia.objects.create(contrato=contrato, tipo_garantia_id=garantia["tipo_garantia"],
                                            porcentaje_asegurado=garantia["porcentaje_asegurado"],
                                            vigencia=garantia["vigencia_garantia"],
                                            extensiva=garantia["garantia_extensiva"])

        ContratoMunicipio.objects.filter(contrato=contrato, municipio_id__in=municipios).delete()
        for mun in municipios:
            ContratoMunicipio.objects.create(contrato=contrato, municipio_id=mun)

        ContratoIterventoriaSupervisor.objects.filter(contrato=contrato).delete()
        for supervisor in supervisores:
            ContratoIterventoriaSupervisor.objects.create(contrato=contrato, tercero_id=supervisor, tipo=SUPERVISOR)

        for interventor in interventores:
            ContratoIterventoriaSupervisor.objects.create(contrato=contrato, tercero_id=interventor, tipo=INTERVENTOR)

        try:
            contrato.full_clean(validate_unique=False)
        except ValidationError as errores:
            datos = datos_xa_render(self.OPCION, contrato)
            datos['errores'] = errores.message_dict
            return render(request, 'Proyectos/Contrato/crear-editar.html', datos)

        if Contrato.objects.filter(numero_contrato=contrato.numero_contrato).exclude(id=id).exists():
            messages.warning(request, 'Ya existe un contrato con número {0}'.format(contrato.numero_contrato))
            return render(request, 'Proyectos/Contrato/crear-editar.html', datos_xa_render(self.OPCION, contrato))
        contrato_db = Contrato.objects.get(id=id)
        if contrato_db.comparar(contrato):
            messages.success(request, 'No se hicieron cambios en el contrato número {0}'
                             .format(contrato.numero_contrato))
            return redirect(reverse('Proyectos:contratos'))
        else:
            contrato.save(update_fields=update_fields)
            messages.success(request, 'Se ha actualizado el contrato número {0}'.format(contrato.numero_contrato))
        return redirect(reverse('Proyectos:contratos'))


class ContratoEliminarView(AbstractEvaLoggedView):
    def post(self, request, id):
        try:
            contrato = Contrato.objects.get(id=id)
            contrato.delete()
            messages.success(request, 'Se ha eliminado el contrato {0}'.format(contrato.numero_contrato))
            return JsonResponse({"estado": "OK"})

        except IntegrityError:
            return JsonResponse({"estado": "error", "mensaje": "Este contrato no se puede eliminar "
                                                               "porque ya está siendo usado."})


class ContratoDetalleView(AbstractEvaLoggedView):
    def get(self, request, id):
        contrato = Contrato.objects.get(id=id)
        municipios = ContratoMunicipio.objects.filter(contrato=contrato)
        forma_pago = FormasPago.objects.get(contrato=contrato)
        vigencias = ContratoVigencia.objects.filter(contrato=contrato)
        supervisores = ContratoIterventoriaSupervisor.objects.filter(contrato=contrato, tipo=SUPERVISOR)
        interventores = ContratoIterventoriaSupervisor.objects.filter(contrato=contrato, tipo=INTERVENTOR)
        garantias = ContratoGarantia.objects.filter(contrato=contrato)
        return render(request, 'Proyectos/Contrato/_modal_contrato_detalle.html',
                      {'contrato': contrato, 'municipios': municipios, 'forma_pago': forma_pago, 'vigencias': vigencias,
                       'supervisores': supervisores, 'interventores': interventores, 'garantias': garantias,
                       'menu_actual': 'contratos'})


# region Métodos de ayuda
def datos_xa_render(opcion: str, contrato: Contrato = None) -> dict:
    """
    Datos necesarios para la creación de los html de Contratos.
    :param opcion: valor de la acción a realizar 'crea' o 'editar'
    :param contrato: Es opcional si se requiere pre cargar datos.
    :return: Un diccionario con los datos.
    """

    paises = Pais.objects.get_xa_select_activos()
    tipos_garantias = TipoGarantia.objects.get_xa_select_activos()

    formas_de_pago = [
        {'campo_valor': 1, 'campo_texto': 'Anticipo – Actas Parciales - Liquidación'},
        {'campo_valor': 2, 'campo_texto': 'Anticipo – Liquidación'},
        {'campo_valor': 3, 'campo_texto': 'Actas Parciales – Liquidación'}
        ]
    origen_recursos = [{'campo_valor': 1, 'campo_texto': 'Otro Origen'}]
    terceros = Tercero.objects.filter(estado=True)
    supervisores = []
    interventores = []

    for ter in terceros:
        if ter.tipo_tercero_id == TipoTercero.SUPERVISOR:
            supervisores.append({'campo_valor': ter.id, 'campo_texto': ter.nombre})
        elif ter.tipo_tercero_id == TipoTercero.INTERVENTOR:
            interventores.append({'campo_valor': ter.id, 'campo_texto': ter.nombre})

    tipos_contrato = TipoContrato.objects.filter(laboral=False)
    lista_tipos_contratos = []
    for tipo in tipos_contrato:
        lista_tipos_contratos.append({'campo_valor': tipo.id, 'campo_texto': tipo.nombre,
                                      'porcentaje_aiu': tipo.porcentaje_aiu})
    procesos = Proceso.objects.get_xa_select_activos()
    colaboradores = Colaborador.objects.get_xa_select_activos()
    residentes = Colaborador.objects.get_xa_select_usuarios_activos()
    empresas = Empresa.objects.filter(estado=True).values(campo_valor=F('id'), campo_texto=F('nombre')) \
        .order_by('nombre')
    clientes = Tercero.objects.clientes_xa_select()
    rango_anho = [{'campo_valor': anho, 'campo_texto': str(anho)} for anho in range(2000, 2051)]
    datos = {'paises': paises,
             'tipos_garantias': tipos_garantias,
             'formas_de_pago': formas_de_pago,
             'tipos_contrato': lista_tipos_contratos,
             'tipos_contrato_json': json.dumps(lista_tipos_contratos),
             'origen_recursos': origen_recursos,
             'supervisores': supervisores,
             'interventores': interventores,
             'procesos': procesos,
             'colaboradores': colaboradores,
             'residentes': residentes,
             'empresas': empresas,
             'clientes': clientes,
             'rango_anho': rango_anho,
             'opcion': opcion,
             'menu_actual': 'contratos'}
    if contrato:
        contrato.porcentaje_a = decimal_para_input_number(contrato.porcentaje_a)
        contrato.porcentaje_i = decimal_para_input_number(contrato.porcentaje_i)
        contrato.porcentaje_u = decimal_para_input_number(contrato.porcentaje_u)

        datos['contrato'] = contrato
        formas_pago = FormasPago.objects.filter(contrato=contrato)
        if formas_pago:
            datos['formas_pago'] = {'anticipo': decimal_para_input_number(formas_pago.first().anticipo),
                                    'actas_parciales': decimal_para_input_number(formas_pago.first().actas_parciales),
                                    'liquidacion': decimal_para_input_number(formas_pago.first().liquidacion),
                                    'forma_pago': formas_pago.first().forma_pago}

        lista_vigencias = []
        for vigencia in ContratoVigencia.objects.filter(contrato=contrato).order_by('anho'):
            lista_vigencias.append({'valor_anho': vigencia.anho, 'valor_vigencia': vigencia.valor})

        lista_garantias = []
        for garantia in ContratoGarantia.objects.filter(contrato=contrato).order_by('-id'):
            lista_garantias.append({'tipo_garantia': garantia.tipo_garantia_id,
                                    'nombre_tipo_garantia': garantia.tipo_garantia.nombre,
                                    'porcentaje_asegurado': str(garantia.porcentaje_asegurado),
                                    'vigencia_garantia': garantia.vigencia,
                                    'garantia_extensiva': garantia.extensiva})

        datos['valores_vigencias_actuales'] = json.dumps(lista_vigencias)
        datos['valores_garantias_actuales'] = json.dumps(lista_garantias)

        lista_supervisores = []
        for supervisor in ContratoIterventoriaSupervisor.objects.filter(contrato=contrato, tipo=SUPERVISOR):
            lista_supervisores.append(supervisor.tercero_id)
        lista_interventores = []
        for interventor in ContratoIterventoriaSupervisor.objects.filter(contrato=contrato, tipo=INTERVENTOR):
            lista_interventores.append(interventor.tercero_id)

        datos['selecciones_interventores'] = lista_interventores
        datos['selecciones_supervisores'] = lista_supervisores

        contrato_municipio = ContratoMunicipio.objects.filter(contrato=contrato)
        lista_municipios = []
        lista_id_selecciones = []
        if contrato_municipio:
            for con_mun in contrato_municipio:
                lista_id_selecciones.append(con_mun.municipio_id)
                lista_municipios.append({'id': con_mun.municipio_id, 'nombre': con_mun.municipio.nombre})
            datos['selecciones_pdm'] = json.dumps({'id_pais': contrato_municipio.first().municipio.departamento.pais_id,
                                                   'nombre_pais': contrato_municipio.first().municipio.departamento.pais.nombre,
                                                   'id_departamento': contrato_municipio.first().municipio.departamento_id,
                                                   'nombre_departamento': contrato_municipio.first().municipio.departamento.nombre,
                                                   'municipio': lista_municipios})
            datos['lista_id_selecciones'] = lista_id_selecciones
    return datos


def gestionar_contrato(request, origen, id_contrato):
    update_fields = ['numero_contrato', 'cliente_id', 'anho', 'residente', 'fecha_suscripcion', 'valor',
                     'valor_con_iva', 'valor_sin_iva', 'porcentaje_a', 'porcentaje_i', 'porcentaje_u',
                     'periodicidad_informes', 'plazo_ejecucion', 'tipo_contrato_id', 'empresa', 'proceso_a_cargo_id',
                     'objeto_del_contrato', 'fecha_registro_presupuestal', 'numero_registro_presupuestal',
                     'recursos_propios', 'origen_de_recursos', 'empresa_id']

    contrato = Contrato.from_dictionary(request.POST)
    contrato.empresa_id = get_id_empresa_global(request)
    if origen == 'editar':
        contrato.id = int(id_contrato)
        FormasPago.objects.filter(contrato=contrato).delete()
        ContratoMunicipio.objects.filter(contrato=contrato, municipio_id__in=municipios).delete()
        ContratoIterventoriaSupervisor.objects.filter(contrato=contrato).delete()

    if not contrato.residente_id:
        contrato.residente_id = None
    if not contrato.proceso_a_cargo_id:
        contrato.proceso_a_cargo_id = None

    municipios = request.POST.getlist('municipio_id[]', [])
    supervisores = request.POST.getlist('supervisor_id[]', [])
    interventores = request.POST.getlist('interventor_id[]', [])
    forma_de_pago = request.POST.get('forma_de_pago_id', None)
    anticipo = request.POST.get('anticipo', None)
    actas_parciales = request.POST.get('actas_parciales', None)
    liquidacion = request.POST.get('liquidacion', None)
    anho_vigencia = request.POST.get('anho_vigencia', '')
    valor_vigencia = request.POST.get('valor_vigencia', '')
    datos_vigencias = request.POST.get('datos_vigencias', '')
    tipo_garantia_id = request.POST.get('tipo_garantia_id', '')
    porcentaje_asegurado = request.POST.get('porcentaje_asegurado', '')
    vigencia_garantia = request.POST.get('vigencia', '')
    garantia_extensiva = request.POST.get('garantia_extensiva', '')
    datos_garantias = request.POST.get('datos_garantias', '')
    contrato.recursos_propios = request.POST.get('origen_recurso_id', '')
    contrato.origen_recursos = request.POST.get('origen_recurso', '')

    # Inicio del bloque que elimina los registros actuales al editar para sustituirlos por los actualizados.
    if origen == 'editar':
        FormasPago.objects.filter(contrato=contrato).delete()
        ContratoMunicipio.objects.filter(contrato=contrato, municipio_id__in=municipios).delete()
        ContratoIterventoriaSupervisor.objects.filter(contrato=contrato).delete()
    # Fin del Bloque.

    FormasPago.objects.create(contrato=contrato, anticipo=anticipo, actas_parciales=actas_parciales,
                              liquidacion=liquidacion, forma_pago=forma_de_pago)

    if contrato.recursos_propios == 0:
        contrato.recursos_propios = True
        contrato.origen_de_recursos = 'Recursos Propios'
    else:
        contrato.recursos_propios = False

    if not contrato.porcentaje_a:
        contrato.porcentaje_a = None
    if not contrato.porcentaje_i:
        contrato.porcentaje_i = None
    if not contrato.porcentaje_u:
        contrato.porcentaje_u = None

    # Inicio del Bloque captura las vigencias
    lista_vigencias = [{"anho": anho_vigencia, "vigencia": valor_vigencia}]
    if datos_vigencias:
        for datos in json.loads(datos_vigencias):
            lista_vigencias.append(datos)

    ContratoVigencia.objects.filter(contrato=contrato).delete()
    for vigencia in lista_vigencias:
        ContratoVigencia.objects.create(contrato=contrato, anho=vigencia["anho"], valor=vigencia["vigencia"])
    # Fin del Bloque

    # Inicio del bloque que captura las garantías
    valor_garantia_extensiva = False
    if garantia_extensiva == "on":
        valor_garantia_extensiva = True

    lista_garantias = [{"tipo_garantia": tipo_garantia_id, "porcentaje_asegurado": porcentaje_asegurado,
                        "vigencia_garantia": vigencia_garantia, "garantia_extensiva": valor_garantia_extensiva}]
    if datos_garantias:
        for datos in json.loads(datos_garantias):
            lista_garantias.append(datos)
    ContratoGarantia.objects.filter(contrato=contrato).delete()
    for garantia in lista_garantias:
        ContratoGarantia.objects.create(contrato=contrato, tipo_garantia_id=garantia["tipo_garantia"],
                                        porcentaje_asegurado=garantia["porcentaje_asegurado"],
                                        vigencia=garantia["vigencia_garantia"],
                                        extensiva=garantia["garantia_extensiva"])
    # Fin del Bloque

    # Inicio dle bloque que crea las selecciones de municipios, supervisores e interventores.
    for mun in municipios:
        ContratoMunicipio.objects.create(contrato=contrato, municipio_id=mun)
    for supervisor in supervisores:
        ContratoIterventoriaSupervisor.objects.create(contrato=contrato, tercero_id=supervisor, tipo=SUPERVISOR)
    for interventor in interventores:
        ContratoIterventoriaSupervisor.objects.create(contrato=contrato, tercero_id=interventor, tipo=INTERVENTOR)
    # Fin del Bloque.

    return contrato
# endregion
