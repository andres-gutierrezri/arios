'use strict';

let grupoSelect = $('#grupo_id');

$(document).ready(function () {
   grupoSelect.select2(
        {
            placeholder: "Seleccione un grupo de permisos",
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
    grupoSelect.next().find("input").css("min-width", "200px");
    grupoSelect.val(JSON.parse($('#multiple_grupos').val())).trigger("change");
});