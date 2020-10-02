
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
    cambiosPorcentajeValor(selectPorcentajeValor.value);
    combinacionesFormasDePago(selectFormaDePago.val());
});

selectPorcentajeValor.change(function () {
    cambiosPorcentajeValor(this.value);
});

selectFormaDePago.change(function () {
    combinacionesFormasDePago(this.value);
    sumarCombinacionFormaDePago(this.value)
});

let inputValorConIVA = $('#valor_con_iva_id');

function validarSumaPorcentajeValor(valorInput){
    if (selectPorcentajeValor.val() === '0') {
        if (valorInput > 100 || valorInput < 100){
            EVANotificacion.toast.error('El total de los valores debe ser igual al 100%');
            inputLiquidacion.val('');
            return false
        }
    }else{
        if (valorInput > parseFloat(inputValorConIVA.val()) || valorInput < parseFloat(inputValorConIVA.val())){
            EVANotificacion.toast.error('El total de los valores debe ser igual al valor con IVA');
            inputLiquidacion.val('');
            return false
        }
    }
}

inputAnticipo.change(function () {
    sumarCombinacionFormaDePago(selectFormaDePago.val())
});

inputActasParciales.change(function () {
    sumarCombinacionFormaDePago(selectFormaDePago.val())
});

inputLiquidacion.change(function () {
    sumarCombinacionFormaDePago(selectFormaDePago.val())
});

function sumarCombinacionFormaDePago(selectFormaDePago) {
    let sumaTotal = 0;
    if (parseInt(selectFormaDePago) === 1){
        sumaTotal = parseFloat(inputLiquidacion.val()) + parseFloat(inputAnticipo.val()) +
            parseFloat(inputActasParciales.val())
    }else if (parseInt(selectFormaDePago) === 2){
        sumaTotal = parseFloat(inputLiquidacion.val()) + parseFloat(inputAnticipo.val())
    }else if (parseInt(selectFormaDePago) === 3){
        sumaTotal = parseFloat(inputLiquidacion.val()) + parseFloat(inputActasParciales.val())
    }
    validarSumaPorcentajeValor(sumaTotal);
}

function cambiosPorcentajeValor(valor) {
    if (parseInt(valor) === 0){
        inputAnticipo.attr("placeholder", "Porcentaje");
        inputAnticipo.next('div').text('Por favor ingrese el porcentaje');
        inputActasParciales.attr('placeholder', 'Porcentaje');
        inputActasParciales.next('div').text('Por favor ingrese el porcentaje');
        inputLiquidacion.attr('placeholder', 'Porcentaje');
        inputLiquidacion.next('div').text('Por favor ingrese el porcentaje');

        inputAnticipo.attr('placeholder', 'Ingrese un porcentaje');
        inputAnticipo.attr('max', '100');
        inputAnticipo.attr('onInput', 'validarLongitud(5,this)');
        inputLiquidacion.attr('placeholder', 'Ingrese un porcentaje');
        inputLiquidacion.attr('max', '100');
        inputLiquidacion.attr('onInput', 'validarLongitud(5,this)');
        inputActasParciales.attr('placeholder', 'Ingrese un porcentaje');
        inputActasParciales.attr('max', '100');
        inputActasParciales.attr('onInput', 'validarLongitud(5,this)');

    }else{
        inputAnticipo.attr('placeholder', 'Valor');
        inputAnticipo.next('div').text('Por favor ingrese el valor');
        inputActasParciales.attr('placeholder', 'Valor');
        inputActasParciales.next('div').text('Por favor ingrese el valor');
        inputLiquidacion.attr('placeholder', 'Valor');
        inputLiquidacion.next('div').text('Por favor ingrese el valor');

        inputAnticipo.attr('placeholder', 'Ingrese un valor');
        inputAnticipo.attr('max', '99999999999999.99');
        inputAnticipo.attr('onInput', 'validarLongitud(16,this)');
        inputLiquidacion.attr('placeholder', 'Ingrese un valor');
        inputLiquidacion.attr('max', '99999999999999.99');
        inputLiquidacion.attr('onInput', 'validarLongitud(16,this)');
        inputActasParciales.attr('placeholder', 'Ingrese un valor');
        inputActasParciales.attr('max', '99999999999999.99');
        inputActasParciales.attr('onInput', 'validarLongitud(16,this)');
    }
    sumarCombinacionFormaDePago(selectFormaDePago.val())
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