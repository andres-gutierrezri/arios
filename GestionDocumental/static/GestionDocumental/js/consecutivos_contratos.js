'use strict';

let colaboradorSelect = $('#colaborador_mostrar_id');
let terceroSelect = $('#tercero_mostrar_id');
let fechaFinal = $('#fecha_final_mostrar');
let fechaInicioID = $('#fecha_inicio_id');
let fechaFinalID = $('#fecha_final_id');
let tipoTerminacionSelect = $("#tipo_terminacion_select_id");
let colaboradorSelectID = $('#colaborador_select_id');
let terceroSelectID = $('#tercero_select_id');

$(document).ready(function () {
    $('.select2').select2();

    mostrarXTipoContrato();

    tipoTerminacionSelect.change(function () {
        mostrarXTipoContrato()
    });

    $('#tipo_consecutivos_select_id').change(function () {
        window.location = '/gestion-documental/consecutivo-contratos/' + this.value + '/index';
    });
});

function mostrarXTipoContrato() {
    if(tipoTerminacionSelect.val() === '1'){
        mostrarOcultarColaboradorTercero('colaborador');
        fechaFinal.show();
        fechaFinalID.attr("required", true);
    }else if(tipoTerminacionSelect.val() === '2'){
        mostrarOcultarColaboradorTercero('colaborador');
        fechaFinal.hide();
        fechaFinalID.removeAttr('required', true);
    }else if(tipoTerminacionSelect.val() === '3'){
        mostrarOcultarColaboradorTercero('tercero');
        fechaFinal.show();
        fechaFinalID.attr("required", true);
    }else if(tipoTerminacionSelect.val() === '4'){
        mostrarOcultarColaboradorTercero('tercero');
        fechaFinal.hide();
        fechaFinalID.removeAttr('required', true);
    }else{
        mostrarOcultarColaboradorTercero('ninguno');
        fechaFinal.show();
        fechaFinalID.attr("required", true);
    }
}

function mostrarOcultarColaboradorTercero(tipo) {
    if (tipo === 'tercero'){
        terceroSelect.show();
        terceroSelectID.attr("required", true);
        colaboradorSelect.hide();
        colaboradorSelectID.removeAttr('required', true);
    }else{
        colaboradorSelect.show();
        colaboradorSelectID.attr("required", true);
        terceroSelect.hide();
        terceroSelectID.removeAttr('required', true);
    }
}

fechaInicioID.change(function () {
    if (new Date(fechaInicioID.val()) > new Date(fechaFinalID.val())) {
        fechaFinalID.val('');
        EVANotificacion.toast.advertencia('La fecha inicial no puede ser mayor a la fecha final');
    }
});

fechaFinalID.change(function () {
    if (new Date(fechaFinalID.val()) < new Date(fechaInicioID.val())) {
        fechaInicioID.val('');
        EVANotificacion.toast.advertencia('La fecha final no puede ser menor a la fecha inicial');
    }
});

