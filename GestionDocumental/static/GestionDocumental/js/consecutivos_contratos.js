'use strict';
let extra_tipos_contrato = $('#extra_tipos_contrato');
let fechaInicioID = $('#fecha_inicio_id');
let fechaFinalID = $('#fecha_final_id');
let colaboradorSelect = $('#colaborador_mostrar_id');
let terceroSelect = $('#tercero_mostrar_id');
let colaboradorSelectID = $('#colaborador_select_id');
let terceroSelectID = $('#tercero_select_id');

let fechaFinal = $('#fecha_final_mostrar');

$(document).ready(function () {
    $('.select2').select2();
    $('#tipo_contrato_select_id').change(function () {
        let actual = this.value;
        $.each(jQuery.parseJSON(extra_tipos_contrato.val()), function(key, value) {
            if(actual == value.id){
              if (value.laboral){
                  mostrarOcultarColaboradorTercero("laboral")
              }else{
                  mostrarOcultarColaboradorTercero("no_laboral")
              }
              if(value.fecha_fin){
                  fechaFinal.show();
                  fechaFinalID.attr("required", true);
              }else{
                  fechaFinal.hide();
                  fechaFinalID.removeAttr("required", true);
              }
            }
        });
        if (actual === ""){
             fechaFinal.show();
             fechaFinalID.attr("required", true);
             mostrarOcultarColaboradorTercero("ninguno")
        }
    });

    $('#tipo_consecutivos_select_id').change(function () {
        window.location = '/gestion-documental/consecutivo-contratos/' + this.value + '/index';
    });
});

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

function mostrarOcultarColaboradorTercero(tipo) {
    if (tipo === 'no_laboral'){
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

