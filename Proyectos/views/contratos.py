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
from Administracion.models import Tercero, Empresa, TipoContrato, Proceso, Pais, TipoTercero, Municipio
from TalentoHumano.models import Colaborador


SUPERVISOR = 0
INTERVENTOR = 1
PROPIOS = 0
OTROS = 1


class ContratoView(AbstractEvaLoggedView):
    def get(self, request):
        contratos = Contrato.objects.filter(empresa_id=get_id_empresa_global(request))
        fecha = datetime.now()
        return render(request, 'Proyectos/Contrato/index.html', {'contratos': contratos, 'fecha': fecha,
                                                                 'menu_actual': 'contratos'})


class ContratoCrearView(AbstractEvaLoggedView):
    OPCION = 'crear'

    def get(self, request):
        return render(request, 'Proyectos/Contrato/crear-editar.html', datos_xa_render(request, self.OPCION))

    def post(self, request):
        contrato = Contrato.from_dictionary(request.POST)
        contrato = validar_datos_contrato(request, contrato)

        try:
            contrato.full_clean()
        except ValidationError as errores:
            datos = datos_xa_render(request, self.OPCION, contrato)
            datos['errores'] = errores.message_dict
            return render(request, 'Proyectos/Contrato/crear-editar.html', datos)

        if Contrato.objects.filter(numero_contrato=contrato.numero_contrato).exists():
            messages.warning(request, 'Ya existe un contrato con número {0}'.format(contrato.numero_contrato))
            return render(request, 'Proyectos/Contrato/crear-editar.html',
                          datos_xa_render(request, self.OPCION, contrato))

        contrato.save()
        gestionar_contrato(request, self.OPCION, contrato)
        crear_notificacion_por_evento(EventoDesencadenador.CONTRATO, contrato.id, contrato.numero_contrato)
        messages.success(request, 'Se ha agregado el contrato número {0}'.format(contrato.numero_contrato))
        return redirect(reverse('proyectos:contratos'))


class ContratoEditarView(AbstractEvaLoggedView):
    OPCION = 'editar'

    def get(self, request, id):
        contrato = Contrato.objects.get(id=id)
        return render(request, 'Proyectos/Contrato/crear-editar.html', datos_xa_render(request, self.OPCION, contrato))

    def post(self, request, id):
        update_fields = ['numero_contrato', 'cliente_id', 'anho', 'residente', 'fecha_suscripcion', 'valor',
                         'valor_con_iva', 'valor_sin_iva', 'porcentaje_a', 'porcentaje_i', 'porcentaje_u',
                         'periodicidad_informes', 'plazo_ejecucion', 'tipo_contrato_id', 'empresa',
                         'objeto_del_contrato', 'fecha_registro_presupuestal', 'numero_registro_presupuestal',
                         'recursos_propios', 'origen_de_recursos', 'empresa_id', 'proceso_a_cargo_id']

        contrato = Contrato.from_dictionary(request.POST)
        contrato.id = id
        contrato = validar_datos_contrato(request, contrato)

        try:
            contrato.full_clean(validate_unique=False)
        except ValidationError as errores:
            datos = datos_xa_render(request, self.OPCION, contrato)
            datos['errores'] = errores.message_dict
            return render(request, 'Proyectos/Contrato/crear-editar.html', datos)

        if Contrato.objects.filter(numero_contrato=contrato.numero_contrato).exclude(id=id).exists():
            messages.warning(request, 'Ya existe un contrato con número {0}'.format(contrato.numero_contrato))
            return render(request, 'Proyectos/Contrato/crear-editar.html',
                          datos_xa_render(request, self.OPCION, contrato))

        contrato.save(update_fields=update_fields)
        gestionar_contrato(request, self.OPCION, contrato)
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
        forma_pago = FormasPago.objects.filter(contrato=contrato)
        if forma_pago:
            forma_pago = forma_pago.first()
        vigencias = ContratoVigencia.objects.filter(contrato=contrato).order_by('anho')
        supervisores = ContratoIterventoriaSupervisor.objects.filter(contrato=contrato, tipo=SUPERVISOR)
        interventores = ContratoIterventoriaSupervisor.objects.filter(contrato=contrato, tipo=INTERVENTOR)
        garantias = ContratoGarantia.objects.filter(contrato=contrato)
        return render(request, 'Proyectos/Contrato/_modal_contrato_detalle.html',
                      {'contrato': contrato, 'municipios': municipios, 'forma_pago': forma_pago, 'vigencias': vigencias,
                       'supervisores': supervisores, 'interventores': interventores, 'garantias': garantias,
                       'menu_actual': 'contratos'})


# region Métodos de ayuda
def datos_xa_render(request, opcion: str, contrato: Contrato = None) -> dict:
    """
    Datos necesarios para la creación de los html de Contratos.
    :param opcion: valor de la acción a realizar 'crea' o 'editar'
    :param contrato: Es opcional si se requiere pre cargar datos.
    :return: Un diccionario con los datos.
    """

    paises = Pais.objects.get_xa_select_activos()
    tipos_garantias = TipoGarantia.objects.get_xa_select_activos()
    todos_tipos_garantias = TipoGarantia.objects.all()
    tipos_garantias_smmlv = []
    for td in todos_tipos_garantias:
        tipos_garantias_smmlv.append({'id': td.id, 'aplica_valor_smmlv': td.aplica_valor_smmlv})

    formas_de_pago = [
        {'campo_valor': 1, 'campo_texto': 'Anticipo – Actas Parciales - Liquidación'},
        {'campo_valor': 2, 'campo_texto': 'Anticipo – Liquidación'},
        {'campo_valor': 3, 'campo_texto': 'Actas Parciales – Liquidación'}
        ]
    porcentaje_valor = [{'valor': 0, 'texto': 'Porcentaje'},
                        {'valor': 1, 'texto': 'Valor'}]
    origen_recursos = [{'campo_valor': 1, 'campo_texto': 'Otro Origen'}]
    supervisor_interventor = [{'campo_valor': 1, 'campo_texto': 'Interventor'}]
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
             'tipos_garantias_smmlv': json.dumps(tipos_garantias_smmlv),
             'formas_de_pago': formas_de_pago,
             'porcentaje_valor': porcentaje_valor,
             'supervisor_interventor': supervisor_interventor,
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

        datos_formulario = obtener_datos_contrato(request)

        if contrato.recursos_propios:
            datos['select_origen_recursos'] = PROPIOS
            datos['origen_de_recursos'] = ''
        else:
            datos['select_origen_recursos'] = OTROS
            datos['origen_de_recursos'] = contrato.origen_de_recursos

        datos['contrato'] = contrato
        datos['valor_contrato'] = decimal_para_input_number(contrato.valor)
        datos['valor_contrato_con_iva'] = decimal_para_input_number(contrato.valor_con_iva)
        datos['valor_contrato_sin_iva'] = decimal_para_input_number(contrato.valor_sin_iva)

        formas_pago = FormasPago.objects.filter(contrato=contrato)
        aplica_porcentaje = 1
        if formas_pago:
            if formas_pago.first().aplica_porcentaje:
                aplica_porcentaje = 0
            datos['formas_pago'] = {'anticipo': decimal_para_input_number(formas_pago.first().anticipo),
                                    'actas_parciales': decimal_para_input_number(formas_pago.first().actas_parciales),
                                    'liquidacion': decimal_para_input_number(formas_pago.first().liquidacion),
                                    'forma_pago': formas_pago.first().forma_pago,
                                    'aplica_porcentaje': aplica_porcentaje}
        else:
            if datos_formulario['forma_de_pago']:
                datos['formas_pago'] = {'anticipo': datos_formulario['anticipo'],
                                        'actas_parciales': datos_formulario['actas_parciales'],
                                        'liquidacion': datos_formulario['liquidacion'],
                                        'forma_pago': int(datos_formulario['forma_de_pago']),
                                        'aplica_porcentaje': aplica_porcentaje}

        lista_vigencias = []
        for vigencia in ContratoVigencia.objects.filter(contrato=contrato).order_by('anho'):
            lista_vigencias.append({'valor_anho': vigencia.anho,
                                    'valor_vigencia': decimal_para_input_number(vigencia.valor)})

        lista_garantias = []
        for garantia in ContratoGarantia.objects.filter(contrato=contrato).order_by('-id'):
            lista_garantias.append({'tipo_garantia': garantia.tipo_garantia_id,
                                    'nombre_tipo_garantia': garantia.tipo_garantia.nombre,
                                    'porcentaje_asegurado': str(garantia.porcentaje_asegurado),
                                    'vigencia_garantia': garantia.vigencia,
                                    'garantia_extensiva': garantia.extensiva,
                                    'aplica_valor_smmlv': garantia.tipo_garantia.aplica_valor_smmlv})

        datos['valores_vigencias_actuales'] = json.dumps(lista_vigencias)
        datos['valores_garantias_actuales'] = json.dumps(lista_garantias)

        if not lista_garantias and not lista_vigencias:
            valores_vigencias = []
            valores_garantias = []
            if datos_formulario['datos_vigencias']:
                valores_vigencias.append(json.loads(datos_formulario['datos_vigencias'])[0])
                valores_vigencias.append({"valor_anho": datos_formulario['anho_vigencia'],
                                          "valor_vigencia": decimal_para_input_number(datos_formulario['valor_vigencia'])})

            valor_garantia_extensiva = False
            if datos_formulario['garantia_extensiva'] == "on":
                valor_garantia_extensiva = True
            if datos_formulario['datos_garantias']:
                valores_garantias.append(json.loads(datos_formulario['datos_garantias'])[0])
                valores_garantias.append({"tipo_garantia": int(datos_formulario['tipo_garantia_id']),
                                          "porcentaje_asegurado": datos_formulario['porcentaje_asegurado'],
                                          "vigencia_garantia": datos_formulario['vigencia_garantia'],
                                          "garantia_extensiva": valor_garantia_extensiva,
                                          "nombre_tipo_garantia": TipoGarantia.objects
                                         .get(id=datos_formulario['tipo_garantia_id']).nombre})

            datos['valores_vigencias_actuales'] = json.dumps(valores_vigencias)
            datos['valores_garantias_actuales'] = json.dumps(valores_garantias)

        lista_supervisores = []
        for supervisor in ContratoIterventoriaSupervisor.objects.filter(contrato=contrato, tipo=SUPERVISOR):
            lista_supervisores.append(supervisor.tercero_id)

        if not lista_supervisores:
            for supervisor in datos_formulario['supervisores']:
                lista_supervisores.append(int(supervisor))

        lista_interventores = []
        for interventor in ContratoIterventoriaSupervisor.objects.filter(contrato=contrato, tipo=INTERVENTOR):
            lista_interventores.append(interventor.tercero_id)

        if not lista_interventores:
            for interventor in datos_formulario['interventores']:
                lista_interventores.append(int(interventor))

        if lista_supervisores:
            supervisor_interventor = SUPERVISOR
        else:
            supervisor_interventor = INTERVENTOR
        datos['seleccion_supervisor_interventor'] = supervisor_interventor
        datos['selecciones_interventores'] = lista_interventores
        datos['selecciones_supervisores'] = lista_supervisores

        contrato_municipio = ContratoMunicipio.objects.filter(contrato=contrato)
        lista_municipios = []
        lista_id_selecciones = []
        if contrato_municipio:
            for con_mun in contrato_municipio:
                lista_id_selecciones.append(con_mun.municipio_id)
                lista_municipios.append({'id': con_mun.municipio_id, 'nombre': con_mun.municipio.nombre})
            datos['selecciones_pdm'] = \
                json.dumps({'id_pais': contrato_municipio.first().municipio.departamento.pais_id,
                            'nombre_pais': contrato_municipio.first().municipio.departamento.pais.nombre,
                            'id_departamento': contrato_municipio.first().municipio.departamento_id,
                            'nombre_departamento': contrato_municipio.first().municipio.departamento.nombre,
                            'municipio': lista_municipios})
            datos['lista_id_selecciones'] = lista_id_selecciones
        else:
            municipios_formulario = Municipio.objects.filter(id__in=datos_formulario['municipios'])
            for mun in municipios_formulario:
                lista_id_selecciones.append(mun.id)
                lista_municipios.append({'id': mun.id, 'nombre': mun.nombre})
            datos['selecciones_pdm'] = json.dumps(
                {'id_pais': municipios_formulario.first().departamento.pais_id,
                 'nombre_pais': municipios_formulario.first().departamento.pais.nombre,
                 'id_departamento': municipios_formulario.first().departamento_id,
                 'nombre_departamento': municipios_formulario.first().departamento.nombre,
                 'municipio': lista_municipios})
            datos['lista_id_selecciones'] = lista_id_selecciones
    else:
        datos['formas_pago'] = {'aplica_porcentaje': 0}
    return datos


def validar_datos_contrato(request, contrato):
    contrato.empresa_id = get_id_empresa_global(request)
    if not contrato.residente_id:
        contrato.residente_id = None
    if not contrato.proceso_a_cargo_id:
        contrato.proceso_a_cargo_id = None

    if contrato.recursos_propios == '0':
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
    return contrato


def obtener_datos_contrato(request):
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
    aplica_porcentaje = request.POST.get('porcentaje_valor', '')
    supervisor_interventor = request.POST.get('supervisor_interventor_id', '')

    if not anticipo:
        anticipo = 0
    if not actas_parciales:
        actas_parciales = 0
    if not liquidacion:
        liquidacion = 0

    return {'municipios': municipios, 'supervisores': supervisores, 'interventores': interventores,
            'forma_de_pago': forma_de_pago, 'anticipo': anticipo, 'actas_parciales': actas_parciales,
            'liquidacion': liquidacion, 'anho_vigencia': anho_vigencia, 'valor_vigencia': valor_vigencia,
            'datos_vigencias': datos_vigencias, 'tipo_garantia_id': tipo_garantia_id,
            'porcentaje_asegurado': porcentaje_asegurado, 'vigencia_garantia': vigencia_garantia,
            'garantia_extensiva': garantia_extensiva, 'datos_garantias': datos_garantias,
            'aplica_porcentaje': aplica_porcentaje, 'supervisor_interventor': supervisor_interventor}


def gestionar_contrato(request, origen, contrato):
    datos = obtener_datos_contrato(request)
    crear_actualizar_formas_de_pago(contrato, datos['anticipo'], datos['actas_parciales'], datos['liquidacion'],
                                    datos['forma_de_pago'], datos['aplica_porcentaje'], origen)
    crear_actualizar_vigencias(datos['anho_vigencia'], datos['valor_vigencia'], datos['datos_vigencias'],
                               contrato, origen)
    crear_actualizar_garantias(datos['garantia_extensiva'], datos['tipo_garantia_id'], datos['porcentaje_asegurado'],
                               datos['vigencia_garantia'], datos['datos_garantias'], contrato, origen)
    crear_actualizar_municipios(datos['municipios'], contrato, origen)
    crear_actualizar_supervisores_interventores(datos['supervisores'], datos['interventores'], contrato,
                                                datos['supervisor_interventor'], origen)


def crear_actualizar_formas_de_pago(contrato, anticipo, actas_parciales, liquidacion, forma_de_pago, aplica_porcentaje,
                                    origen):
    if aplica_porcentaje == '1':
        aplica_porcentaje = False
    else:
        aplica_porcentaje = True
    if origen == 'editar':
        FormasPago.objects.filter(contrato=contrato).delete()
    FormasPago.objects.create(contrato=contrato, anticipo=anticipo, actas_parciales=actas_parciales,
                              liquidacion=liquidacion, forma_pago=forma_de_pago, aplica_porcentaje=aplica_porcentaje)


def crear_actualizar_vigencias(anho_vigencia, valor_vigencia, datos_vigencias, contrato, origen):
    if origen == 'editar':
        ContratoVigencia.objects.filter(contrato=contrato).delete()
    lista_vigencias = [{"valor_anho": anho_vigencia, "valor_vigencia": valor_vigencia}]
    if datos_vigencias:
        for datos in json.loads(datos_vigencias):
            lista_vigencias.append(datos)

    for vigencia in lista_vigencias:
        ContratoVigencia.objects.create(contrato=contrato, anho=vigencia["valor_anho"], valor=vigencia["valor_vigencia"])


def crear_actualizar_garantias(garantia_extensiva, tipo_garantia_id, porcentaje_asegurado, vigencia_garantia,
                               datos_garantias, contrato, origen):
    if origen == 'editar':
        ContratoGarantia.objects.filter(contrato=contrato).delete()
    valor_garantia_extensiva = False
    if garantia_extensiva == "on":
        valor_garantia_extensiva = True

    lista_garantias = [{"tipo_garantia": tipo_garantia_id, "porcentaje_asegurado": porcentaje_asegurado,
                        "vigencia_garantia": vigencia_garantia, "garantia_extensiva": valor_garantia_extensiva}]
    if datos_garantias:
        for datos in json.loads(datos_garantias):
            lista_garantias.append(datos)

    for garantia in lista_garantias:
        ContratoGarantia.objects.create(contrato=contrato, tipo_garantia_id=garantia["tipo_garantia"],
                                        porcentaje_asegurado=garantia["porcentaje_asegurado"],
                                        vigencia=garantia["vigencia_garantia"],
                                        extensiva=garantia["garantia_extensiva"])


def crear_actualizar_municipios(municipios, contrato, origen):
    if origen == 'editar':
        ContratoMunicipio.objects.filter(contrato=contrato, municipio_id__in=municipios).delete()
    for mun in municipios:
        ContratoMunicipio.objects.create(contrato=contrato, municipio_id=mun)


def crear_actualizar_supervisores_interventores(supervisores, interventores, contrato, supervisor_interventor, origen):
    if origen == 'editar':
        ContratoIterventoriaSupervisor.objects.filter(contrato=contrato).delete()
    if int(supervisor_interventor) == SUPERVISOR:
        for supervisor in supervisores:
            ContratoIterventoriaSupervisor.objects.create(contrato=contrato, tercero_id=supervisor, tipo=SUPERVISOR)
    else:
        for interventor in interventores:
            ContratoIterventoriaSupervisor.objects.create(contrato=contrato, tercero_id=interventor, tipo=INTERVENTOR)

# endregion
