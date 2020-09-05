
'use strict';
let URLDomain = document.location.origin+"/";
let pais = $("#pais_id_select_id");
let departamento = $("#departamento_id_select_id");
let municipio = $("#municipio_id");

$(document).ready(function() {
    pais.change(function () {
        if(this.value) {
            $.ajax({
                url: URLDomain + "administracion/paises/" + this.value + "/departamentos/json",
                type: 'GET',
                context: document.body,
                success: function (data) {
                    if (data.length > 0) {
                        departamento.empty();
                        municipio.empty();
                        departamento.append('<option value="">Seleccione un departamento</option>');
                        for (let i = 0; i < data.length; i++) {
                            departamento.append('<option value="' + data[i].id + '">' + data[i].nombre + '</option>');
                        }
                    } else {
                        departamento.empty();
                        departamento.append('<option value="">Seleccione un departamento</option>');
                    }
                },
                failure: function (errMsg) {
                    alert('Se presentó un error al realizar la consulta');

                }
            });
        }
    });

    departamento.change(function () {
        if(this.value) {
            $.ajax({
                url: URLDomain + "administracion/departamentos/" + this.value + "/municipios/json",
                type: 'GET',
                context: document.body,
                success: function (data) {
                    if (data.length > 0) {
                        let lista_opciones = $("#municipio_id option:selected");
                        let valores_seleccionados = municipio.val();
                        municipio.empty();
                        municipio.append('<option value="">Seleccione un municipio</option>');
                        $.each(lista_opciones, function(pos, v_opciones) {
                            $.each(valores_seleccionados, function(pos, v_valores) {
                                if(v_valores === v_opciones.value) {
                                    municipio.append(v_opciones);
                                }
                            });
                        });
                        for (let i = 0; i < data.length; i++) {
                            municipio.append('<option value="' + data[i].id + '">' + data[i].nombre + '</option>');
                        }
                    } else {
                        municipio.empty();
                        municipio.append('<option value="">Seleccione un municipio</option>');
                    }
                },
                failure: function (errMsg) {
                    alert('Se presentó un error al realizar la consulta');

                }
            });
        }
    });
});