'use strict';

let item = [];

$(document).ready(function() {

    let entidadSelect = $("#tipo_entidad_id_select_id");

    entidadSelect.change(function () {
        window.location = '/talento-humano/entidades-cafe/' + entidadSelect.val();
    });

});

$(document).ready(function() {

    let contratoSelect = $("#contrato_id_select_id");

    contratoSelect.change(function () {
        window.location = '/talento-humano/colaboradores/contratos/' + contratoSelect.val();
    });

});
