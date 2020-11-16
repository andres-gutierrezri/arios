
'use strict';

function cargarDepartamentosDePais(idPais, departamento) {
    $.ajax({
        url: "/administracion/paises/" + idPais + "/departamentos/json",
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

function cargarMunicipiosDeDepartamento(idDepartamento, municipio) {
    $.ajax({
        url: "/administracion/departamentos/" + idDepartamento + "/municipios/json",
        type: 'GET',
        context: document.body,
        success: function (data) {
            if (data.length > 0) {
                municipio.empty();
                municipio.append('<option value="">Seleccione un municipio</option>');
                for (let i = 0; i < data.length; i++) {
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
}

function cargarCentroPobladoDeMunicipio(idMunicipio, centroPoblado) {
    $.ajax({
        url: "/administracion/municipios/" + idMunicipio + "/centros-poblados/json",
        type: 'GET',
        context: document.body,
        success: function (data) {
            if (data.length > 0) {
                centroPoblado.empty();
                centroPoblado.append('<option value="">Seleccione un centro poblado</option>');
                for (let i = 0; i < data.length; i++) {
                    centro_poblado.append('<option value="' + data[i].id + '">' + data[i].nombre + '</option>');
                }
            }else {
                centroPoblado.empty();
                centroPoblado.append('<option value="">Seleccione centro poblado</option>');
            }
        },
        failure: function (errMsg) {
            alert('Se presentó un error al realizar la consulta');

        }
    });
}