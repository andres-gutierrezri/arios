
'use strict';
let selectPorcentajeValor = $('#porcentaje_valor_id_select_id');
let selectFormaDePago = $('#forma_de_pago_id_select_id');

let divFormasDePago = $('#div_formas_pago');
let divAnticipo = $('#div_anticipo');
let divActasParciales = $('#div_actas_parciales');
let divLiquidacion = $('#div_liquidacion');
let inputAnticipo = $('#anticipo_id');
let inputActasParciales = $('#actas_parciales_id');
let inputLiquidacion = $('#liquidacion_id');

$(document).ready(function () {
    selectPorcentajeValor.change(function () {
        cambiosPorcentajeValor(this.value);
    });

    combinacionesFormasDePago(selectFormaDePago.val());
    selectFormaDePago.change(function () {
        combinacionesFormasDePago(this.value);
    });
});

let inputValorConIVA = $('#valor_con_iva_id');

function validarSumaPorcentajeValor(selectValor){
    if (selectPorcentajeValor.val() === '0') {
        if (selectValor > 100 || selectValor < 100){
            EVANotificacion.toast.error('El total de los valores no debe sumar el 100%');
            inputLiquidacion.val('');
            return false
        }
    }else{
        if (selectValor > parseInt(inputValorConIVA.val()) || selectValor < parseInt(inputValorConIVA.val())){
            EVANotificacion.toast.error('El total de los valores no debe ser igual al valor con IVA');
            inputLiquidacion.val('');
            return false
        }
    }
}

inputAnticipo.change(function () {
    cambiosAnticipo()
});

inputActasParciales.change(function () {
    cambiosActaParciales()
});

inputLiquidacion.change(function () {
    cambiosLiquidacion()
});

function cambiosAnticipo(){
    let sumaAnticipo = parseFloat(inputLiquidacion.val()) + parseFloat(inputAnticipo.val());
    if (inputActasParciales.is(':visible')) {
        sumaAnticipo += parseFloat(inputActasParciales.val());
    }
    validarSumaPorcentajeValor(sumaAnticipo)
}

function cambiosActaParciales(){
    let sumaActasParciales = parseFloat(inputLiquidacion.val()) + parseFloat(inputActasParciales.val());
    if (inputAnticipo.is(':visible')) {
        sumaActasParciales += parseFloat(inputAnticipo.val());
    }
    validarSumaPorcentajeValor(sumaActasParciales)
}

function cambiosLiquidacion(){
    let sumaLiquidacion = parseFloat(inputLiquidacion.val());
    if (inputAnticipo.is(':visible')) {
        sumaLiquidacion += parseFloat(inputAnticipo.val())
    }
    if (inputActasParciales.is(':visible')) {
        sumaLiquidacion += parseFloat(inputActasParciales.val())
    }
    validarSumaPorcentajeValor(sumaLiquidacion)
}

function cambiosPorcentajeValor(valor) {
    if (parseInt(valor) === 0){
        inputAnticipo.attr("placeholder", "Porcentaje");
        inputAnticipo.next('div').text('Por favor ingrese el porcentaje');
        inputActasParciales.attr('placeholder', 'Porcentaje');
        inputActasParciales.next('div').text('Por favor ingrese el porcentaje');
        inputLiquidacion.attr('placeholder', 'Porcentaje');
        inputLiquidacion.next('div').text('Por favor ingrese el porcentaje');
    }else{
        inputAnticipo.attr('placeholder', 'Valor');
        inputAnticipo.next('div').text('Por favor ingrese el valor');
        inputActasParciales.attr('placeholder', 'Valor');
        inputActasParciales.next('div').text('Por favor ingrese el valor');
        inputLiquidacion.attr('placeholder', 'Valor');
        inputLiquidacion.next('div').text('Por favor ingrese el valor');
    }
    cambiosAnticipo();
    cambiosActaParciales();
    cambiosLiquidacion()
}

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
            divFormasDePago.show();

            divAnticipo.removeClass('col-md-6');
            divAnticipo.addClass('col-md-4');
            divActasParciales.removeClass('col-md-6');
            divActasParciales.addClass('col-md-4');
            divLiquidacion.removeClass('col-md-6');
            divLiquidacion.addClass('col-md-4');
        }else if (valor === '2'){
            divAnticipo.show();
            divActasParciales.hide();

            inputAnticipo.attr('required', true);
            inputActasParciales.removeAttr('required', true);
            inputLiquidacion.attr('required', true);
            inputAnticipo.removeAttr('disabled', true);
            inputLiquidacion.removeAttr('disabled', true);
            divFormasDePago.show();

            divAnticipo.removeClass('col-md-4');
            divAnticipo.addClass('col-md-6');
            divLiquidacion.removeClass('col-md-4');
            divLiquidacion.addClass('col-md-6');
        }else if (valor === '3'){
            divAnticipo.hide();
            divActasParciales.show();

            inputAnticipo.removeAttr('required', true);
            inputActasParciales.attr('required', true);
            inputLiquidacion.attr('required', true);
            inputActasParciales.removeAttr('disabled', true);
            inputLiquidacion.removeAttr('disabled', true);
            divFormasDePago.show();

            divActasParciales.removeClass('col-md-4');
            divActasParciales.addClass('col-md-6');
            divLiquidacion.removeClass('col-md-4');
            divLiquidacion.addClass('col-md-6');
        }else{
            divAnticipo.show();
            divActasParciales.show();

            inputAnticipo.removeAttr('required', true);
            inputActasParciales.removeAttr('required', true);
            inputLiquidacion.removeAttr('required', true);
            divFormasDePago.hide();
        }
}