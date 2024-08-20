
'use strict';
let URLDomain = document.location.origin+"/";
let pais = $("#pais_id_select_id");
let departamento = $("#departamento_id_select_id");
let municipio = $("#municipio_id");
let seleccionesPDM = $('#selecciones_pdm').val();
let valoresPDM;

$(document).ready(function() {
    if (seleccionesPDM){
        valoresPDM = JSON.parse(seleccionesPDM);
        seleccionarPais(valoresPDM);
    }
    pais.change(function () {
        if(pais.val()) {
            cargarDepartamentos(pais.val())
        }
    });

    departamento.change(function () {
        if(departamento.val()) {
            cargarMunicipios(departamento.val())
        }
    });
});

function seleccionarPais(valores) {
    pais.val(valores.id_pais);
    $('#select2-pais_id_select_id-container').text(valores.nombre_pais);
    cargarDepartamentos(valores.id_pais);
}

function seleccionarDepartamento(valores) {
    departamento.val(valores.id_departamento);
    $('#select2-departamento_id_select_id-container').text(valores.nombre_departamento);
    cargarMunicipios(valores.id_departamento)
}

function cargarDepartamentos(idPais) {
    $.ajax({
        url: URLDomain + "administracion/paises/" + idPais + "/departamentos/json",
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
            if (seleccionesPDM){
                valoresPDM = JSON.parse(seleccionesPDM);
                seleccionarDepartamento(valoresPDM);
            }
        },
        failure: function (errMsg) {
            alert('Se presentó un error al realizar la consulta');

        }
    });
}

function cargarMunicipios(idDepartamento) {
    if (seleccionesPDM) {
        valoresPDM =JSON.parse(seleccionesPDM);
    }
    $.ajax({
        url: URLDomain + "administracion/departamentos/" + idDepartamento + "/municipios/json",
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
                if (valoresPDM && valores_seleccionados.length === 0) {
                    $.each(valoresPDM.municipio, function (pos, objeto) {
                        municipio.append('<option selected value="' + objeto.id + '">' + objeto.nombre + '</option>')
                    });
                }
                for (let i = 0; i < data.length; i++) {
                    let coincidencia = false;
                    if (valoresPDM) {
                        $.each(valoresPDM.municipio, function (pos, mun) {
                            if (parseInt(mun.id) === parseInt(data[i].id)) {
                                coincidencia = true;
                            }
                        });
                        $.each(valores_seleccionados, function (pos, sel) {
                            if (parseInt(sel) === parseInt(data[i].id)) {
                                coincidencia = true;
                            }
                        });
                    }
                    if (!coincidencia){
                        municipio.append('<option value="' + data[i].id + '">' + data[i].nombre + '</option>');
                    }

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
