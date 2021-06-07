'use strict';
let extraTiposContrato = $('#extra_tipos_contrato');
let fechaInicioID = $('#fecha_inicio_id');
let fechaFinalID = $('#fecha_final_id');
let colaboradorSelect = $('#colaborador_mostrar_id');
let terceroSelect = $('#tercero_mostrar_id');
let colaboradorSelectID = $('#colaborador_select_id');
let terceroSelectID = $('#tercero_select_id');

let fechaFinal = $('#fecha_final_mostrar');

$(document).ready(function () {
    $('.select2').select2();
    $('#tipo_consecutivos_select_id').change(function () {
        window.location = '/gestion-documental/consecutivo-contratos/' + this.value + '/index';
    });
});
