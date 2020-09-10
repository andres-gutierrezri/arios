
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
let datosVigencias = $('#datos_vigencias');
let datosGarantias = $('#datos_garantias');


let valoresVigencias = [];
let valoresGarantias = [];

let contadorVigencia = 0;

function agregarVigencia(valores) {
    let datoAnho = anho.val();
    let datoVigencia = vigencia.val();
    if (valores){
        datoAnho = valores.valor_anho;
        datoVigencia = valores.valor_vigencia;
    }
    if (datoVigencia === '' || datoAnho === ''){
        EVANotificacion.toast.error('Debes llenar los campos disponibles antes de realizar esta acción.');
        return false;
    }
    eliminarVigencia.show();
    valoresVigencias.push({'valor_anho': datoAnho, 'valor_vigencia': datoVigencia});
    divVigencias.append('<div class="form-group" id="vigencia_'+ contadorVigencia +'" style="margin-bottom: 0">' +
        '<div class="form-row"><div class="col-md-6">\n' +
        '<label>Año de vigencia</label>\n' +
        '<input disabled type="text" id="valor_anho_'+ contadorVigencia +'" value="'+ datoAnho +'" class="form-control"></div>\n' +
        '<div class="col-md-5">\n' +
        '<label>Valor de vigencia</label>\n' +
        '<input disabled type="text" id="valor_vigencia_'+ contadorVigencia +'" value="'+ datoVigencia +'" class="form-control"></div>\n' +
        '<div class="col-md-1"></div></div><br></div>');
    contadorVigencia += 1;
    anho.val('');
    vigencia.val('');
    datosVigencias.val(JSON.stringify(valoresVigencias));
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
    datosVigencias.val(JSON.stringify(valoresVigencias));
}

let contadorGarantia = 0;

function agregarGarantia(valores) {
    let datoTipoGarantia = tipoGarantia.val();
    let datoNombreTipoGarantia = $("#tipo_garantia_id_select_id option:selected").text();
    let datoPorcentajeAsegurado = porcentajeAsegurado.val();
    let datoVigenciaGarantia = vigenciaGarantia.val();
    let datoGarantiaExtensiva = vigencia.val();
    if (valores){
        datoTipoGarantia = valores.tipo_garantia;
        datoNombreTipoGarantia = valores.nombre_tipo_garantia;
        datoPorcentajeAsegurado = valores.porcentaje_asegurado;
        datoVigenciaGarantia = valores.vigencia_garantia;
        datoGarantiaExtensiva = valores.garantia_extensiva;
    }
    if (datoTipoGarantia === '' || datoPorcentajeAsegurado === '' || datoVigenciaGarantia === ''){
        EVANotificacion.toast.error('Debes llenar los campos disponibles antes de realizar esta acción.');
        return false;
    }
    let inputCheck;
    let checkActivo = false;
    eliminarGarantia.show();
    if (garantiaExtensiva.prop('checked') || datoGarantiaExtensiva === true){
        inputCheck = '<input disabled checked id="valor_garantia_extensiva_'+ contadorGarantia +'" type="checkbox" class="custom-control-input">';
        checkActivo = true;
    }else{
        inputCheck = '<input disabled id="valor_garantia_extensiva_'+ contadorGarantia +'" type="checkbox" class="custom-control-input">';
    }

    valoresGarantias.push({'tipo_garantia': datoTipoGarantia, 'vigencia_garantia': datoVigenciaGarantia,
        'porcentaje_asegurado': datoPorcentajeAsegurado, 'garantia_extensiva': checkActivo, 'nombre_tipo_garantia': datoNombreTipoGarantia});

    divGarantias.append('<div class="form-group" id="garantia_'+ contadorGarantia +'" style="margin-bottom: 0">\n' +
        '<div class="form-row" style="padding-bottom: 0">\n' +
        '<div class="col-md-3">\n' +
        '<label>Tipo de Garantía</label>\n' +
        '<input hidden type="text" id="valor_tipo_garantia_'+ contadorGarantia +'" value="'+ datoTipoGarantia +'">\n' +
        '<input disabled type="text" id="texto_tipo_garantia_'+ contadorGarantia +'" value="'+ datoNombreTipoGarantia +'"\n' +
        'class="form-control">\n' +
        '</div>\n' +
        '<div class="col-md-3">\n' +
        '<label>Porcentaje Asegurado</label>\n' +
        '<input disabled type="text" id="valor_porcentaje_asegurado_'+ contadorGarantia +'" value="'+ datoPorcentajeAsegurado +'"\n' +
        'class="form-control">\n' +
        '</div>\n' +
        '<div class="col-md-3">\n' +
        '<label>Vigencia (Meses)</label>\n' +
        '<input disabled type="text" id="valor_vigencia_garantia_'+ contadorGarantia +'" value="'+ datoVigenciaGarantia +'" class="form-control">\n' +
        '</div>\n' +
        '<div class="col-md-2" style="padding-top: 33px;">\n' +
        '<div class="custom-control custom-checkbox">\n' + inputCheck +
        '<label class="custom-control-label">Garantía Extensiva</label>\n' +
        '</div></div>\n' +
        '<div class="col-md-1" style="padding-top:30px">\n' +
        '</div></div><br></div>');
    contadorGarantia += 1;

    $('#select2-tipo_garantia_id_select_id-container').text('Seleccione un tipo de garantía');
    tipoGarantia.val('');
    porcentajeAsegurado.val('');
    vigenciaGarantia.val('');
    garantiaExtensiva.prop('checked', false);
    datosGarantias.val(JSON.stringify(valoresGarantias));
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
    tipoGarantia.val(valorTipoGarantia);

    porcentajeAsegurado.val($('#valor_porcentaje_asegurado_'+ contadorGarantia).val());
    vigenciaGarantia.val($('#valor_vigencia_garantia_'+ contadorGarantia).val());

    if ($('#valor_garantia_extensiva_'+ contadorGarantia).prop('checked')){
        garantiaExtensiva.prop('checked', true);
    }else{
       garantiaExtensiva.prop('checked', false);
    }
    $('#garantia_'+ contadorGarantia).remove();
     datosGarantias.val(JSON.stringify(valoresGarantias));
}

let inputOrigenRecurso = $('#origen_recurso_id');
let selectOrigenRecurso = $('#origen_recurso_id_select_id');

function origenRecursos(){
    if(selectOrigenRecurso.val() === 1 || selectOrigenRecurso.val() === '1'){
        inputOrigenRecurso.removeAttr('disabled', true);
        inputOrigenRecurso.attr('required', true)
    }else{
        inputOrigenRecurso.attr('disabled', true);
        inputOrigenRecurso.removeAttr('required', true)
    }
}

let selectTipoContrato = $('#tipo_contrato_id_select_id');
let tiposContrato = JSON.parse($('#tipos_contrato').val());
let divAIU = $('#div_aiu');
let inputA = $('#porcentaje_a_id');
let inputI = $('#porcentaje_i_id');
let inputU = $('#porcentaje_u_id');

function verificarPorcentajeAIU(){
    $.each(tiposContrato, function(pos, tipos) {
        if(tipos.campo_valor === parseInt(selectTipoContrato.val())){
            if (tipos.porcentaje_aiu){
                divAIU.show();
                inputA.attr('required', true);
                inputI.attr('required', true);
                inputU.attr('required', true)
            }else{
                divAIU.hide();
                inputA.removeAttr('required', true);
                inputI.removeAttr('required', true);
                inputU.removeAttr('required', true)
            }
        }
    })
}

$(document).ready(function () {
    origenRecursos();
    selectOrigenRecurso.change(function () {
        origenRecursos();
    });
    verificarPorcentajeAIU();
    selectTipoContrato.change(function () {
        verificarPorcentajeAIU();
    });

    let selectFormaDePago = $('#forma_de_pago_id_select_id');
    combinacionesFormasDePago(selectFormaDePago.val());

    selectFormaDePago.change(function () {
        combinacionesFormasDePago(this.value);
    });
    let valores_vigencias = $('#valores_vigencias_actuales').val();
    let valores_garantias = $('#valores_garantias_actuales').val();
    if (valores_vigencias){
        $.each(JSON.parse(valores_vigencias), function (pos, vigencia) {
            agregarVigencia(vigencia)
        });
    }
    quitarVigencia();
    if (valores_garantias){
        $.each(JSON.parse(valores_garantias), function (pos, garantia) {
            agregarGarantia(garantia)
        });
    }
    quitarGarantia()
});

let divAnticipo = $('#div_anticipo');
let divActasParciales = $('#div_actas_parciales');
let divLiquidacion = $('#div_liquidacion');
let inputAnticipo = $('#anticipo_id');
let inputActasParciales = $('#actas_parciales_id');
let inputLiquidacion = $('#liquidacion_id');

function combinacionesFormasDePago(valor) {
    if(valor === '1'){
            divAnticipo.show();
            divActasParciales.show();

            inputAnticipo.attr('required', true);
            inputActasParciales.attr('required', true);
            inputLiquidacion.attr('required', true);
            inputAnticipo.removeAttr('disabled', true);
            inputActasParciales.removeAttr('disabled', true);
            inputLiquidacion.removeAttr('disabled', true);

            divAnticipo.removeClass('col-md-3');
            divAnticipo.addClass('col-md-2');
            divActasParciales.removeClass('col-md-3');
            divActasParciales.addClass('col-md-2');
            divLiquidacion.removeClass('col-md-3');
            divLiquidacion.addClass('col-md-2');
        }else if (valor === '2'){
            divAnticipo.show();
            divActasParciales.hide();

            inputAnticipo.attr('required', true);
            inputActasParciales.removeAttr('required', true);
            inputLiquidacion.attr('required', true);
            inputAnticipo.removeAttr('disabled', true);
            inputLiquidacion.removeAttr('disabled', true);

            divAnticipo.removeClass('col-md-2');
            divAnticipo.addClass('col-md-3');
            divLiquidacion.removeClass('col-md-2');
            divLiquidacion.addClass('col-md-3');
        }else if (valor === '3'){
            divAnticipo.hide();
            divActasParciales.show();

            inputAnticipo.removeAttr('required', true);
            inputActasParciales.attr('required', true);
            inputLiquidacion.attr('required', true);
            inputActasParciales.removeAttr('disabled', true);
            inputLiquidacion.removeAttr('disabled', true);

            divActasParciales.removeClass('col-md-2');
            divActasParciales.addClass('col-md-3');
            divLiquidacion.removeClass('col-md-2');
            divLiquidacion.addClass('col-md-3');
        }else{
            divAnticipo.show();
            divActasParciales.show();

            inputAnticipo.removeAttr('required', true);
            inputActasParciales.removeAttr('required', true);
            inputLiquidacion.removeAttr('required', true);
            inputAnticipo.attr('disabled', true);
            inputActasParciales.attr('disabled', true);
            inputLiquidacion.attr('disabled', true);


            divAnticipo.removeClass('col-md-3');
            divAnticipo.addClass('col-md-2');
            divActasParciales.removeClass('col-md-3');
            divActasParciales.addClass('col-md-2');
            divLiquidacion.removeClass('col-md-3');
            divLiquidacion.addClass('col-md-2');
        }
}

inputAnticipo.change(function () {
    let sumaAnticipo = parseFloat(inputLiquidacion.val()) + parseFloat(inputAnticipo.val());
    if (inputActasParciales.is(':visible')) {
        sumaAnticipo += parseFloat(inputActasParciales.val());
    }
    if (sumaAnticipo > 100){
        EVANotificacion.toast.error('El total de los valores no debe ser mayor al 100%');
        inputAnticipo.val('');
        return false
    }
});

inputActasParciales.change(function () {
    let sumaActasParciales = parseFloat(inputLiquidacion.val()) + parseFloat(inputActasParciales.val());
    if (inputAnticipo.is(':visible')) {
        sumaActasParciales += parseFloat(inputAnticipo.val());
    }
    if (sumaActasParciales > 100){
        EVANotificacion.toast.error('El total de los valores no debe ser mayor al 100%');
        inputActasParciales.val('');
        return false
    }
});

inputLiquidacion.change(function () {
    let sumaLiquidacion = parseFloat(inputLiquidacion.val());
    if (inputAnticipo.is(':visible')) {
        sumaLiquidacion += parseFloat(inputAnticipo.val())
    }
    if (inputActasParciales.is(':visible')) {
        sumaLiquidacion += parseFloat(inputActasParciales.val())
    }
    if (sumaLiquidacion > 100){
        EVANotificacion.toast.error('El total de los valores no debe ser mayor al 100%');
        inputLiquidacion.val('');
        return false
    }
});
