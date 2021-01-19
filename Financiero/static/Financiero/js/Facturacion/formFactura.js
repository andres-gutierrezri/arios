'use strict';

let tablaItems;
let cargandoBorrador = false;
const inputObservaciones = $('#observaciones_id');
let modificado = true;
let observacionesModificado = false;
class Factura
{
    constructor() {
        this.id= 0;
        this.estado= 0;
        this.cliente= 0;
        this.fechaVencimeinto = new Date();
        this.subtotal= 0.00;
        this.cantidadItems = 0;
        this.numeroFactura = 0;
        this.valorImpuestos = 0.00;
        this.baseImpuestos = 0.00;
        this.porcentajeAdministracion = 0.00;
        this.porcentajeImprevistos = 0.00;
        this.porcentajeUtilidad = 0.00;
        this.amortizacion = 0.00;
        this.idAmortizacion = '';
        this.fechaAmortizacion = new Date();
        this.items = [];
        this.impuestos = [];
        this.total = 0.00;
        this.observaciones = '';
    }

    get totalAdministracion() {
        return(valorXaPorcentaje(this.subtotal, this.porcentajeAdministracion))
    }

    get totalImprevistos() {
        return(valorXaPorcentaje(this.subtotal, this.porcentajeImprevistos))
    }

    get totalUtilidad() {
        return(valorXaPorcentaje(this.subtotal, this.porcentajeUtilidad))
    }

    get isAplicaAIU() {
        return ((this.porcentajeAdministracion != null && this.porcentajeAdministracion !== 0) ||
            (this.porcentajeImprevistos != null && this.porcentajeImprevistos !== 0) ||
            (this.porcentajeUtilidad != null && this.porcentajeUtilidad !== 0));
    }

    agregarItem(tituloItem, descripcionItem, valorUnitario, cantidad, impuesto, unidadMedida) {
        const item = new ItemFactura(tituloItem, descripcionItem, valorUnitario, cantidad, impuesto, this.getPorcentajeImpuesto(impuesto), unidadMedida );
        this.items.push(item);
        this.subtotal += item.valorTotal;
        this.cantidadItems++;
        this.actualizarImpuesto(item, true);
        this.actualizarTotal();
        return(item);
    }

    eliminarItem(posicionItem) {
         const item = this.items.splice(posicionItem, 1)[0];
         this.subtotal -= item.valorTotal;
         this.cantidadItems--;
         this.actualizarImpuesto(item, false);
         this.actualizarTotal();
    }

    actualizarImpuesto(item, incrementa) {
        let impuesto = this.impuestos.find( value => value.id === item.impuesto)

        if(impuesto) {
            if (incrementa) {
                impuesto.base += item.valorTotal;
                impuesto.valor += item.valorImpuesto;
                this.valorImpuestos += item.valorImpuesto;
                this.baseImpuestos += item.valorTotal;
            }
            else {
                impuesto.base -= item.valorTotal;
                impuesto.valor -= item.valorImpuesto;
                this.valorImpuestos -= item.valorImpuesto;
                this.baseImpuestos -= item.valorTotal;

            }

        }
        //this.calcularTotalImpuestos();
    }
    calcularTotalImpuestos()
    {
        let total = 0.00;
        this.impuestos.forEach( impuesto => {
            total += valorXaPorcentaje(impuesto.base, impuesto.porcentaje);
        });

        this.valorImpuestos = total;
    }
    actualizarTotal() {
        this.total = redondear2Decimales(this.subtotal + this.valorImpuestos + this.totalAdministracion +
            this.totalImprevistos + this.totalUtilidad - this.amortizacion);
    }

    setPorcentajesAIU(porcentaje_administracion, porcentaje_imprevistos, porcentaje_utilidad){
        this.porcentajeAdministracion = porcentaje_administracion;
        this.porcentajeImprevistos = porcentaje_imprevistos;
        this.porcentajeUtilidad = porcentaje_utilidad;
        this.actualizarTotal();
    }

    setAmortizacion(amortizacion, id, fecha) {
       this.amortizacion = amortizacion;
       this.idAmortizacion = id;
       this.fechaAmortizacion = fecha;
       this.actualizarTotal();
    }

    static fromJSON(jsonData) {
        let factura = new Factura();
        Object.assign(factura, jsonData);
        return factura;
    }
    getPorcentajeImpuesto(id) {
        let impuesto = this.impuestos.find( value => value.id === id)
        return impuesto ? impuesto.porcentaje : 0;
    }
}
let controls = {
	leftArrow: '<i class="fal fa-angle-left" style="font-size: 1.25rem"></i>',
	rightArrow: '<i class="fal fa-angle-right" style="font-size: 1.25rem"></i>'
};
let factura = new Factura();

function valorXaPorcentaje(valor, porcentaje) {
    return redondear2Decimales((valor * porcentaje) / 100.00);
}

$(document).ready(function () {


    const clienteSelect = $('#cliente_select_id');
    clienteSelect.select2();
    clienteSelect.change(function () {
        cargarDatosCliente(clienteSelect.val());
    });

    // se realiza esto para que el select2 de impuestos se muestre correctamente en el modal de agregar ítem.
    $('#impuesto_select_id').select2({
            dropdownParent: $('#agregar_item_modal')
        }
    );

    inputObservaciones.blur(function (){
        if(inputObservaciones.val() !== factura.observaciones){
            factura.observaciones = inputObservaciones.val();
            habilitarBotones(true, false);
        } else {
            habilitarBotones(observacionesModificado, !observacionesModificado);
        }
    });

    inputObservaciones.focus(function (){
        observacionesModificado = modificado;
        habilitarBotones(true, false);
    });

    configurarTablaDetalle();
    configurarFormularios();
    configurarBotones();
    cargaImpuestosEnFactura();
    cargarBorrador();

    $('.fecha-control ').datepicker({
		todayHighlight: true,
		orientation: "bottom left",
		templates: controls,
		format: 'yyyy-mm-dd',
		autoclose: true
	});

});

function configurarTablaDetalle() {
    tablaItems = $('#dt_detalle_factura').DataTable({
        dom: "<'row mb-3'<'col-sm-12 col-md-6 d-flex align-items-center justify-content-start'f><'col-sm-12 col-md-6 d-flex align-items-center justify-content-end'B>>" +
                        "<'row'<'col-sm-12'tr>>" +
                        "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
        paging: false,
        searching: false,
        ordering: false,
        select: {
            style:'single',
        },
        buttons: [
                    {
                        extend: 'selected',
                        text: '<i class="fal fa-times mr-1"></i> Eliminar',
                        name: 'eliminar',
                        className: 'btn-danger btn-sm mr-1 btn-pills',
                        action: eliminarItemFactura
                    },
                    {
                        extend: 'selected',
                        text: '<i class="fal fa-edit mr-1"></i> Editar',
                        name: 'editar',
                        className: 'btn-primary btn-sm mr-1 btn-pills'
                    },
                    {
                        text: '<i class="fal fa-plus mr-1"></i> Agregar',
                        name: 'agregar',
                        className: 'btn-success btn-sm mr-1 btn-pills',
                        action: function abrirModalAgregarItem() {
                                    $("#agregar_item_modal").modal('show');
                                }
                    }],
        columnDefs: [
                    {
                        "targets": [1],
                        "width": '10%',
                        className: 'text-right'
                    },
                    {
                        "targets": [2],
                        "width": '10%',
                        className: 'text-right'
                    },
                    {
                        "targets": [3],
                        "width": '20%',
                         className: 'text-right'
                    },
                    {
                        "targets": [4],
                        "width": '20%',
                         className: 'text-right'
                    }],
        language: {
            info: '',
            infoEmpty:'',
            emptyTable: 'Para agregar un ítem hacer clic en el botón "+ Agregar"'
         }
    });
}

function configurarFormularios() {
    const form = $("#fitem_factura")[0];
    agregarValidacionForm(form, function (event){
        agregarItemFactura();
        limpiarFormulario(form);
        $('#impuesto_select_id').val(null).trigger('change');
        cerrarModalAgregarItem();
        return true;
    });

    const formAmortizacion = $("#famortizacion_factura")[0];
    agregarValidacionForm(formAmortizacion, function (event) {
        agregarAmortizacionFactura();
        limpiarFormulario(formAmortizacion);
        cerrarModalAgregarAmortizacion();
        return true;
    });

    const formAIU = $("#faiu_factura")[0];
    agregarValidacionForm(formAIU, function (event) {
        agregarAIUFactura();
        limpiarFormulario(formAIU);
        cerrarModalAgregarAIU();
        return true;
    });

}

function configurarBotones() {
    const btnGuardarBorrador = $('#btn_guardar_borrador');
    btnGuardarBorrador.click(function () {
        enviarFactura(0);
    });

    const btnGenerarFactura = $('#btn_generar_factura');
    btnGenerarFactura.click(function () {
        enviarFactura(1);
    });
    
}

function cerrarModalAgregarItem() {
    $("#agregar_item_modal").modal('hide');
    $(".modal-backdrop").remove();
}

function ItemFactura(titulo, descripcion, valorUnitario, cantidad, impuesto, porcentajeImpuesto, unidadMedida) {
    this.titulo = titulo;
    this.descripcion = descripcion;
    this.valorUnitario = valorUnitario;
    this.cantidad = cantidad;
    this.impuesto = impuesto;
    this.valorTotal = valorUnitario * cantidad;
    this.valorImpuesto = valorXaPorcentaje(this.valorTotal, porcentajeImpuesto);
    this.unidadMedida = unidadMedida;
}

function getItemXaTabla(itemFactura) {
    return([
        itemFactura.titulo === '' ? `${itemFactura.descripcion}` : `<b>${itemFactura.titulo}</b><br>${itemFactura.descripcion}`,
        numToDecimalStr(itemFactura.cantidad),
        itemFactura.unidadMedida.descripcion,
        numToDecimalStr(itemFactura.valorUnitario),
        numToDecimalStr(itemFactura.valorTotal)
    ]);
}

function agregarItemFactura() {
    let existe = false;
    const tituloItem = $('#titulo_item_id').val();
    const descripcionItem = $('#descripcion_item_id').val();
    const valorUnitario = Number($('#valor_unitario_id').inputmask('unmaskedvalue'));
    const cantidad = Number($('#cantidad_id').inputmask('unmaskedvalue'));
    const impuesto_seleccionado = $('#impuesto_select_id')[0].selectedOptions[0];
    const impuesto = impuesto_seleccionado.value !== '' ? JSON.parse(impuesto_seleccionado.value) : {id:0, porcentaje:0.00};
    const unidad_seleccionada = $('#unidad_medida_select_id')[0].selectedOptions[0];
    const unidadMedida = unidad_seleccionada.value !== '' ? {id: unidad_seleccionada.value, descripcion: unidad_seleccionada.text} : {id:0, descripcion:''}
    const itemFactura = factura.agregarItem(tituloItem, descripcionItem, valorUnitario, cantidad, impuesto.id, unidadMedida);

    tablaItems.row.add(getItemXaTabla(itemFactura)).node();
    tablaItems.draw(false);
    renderTotalFactura();
}

function renderTotalFactura() {
    const footer = $('#tableItemsFooter');
    const totales = armaTotales();
    let filasTotales = '';
    const subtotal = 0;
    totales.forEach(function (total) {
        filasTotales += getFilaTotales(total.nombre, total.valor);
    });

    footer.html(filasTotales);
    habilitarBotones(true, false);
}

function getFilaTotales(nombre, valor) {
    if(nombre !== 'Subtotal')
        return `<tr><td colspan="4" class="text-right"><b>${nombre}</b></td><td class="text-right">${numToDecimalStr(valor)}</td></tr>`;
    else
        return `<tr><td colspan="4" class="text-right"><div class="btn-group dropup">
                        <button type="button" class="btn btn-warning rounded-circle btn-icon" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                            <i class="fal fa-ellipsis-h-alt"></i>
                        </button>
                        <div class="dropdown-menu p-0">
                            <div class="dropdown-header bg-trans-gradient d-flex flex-row px-4 py-3 rounded-top text-white">
                                <div class="fs-lg text-truncate text-truncate-lg">Agregar</div>
                            </div>
                            <a class="dropdown-item" href="javascript:abrirModalAgregarAmortizacion();">Amortización</a>
                        </div>
                    </div> <b>${nombre}</b></td><td class="text-right">${numToDecimalStr(valor)}
                </td></tr>`
}

function armaTotales() {
    let totales = [];

    totales.push({nombre:'Subtotal', valor: factura.subtotal});

    factura.impuestos.forEach(impuesto => {
        if(impuesto.base > 0)
            totales.push({nombre:impuesto.nombre, valor: impuesto.valor});
            //totales.push({nombre:impuesto.nombre, valor: valorXaPorcentaje(impuesto.base, impuesto.porcentaje)});
    });

    if(factura.isAplicaAIU) {
        totales.push({nombre:`Administración ${factura.porcentajeAdministracion}%`, valor: factura.totalAdministracion});
        totales.push({nombre:`Imprevistos ${factura.porcentajeImprevistos}%`, valor: factura.totalImprevistos});
        totales.push({nombre:`Utilidad ${factura.porcentajeUtilidad}%`, valor: factura.totalUtilidad});
    }

    if(factura.amortizacion > 0) {
        totales.push({nombre: 'Menos amortización', valor: factura.amortizacion});
    }

    totales.push({nombre:'Total', valor: factura.total});
    return(totales);
}

let eliminarItemFactura = function ( e, dt, button, config) {
    const fila = dt.row({ selected: true });
    factura.eliminarItem(fila.index());
    fila.remove().draw(false);
    renderTotalFactura();
};

function abrirModalAgregarAmortizacion() {
    $("#agregar_amortizacion_modal").modal('show');
}

function abrirModalAgregarAIU() {
    $("#agregar_aiu_modal").modal('show');
}

function cerrarModalAgregarAmortizacion() {
    $("#agregar_amortizacion_modal").modal('hide');
    $(".modal-backdrop").remove();
}

function cerrarModalAgregarAIU() {
    $("#agregar_aiu_modal").modal('hide');
    $(".modal-backdrop").remove();
}

function agregarAmortizacionFactura() {

    factura.setAmortizacion(Number($('#valor_amortizacion_id').inputmask('unmaskedvalue')),
        $('#id_amortizacion_id').val(), new Date($('#fecha_amortizacion_id').val()));

    renderTotalFactura();
}

function agregarAIUFactura() {

    factura.setPorcentajesAIU(Number($('#porcentaje_administracion_id').val()), Number($('#porcentaje_imprevistos_id').val()),
        Number($('#porcentaje_utilidad_id').val()));

    renderTotalFactura();
}

function cargaImpuestosEnFactura() {
    let impuestos = [];
    for (let opcion of $('#impuesto_select_id')[0].options) {
        if(opcion.index !== 0) {
            let impuesto = JSON.parse(opcion.value);
            impuesto.nombre = opcion.text;
            impuesto.base = 0;
            impuesto.valor = 0;
            impuestos.push(impuesto);
        }
    }
    factura.impuestos = impuestos;
}

function enviarFactura(estado) {
    factura.estado = estado;

    if(!validarFactura())
        return;
    if(estado === 0)
        EVANotificacion.modal.cargando("Guardando borrador de factura.");
    else
        EVANotificacion.modal.cargando("Generando factura.");

    $.ajax({
            url: "/financiero/facturas/add",
            context: document.body,
            type:'POST',
            data:JSON.stringify(factura),
            contentType: "application/json; charset=utf-8;",
            dataType: "json",
    }).done(function(response) {
        if(response.hasOwnProperty('estado')){
            if (response.estado === 'OK') {
                if (factura.estado === 0) {
                    factura.id = response.datos.factura_id;
                    habilitarBotones(false, true);
                    EVANotificacion.toast.exitoso('Borrador de factura guardado exitosamente.');
                } else {
                    factura.numeroFactura = response.datos.factura_numero;
                    habilitarBotones(false, false);
                    EVANotificacion.toast.exitoso(`Se generó exitosamente la factura # ${factura.numeroFactura}`);
                    window.location = '/financiero/facturas/';
                }
            } else {
                if (response.hasOwnProperty('mensaje'))
                    EVANotificacion.toast.error(response.mensaje);
                else
                    EVANotificacion.toast.error("Error no esperado.");
            }
        }

    }).fail(function () {
        EVANotificacion.toast.error('Falló el guardado del borrador de la factura');
    }).always(function () {
        EVANotificacion.modal.cerrar();
    });
}

function validarFactura() {
    let mensajeError = '';
    if (factura.cantidadItems === 0)
        mensajeError = 'La factura no tiene ítems';
    else if (factura.total <= 0)
        mensajeError = 'El total a pagar debe ser mayor a 0';
    else if (factura.cliente === 0)
        mensajeError = 'No se ha seleccionado un cliente';

    if(mensajeError === '')
        return true;
    else
        EVANotificacion.toast.error(mensajeError);

    return false;
}

function cargarDatosCliente(idCliente) {

    if(idCliente === '') {
        factura.cliente = 0;
        renderDatosCliente({identificacion:'', direccion:'', telefono:'', fax:''});
        return;
    }

    factura.cliente = idCliente;

    $.ajax({
            url: `/administracion/terceros/${idCliente}/json`,
            context: document.body
    }).done(response => {
        if (response.estado === 'OK') {
            renderDatosCliente(response.datos);
            if(cargandoBorrador)
               cargandoBorrador = false;
            else
                habilitarBotones(true, false);
        }
        else
            EVANotificacion.toast.error(response.mensaje);

    }).fail(() => {
         EVANotificacion.toast.error('Error consultando cliente');
    });
}

function renderDatosCliente(datos) {
    $('#cliente_nit_id').val(datos.identificacion);
    $('#cliente_direccion_id').val(datos.direccion);
    $('#cliente_telefono_id').val(datos.telefono);
    $('#cliente_fax_id').val(datos.fax);
    $('#cliente_dv_id').val(datos.digito_verificacion);
}

function habilitarBotones(borrador, generar) {
    $('#btn_guardar_borrador').prop('disabled', !borrador);
    $('#btn_generar_factura').prop('disabled', !generar);
    modificado = borrador;
}

function cargarBorrador() {
    const idFactura = $('#id_factura').val();
    if ((idFactura !== undefined) && (idFactura > 0)) {
        EVANotificacion.modal.cargando('Cargando borrador de factura.');
        $.ajax({
            url: `/financiero/facturas/${idFactura}/json`,
            context: document.body
        }).done(response => {
            if (response.estado === 'OK') {
                try {
                    factura = Factura.fromJSON(response.datos);
                    console.log(factura);
                    renderBorrador();
                    EVANotificacion.toast.exitoso('Borrador cargado exitosamente.');
                } catch {
                     EVANotificacion.toast.error("Error con el borrador recibido.");
                }
            }
            else
                EVANotificacion.toast.error(response.mensaje);

        }).fail(() => {
             EVANotificacion.toast.error('Error cargando borrador de factura.');
        }).always(() => {
            EVANotificacion.modal.cerrar();
        });
    }

}

function renderBorrador() {

    cargandoBorrador = true;
    factura.items.forEach(item =>{
        tablaItems.row.add(getItemXaTabla(item)).node();
    });
    tablaItems.draw(false);
    renderTotalFactura();
    inputObservaciones.val(factura.observaciones);
    const clienteSelect = $('#cliente_select_id');
    clienteSelect.val(factura.cliente).change();
    habilitarBotones(false, true);
}


