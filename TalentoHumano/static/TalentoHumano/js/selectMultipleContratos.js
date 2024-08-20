'use strict';

let idContrato = $('#contrato_id');

$(document).ready(function () {
   idContrato.select2(
        {
            placeholder: "Seleccione un contrato",
            "language": {
                noResults: function () {
                    return 'No se encontraron coincidencias';
                },
                searching: function () {
                    return 'Buscando…';
                },
                removeAllItems: function () {
                    return 'Quitar todas los items';
                }
            },
        });
    idContrato.next().find("input").css("min-width","200px");
    idContrato.val(JSON.parse($('#multiple').val())).trigger("change");
});