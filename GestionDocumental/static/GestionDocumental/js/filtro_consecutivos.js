'use strict';

let item = [];

$(document).ready(function() {

    let opcionSelect = $("#filtro_consecutivos_select_id");
    let ruta_filtro_consecutivos = $('#ruta_filtro_consecutivos');

    opcionSelect.change(function () {
        window.location = ruta_filtro_consecutivos.val() + opcionSelect.val() + '/index';
    });

});