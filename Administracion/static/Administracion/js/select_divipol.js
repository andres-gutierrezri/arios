var URLDomain = document.location.origin+"/";

var departamento = $("#departamento_select");
var municipio = $("#municipio_select");
var centro_poblado = $("#centro_poblado_select");

var selector = $("#medidor_select");

$(document).ready(function() {

    departamento.change(function () {
        $.ajax({
            url: URLDomain + "administracion/departamentos/" + this.value + "/municipios/json",
            type: 'GET',
            context: document.body,
            success: function (data) {
                data = JSON.parse(data);
                if (data.length > 0) {
                    municipio.empty();
                    municipio.append('<option value="">Seleccione un Municipio</option>');
                    for (var i = 0; i < data.length; i++) {
                        municipio.append('<option value="' + data[i].id + '">' + data[i].nombre + '</option>');
                    }
                }else {
                    municipio.empty();
                    municipio.append('<option value="">Seleccione un Municipio</option>');
                }
            },
            failure: function (errMsg) {
                alert('Se presentó un error al realizar la consulta');

            }
        });
    });
});

$(document).ready(function() {

    municipio.change(function () {
        $.ajax({
            url: URLDomain + "administracion/municipios/" + this.value + "/centros-poblados/json",
            type: 'GET',
            context: document.body,
            success: function (data) {
                data = JSON.parse(data);
                if (data.length > 0) {
                    centro_poblado.empty();
                    centro_poblado.append('<option value="">Seleccione Centro Poblado</option>');
                    for (var i = 0; i < data.length; i++) {
                        centro_poblado.append('<option value="' + data[i].id + '">' + data[i].nombre + '</option>');
                    }
                }else {
                    centro_poblado.empty();
                    centro_poblado.append('<option value="">Seleccione Centro Poblado</option>');
                }

            },
            failure: function (errMsg) {
                alert('Se presentó un error al realizar la consulta');

            }
        });
    });
});
