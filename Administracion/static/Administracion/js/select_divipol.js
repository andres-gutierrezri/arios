'use strict';

let DivipolURLDomain = document.location.origin+"/";

let departamento = $("#departamento_id_select_id");
let municipio = $("#municipio_id_select_id");
let centro_poblado = $("#centro_poblado_id_select_id");

let selector = $("#medidor_select");

$(document).ready(function() {

    departamento.change(function () {
        $.ajax({
            url: DivipolURLDomain + "administracion/departamentos/" + this.value + "/municipios/json",
            type: 'GET',
            context: document.body,
            success: function (data) {
                if (data.length > 0) {
                    municipio.empty();
                    municipio.append('<option value="">Seleccione un municipio</option>');
                    for (var i = 0; i < data.length; i++) {
                        municipio.append('<option value="' + data[i].id + '">' + data[i].nombre + '</option>');
                    }
                }else {
                    municipio.empty();
                    municipio.append('<option value="">Seleccione un municipio</option>');
                }
            },
            failure: function (errMsg) {
                alert('Se presentó un error al realizar la consulta');

            }
        });
    });
    municipio.change(function () {
        $.ajax({
            url: DivipolURLDomain + "administracion/municipios/" + this.value + "/centros-poblados/json",
            type: 'GET',
            context: document.body,
            success: function (data) {
                if (data.length > 0) {
                    centro_poblado.empty();
                    centro_poblado.append('<option value="">Seleccione un centro poblado</option>');
                    for (var i = 0; i < data.length; i++) {
                        centro_poblado.append('<option value="' + data[i].id + '">' + data[i].nombre + '</option>');
                    }
                }else {
                    centro_poblado.empty();
                    centro_poblado.append('<option value="">Seleccione centro poblado</option>');
                }
            },
            failure: function (errMsg) {
                alert('Se presentó un error al realizar la consulta');

            }
        });
    });
});

