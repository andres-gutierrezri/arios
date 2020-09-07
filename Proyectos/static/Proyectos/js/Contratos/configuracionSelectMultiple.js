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
   let valoresSupervisores = $('#valores_supervisores').val();
   idSelectSupervisor.next().find("input").css("min-width", "200px");
   if (valoresSupervisores){
       idSelectSupervisor.val(JSON.parse(valoresSupervisores)).trigger("change");
   }
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

   let valoresInterventores = $('#valores_interventores').val();
   idSelectInterventor.next().find("input").css("min-width", "200px");
   if (valoresInterventores){
       idSelectInterventor.val(JSON.parse(valoresInterventores)).trigger("change");
   }
});

let idSelectMunicipio = $('#municipio_id');

$(document).ready(function () {
   idSelectMunicipio.select2(
        {
            placeholder: "Seleccione un municipio",
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

   let valoresMunicipios = $('#valores_municipios').val();
   idSelectMunicipio.next().find("input").css("min-width", "200px");
   if (valoresMunicipios){
       idSelectMunicipio.val(JSON.parse(valoresMunicipios)).trigger("change");
   }
});