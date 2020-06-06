'use strict';

let colaboradorSelect = $('#colaborador_mostrar_id');
let terceroSelect = $('#tercero_mostrar_id');
let fechaFinal = $('#fecha_final_mostrar');
let fechaInicioID = $('#fecha_inicio_id');
let fechaFinalID = $('#fecha_final_id');
let tipoTerminacionSelect = $("#tipo_terminacion_select_id");

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
        colaboradorSelect.show();
        terceroSelect.hide();
        fechaFinal.show();
        fechaFinalID.attr("required", true);
    }else if(tipoTerminacionSelect.val() === '2'){
        colaboradorSelect.show();
        terceroSelect.hide();
        fechaFinal.hide();
        fechaFinalID.removeAttr('required', true);
    }else if(tipoTerminacionSelect.val() === '3'){
        colaboradorSelect.hide();
        terceroSelect.show();
        fechaFinal.show();
        fechaFinalID.attr("required", true);
    }else if(tipoTerminacionSelect.val() === '4'){
        colaboradorSelect.hide();
        terceroSelect.show();
        fechaFinal.hide();
        fechaFinalID.removeAttr('required', true);
    }else{
       colaboradorSelect.show();
        terceroSelect.hide();
        fechaFinal.show();
        fechaFinalID.attr("required", true);
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

