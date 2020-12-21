
'use strict';

let URLDomain = document.location.origin+"/";
let divContenedor = $('#div_contenedor');
let contador = 0;

$(document).ready(function() {
    let contadorServer = $('#contadorServer');
    if (contadorServer.val() !== ''){
        contador = parseInt(contadorServer.val())
        $('#contadorJS').val(contador + 1)
    }
    if ($('#selecciones').val() === '[]'){
        agregarProductoServicio();
    }
});

function cambioTipoProductoServicio(pos){
    let valor = $(`#tipo_producto_servicio_${pos}_select_id`).val();
    if(valor !== '') {
        cargarSubtiposProductosServicios(valor, pos)
        cambioLabelSelects(valor, pos)
    }
}

function cambioSubtipoProductoServicio(pos){
    let valor = $(`#subtipo_producto_servicio_${pos}_select_id`).val();
    if(valor !== '') {
        cargarProductosServicios(valor, pos)
    }
}

function cambioLabelSelects(valor, pos) {
    let labelSubtipoProductoServicio = $(`#subtipo_producto_servicio_${pos}_label_id`);
    let labelProductoServicio = $(`#producto_servicio_${pos}_label_id`);
    if (valor === '1'){
        labelSubtipoProductoServicio.text('Subtipos de Productos')
        labelProductoServicio.text('Productos')
    }else if (valor === '2'){
        labelSubtipoProductoServicio.text('Subtipos de Servicios')
        labelProductoServicio.text('Servicios')
    }
}

function cargarSubtiposProductosServicios(idProductoServicio, pos) {
    let subtipoProductoServicio = $(`#subtipo_producto_servicio_${pos}_select_id`);
    let productoServicio = $(`#producto_servicio_${pos}`);
    $.ajax({
        url: URLDomain + "administracion/producto-servicio/" + idProductoServicio + "/subtipos/json",
        type: 'GET',
        context: document.body,
        success: function (data) {
            if (data.length > 0) {
                subtipoProductoServicio.empty();
                productoServicio.empty();
                subtipoProductoServicio.append('<option value="">Seleccione una opción</option>');
                for (let i = 0; i < data.length; i++) {
                    subtipoProductoServicio.append('<option value="' + data[i].id + '">' + data[i].nombre + '</option>');
                }
            } else {
                subtipoProductoServicio.empty();
                subtipoProductoServicio.append('<option value="">Seleccione una opción</option>');
            }
        },
        failure: function (errMsg) {
            alert('Se presentó un error al realizar la consulta');

        }
    });
}

function cargarProductosServicios(idSubtipoProductoServicio, pos) {
    let productoServicio = $(`#producto_servicio_${pos}`);
    $.ajax({
        url: URLDomain + "administracion/subtipo-producto-servicio/" + idSubtipoProductoServicio + "/producto-servicio/json",
        type: 'GET',
        context: document.body,
        success: function (data) {
            if (data.length > 0) {
                productoServicio.empty();
                for (let i = 0; i < data.length; i++) {
                    productoServicio.append('<option value="' + data[i].id + '">' + data[i].nombre + '</option>');
                }
            } else {
                productoServicio.empty();
            }
        },
        failure: function (errMsg) {
            alert('Se presentó un error al realizar la consulta');
        }
    });
}

function generarSelect(nombre, texto_label, multiple, onchange, opciones){
    let listaOpciones = []
    let id = `${nombre}_${contador}_select_id`
    if (multiple){
        multiple = 'multiple="multiple"'
        id = `${nombre}_${contador}`
    }else{
        multiple = ''
        listaOpciones.push('<option value="">Seleccione una opción</option>')
    }
    if (opciones){
        opciones.forEach(function (obj){
            listaOpciones.push(`<option value="${obj.id}">${obj.nombre}</option>`)
        })
    }
    let x = listaOpciones;
    return `<label for="${id}" id="${nombre}_${contador}_label_id">${texto_label}</label>
        <select class="select2 form-control" required="required" ${multiple} id="${id}" name="${nombre}_${contador}" ${onchange}>
            ${listaOpciones}
        </select>
        <div class="invalid-tooltip">Por favor seleccione una opción</div>`
}

function cargarSelects() {
    let opciones = [{'id': 1, 'nombre': 'Producto'}, {'id': 2, 'nombre': 'Servicio'}]
    let elementos = `<div class="form-row inputs-producto-servicio" id="inputs_${contador}">
                        <div class="form-group col-3">
                              ${generarSelect('tipo_producto_servicio', 'Producto/Servicio',
                                              false, `onchange="cambioTipoProductoServicio(${contador})"`,  opciones)}
                          </div>
                          <div class="form-group col-3">
                              ${generarSelect('subtipo_producto_servicio', 'Subtipo de Producto', 
                                             false, `onchange="cambioSubtipoProductoServicio(${contador})"`)}
                          </div>
                          <div class="form-group col-5">
                              ${generarSelect('producto_servicio', 'Producto', true, '')}
                          </div>
                          <div class="form-group col-1" style="padding-top:30px">
                            <a class="far fa-2x fa-trash-alt color-danger-900" id="eliminar_${contador}" href="javascript:eliminarProductoServicio(${contador});" data-template='<div class="tooltip" role="tooltip"><div class="tooltip-inner bg-primary-500"></div></div>' data-toggle="tooltip" title="" data-original-title="Eliminar"></a>
                          </div></div>`
    divContenedor.append(elementos)
    contador += 1;
}

function agregarProductoServicio() {
    cargarSelects();
    activarSelect2();
    $('#contadorJS').val(contador + 1)
}

function eliminarProductoServicio(pos) {
    if (($('.inputs-producto-servicio').toArray().length) > 1){
        $(`#inputs_${pos}`).remove();
    }else{
         EVANotificacion.toast.error('No se puede realizar esta acción');
    }
}