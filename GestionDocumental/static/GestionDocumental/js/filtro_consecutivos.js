'use strict';

let item = [];

$(document).ready(function() {

    let opcionSelect = $("#filtro_consecutivos_select_id");

    opcionSelect.change(function () {
        window.location = '/gestion-documental/consecutivo-documento/' + opcionSelect.val() + '/index';
    });

});