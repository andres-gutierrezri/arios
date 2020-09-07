'use strict';

let idSelectSupervisor = $('#supervisor_id');

$(document).ready(function () {
   idSelectSupervisor.select2(
        {
            placeholder: "Seleccione un supervisor",
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
    idSelectSupervisor.next().find("input").css("min-width","200px");
    idSelectSupervisor.val(JSON.parse($('#multiple').val())).trigger("change");
});

let idSelectInterventor = $('#interventor_id');

$(document).ready(function () {
   idSelectInterventor.select2(
        {
            placeholder: "Seleccione un interventor",
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
    idSelectInterventor.next().find("input").css("min-width","200px");
    idSelectInterventor.val(JSON.parse($('#multiple').val())).trigger("change");
});