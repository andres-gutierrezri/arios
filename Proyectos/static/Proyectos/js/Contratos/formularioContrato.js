
'use strict';

let divVigencias = $('#div_vigencias');
let divGarantias = $('#div_garantias');
let anho = $('#anho_vigencia_id');
let vigencia = $('#valor_vigencia_id');
let tipoGarantia = $('#tipo_garantia_id_select_id');
let porcentajeAsegurado = $('#porcentaje_asegurado_id');
let garantiaExtensiva = $('#garantia_extensiva');
let vigenciaGarantia = $('#vigencia_id');
let eliminarVigencia = $('#eliminar_vigencia');
let eliminarGarantia = $('#eliminar_garantia');

let valoresVigencias = [];
let valoresGarantias = [];

let contadorVigencia = 0;

function agregarVigencia() {
    if (vigencia.val() === '' || anho.val() === ''){
        EVANotificacion.toast.error('Debes llenar los campos disponibles antes de realizar esta acción.');
        return false;
    }
    eliminarVigencia.show();
    valoresVigencias.push({'anho': anho.val(), 'vigencia': vigencia.val()});
    divVigencias.append('<div class="form-group" id="vigencia_'+ contadorVigencia +'" style="margin-bottom: 0">' +
        '<div class="form-row"><div class="col-md-6">\n' +
        '<label>Año de vigencia</label>\n' +
        '<input disabled type="text" id="valor_anho_'+ contadorVigencia +'" value="'+ anho.val() +'" class="form-control"></div>\n' +
        '<div class="col-md-5">\n' +
        '<label>Valor de vigencia</label>\n' +
        '<input disabled type="text" id="valor_vigencia_'+ contadorVigencia +'" value="'+ vigencia.val() +'" class="form-control"></div>\n' +
        '<div class="col-md-1"></div></div></div>');
    contadorVigencia += 1;
    anho.val('');
    vigencia.val('');
}

function quitarVigencia() {
    contadorVigencia -= 1;
    if (contadorVigencia === 0){
        eliminarVigencia.hide();
    }
    valoresVigencias.pop();
    anho.val($('#valor_anho_' + contadorVigencia).val());
    vigencia.val($('#valor_vigencia_' + contadorVigencia).val());
    $('#vigencia_'+ contadorVigencia).remove();
}

let contadorGarantia = 0;

function agregarGarantia() {
    if (tipoGarantia.val() === '' || vigenciaGarantia.val() === '' || porcentajeAsegurado.val() === ''){
        EVANotificacion.toast.error('Debes llenar los campos disponibles antes de realizar esta acción.');
        return false;
    }
    let inputCheck;
    let checkActivo = false;
    eliminarGarantia.show();
    if (garantiaExtensiva.prop('checked')){
        inputCheck = '<input disabled checked id="valor_garantia_extensiva_'+ contadorGarantia +'" type="checkbox" class="custom-control-input">';
        checkActivo = true;
    }else{
        inputCheck = '<input disabled id="valor_garantia_extensiva_'+ contadorGarantia +'" type="checkbox" class="custom-control-input">';
    }

    valoresGarantias.push({'tipo_garantia': tipoGarantia.val(), 'vigencia_garantia': vigenciaGarantia.val(),
        'porcentaje_asegurado': porcentajeAsegurado.val(), 'garantia_extensiva': checkActivo});

    let textoSelect = $("#tipo_garantia_id_select_id option:selected").text();

    divGarantias.append('<div class="form-group" id="garantia_'+ contadorGarantia +'" style="margin-bottom: 0">\n' +
        '<div class="form-row" style="padding-bottom: 0">\n' +
        '<div class="col-md-3">\n' +
        '<label>Tipo de Garantía</label>\n' +
        '<input hidden type="text" id="valor_tipo_garantia_'+ contadorGarantia +'" value="'+ tipoGarantia.val() +'">\n' +
        '<input disabled type="text" id="texto_tipo_garantia_'+ contadorGarantia +'" value="'+ textoSelect +'"\n' +
        'class="form-control">\n' +
        '</div>\n' +
        '<div class="col-md-3">\n' +
        '<label>Porcentaje Asegurado</label>\n' +
        '<input disabled type="text" id="valor_porcentaje_asegurado_'+ contadorGarantia +'" value="'+ porcentajeAsegurado.val() +'"\n' +
        'class="form-control">\n' +
        '</div>\n' +
        '<div class="col-md-3">\n' +
        '<label>Vigencia (Meses)</label>\n' +
        '<input disabled type="text" id="valor_vigencia_garantia_'+ contadorGarantia +'" value="'+ vigenciaGarantia.val() +'" class="form-control">\n' +
        '</div>\n' +
        '<div class="col-md-2" style="padding-top: 33px;">\n' +
        '<div class="custom-control custom-checkbox">\n' + inputCheck +
        '<label class="custom-control-label">Garantía Extensiva</label>\n' +
        '</div></div>\n' +
        '<div class="col-md-1" style="padding-top:30px">\n' +
        '</div></div></div>');
    contadorGarantia += 1;

    $('#select2-tipo_garantia_id_select_id-container').text('Seleccione un tipo de garantía');
    $('#tipo_garantia_id_select_id').val('');
    porcentajeAsegurado.val('');
    vigenciaGarantia.val('');
    garantiaExtensiva.prop('checked', false);
}

function quitarGarantia() {
    contadorGarantia -= 1;

    if (contadorGarantia === 0){
        eliminarGarantia.hide();
    }
    valoresGarantias.pop();
    let valorTipoGarantia = $('#valor_tipo_garantia_' + contadorGarantia).val();
    let textoTipoGarantia = $('#texto_tipo_garantia_' + contadorGarantia).val();

    $('#select2-tipo_garantia_id_select_id-container').text(textoTipoGarantia);
    $('#tipo_garantia_id_select_id').val(valorTipoGarantia);

    porcentajeAsegurado.val($('#valor_porcentaje_asegurado_'+ contadorGarantia).val());
    vigenciaGarantia.val($('#valor_vigencia_garantia_'+ contadorGarantia).val());

    if ($('#valor_garantia_extensiva_'+ contadorGarantia).prop('checked')){
        garantiaExtensiva.prop('checked', true);
    }else{
       garantiaExtensiva.prop('checked', false);
    }
    $('#garantia_'+ contadorGarantia).remove();
}