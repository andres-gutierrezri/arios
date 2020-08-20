
'use strict';

const controls = {
    leftArrow: '<i class="fal fa-angle-left" style="font-size: 1.25rem"></i>',
    rightArrow: '<i class="fal fa-angle-right" style="font-size: 1.25rem"></i>'
};

let idContratoProceso = $('#contrato_proceso_id');
let idEstados = $('#estados_id');
let idSubtipos = $('#subtipos_id');

$('.select2').select2({
    language: {
        noResults: function() {
          return "No se encontraron coincidencias";
        },
        searching: function() {
          return "Buscando...";
        }
  }
});

$(document).ready(function() {
    // Exportar resultado de la busqueda del consolidado
    iniciarTablaExportar([0, 1, 2, 3, 4]);

    idContratoProceso.select2({
        placeholder: "Seleccione una opción",
        "language": {
            noResults: function () {
                return 'No se encontraron coincidencias';
            },
            searching: function () {
                return 'Buscando…';
            },
        },
    });

    $('.fecha-control ').datepicker({
		todayHighlight: true,
		orientation: "bottom left",
		templates: controls,
		format: 'yyyy-mm-dd',
		autoclose: true
	});
    let valoresContratoProceso = $('#valores_con_pro').val();
    idContratoProceso.next().find("input").css("min-width", "200px");
    if (valoresContratoProceso){
        idContratoProceso.val(JSON.parse(valoresContratoProceso)).trigger("change");
    }

    idEstados.select2({
        placeholder: "Seleccione un opción",
        "language": {
            noResults: function () {
                return 'No se encontraron coincidencias';
            },
            searching: function () {
                return 'Buscando…';
            },
        },
    });
    idEstados.next().find("input").css("min-width", "200px");
    idEstados.val(JSON.parse($('#valores_estados').val())).trigger("change");

    idSubtipos.select2({
        placeholder: "Seleccione un opción",
        "language": {
            noResults: function () {
                return 'No se encontraron coincidencias';
            },
            searching: function () {
                return 'Buscando…';
            },
        },
    });
    let valoresSubtipos = $('#valores_subtipos').val();
    idSubtipos.next().find("input").css("min-width", "200px");
    if (valoresSubtipos){
        idSubtipos.val(JSON.parse(valoresSubtipos)).trigger("change");
    }
});

function seleccionarTodos(elemento) {
    let idElemento = $('#' + elemento + '_id');
    let icono = $('#ic_all_' + elemento);
    let boton = $('#btn_all_' + elemento);
    let texto = $('#txt_all_' + elemento);
    if (icono.hasClass('fa-check')){
        boton.attr('title', 'Quitar Selecciones');
        idElemento.select2('destroy').find('option').prop('selected', 'selected').end().select2();
        icono.removeClass('fa-check');
        icono.addClass('fa-times');
        texto.html('Quitar Selecciones')
    }else{
        boton.attr('title', 'Seleccionar Todos');
        idElemento.select2('destroy').find('option').prop('selected', false).end().select2({placeholder: "Seleccione una opción"});
        icono.removeClass('fa-times');
        icono.addClass('fa-check');
        texto.html('Seleccionar Todos')
    }
}

let fechaHasta = $('#fecha_hasta_id');
let fechaDesde = $('#fecha_desde_id');
let fecha_min_max = JSON.parse($('#fecha_min_max').val());
let fechaMinima = fecha_min_max.fecha_min.split(" ")[0];
let fechaMaxima = fecha_min_max.fecha_max.split(" ")[0];
let borrarFechaDesde = $('#borrarFechaDesde');
let borrarFechaHasta = $('#borrarFechaHasta');

fechaDesde.change(function () {
    if (fechaDesde.val() !== ''){
        borrarFechaDesde.show();
    }else{
        borrarFechaDesde.hide();
    }
    if (fechaHasta.val() !== ''){
        if (new Date(fechaHasta.val()) < new Date(fechaDesde.val())) {
            fechaDesde.val('');
            EVANotificacion.toast.error('La fecha desde no puede ser mayor a la fecha hasta seleccionada.');
        }
    }else{
        validarFechaMaxMin(fechaDesde)
    }
});

fechaHasta.change(function () {
    if (fechaHasta.val() !== ''){
        borrarFechaHasta.show();
    }else{
        borrarFechaHasta.hide();
    }
    if (fechaDesde.val() !== ''){
        if (new Date(fechaDesde.val()) > new Date(fechaHasta.val())) {
            fechaDesde.val('');
            EVANotificacion.toast.error('La fecha hasta no puede ser inferior a la fecha desde seleccionada.');
        }
    }else{
        validarFechaMaxMin(fechaHasta)
    }
});

function validarFechaMaxMin(fecha) {

    if (new Date(fechaMinima) > new Date(fecha.val())){
        EVANotificacion.toast.error('Los movimientos mas antiguos van desde ' + fechaMinima);
        fecha.val('');
    }else if (new Date(fechaMaxima) < new Date(fecha.val())){
        EVANotificacion.toast.error('Los movimientos mas nuevos están hasta ' + fechaMaxima);
        fecha.val('');
    }
}

function borrarFecha(input) {
    if(input === 'fecha_desde'){
        fechaDesde.val('');
        borrarFechaDesde.hide();
    } else if (input === 'fecha_hasta'){
        fechaHasta.val('');
        borrarFechaHasta.hide();
    }
}
