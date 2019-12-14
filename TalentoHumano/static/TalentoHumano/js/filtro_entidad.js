'use strict';

let item = [];

$(document).ready(function() {

    let entidadSelect = $("#tipo_entidad_id_select_id");

    entidadSelect.change(function () {
        window.location = '/talento-humano/entidades-index/' + entidadSelect.val();
    });

});
