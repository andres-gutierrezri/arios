
'use strict';
let aplicaPorcentajeValor = $('#aplica_porcentaje_valor');
let selectPorcentajeValor = $('#porcentaje_valor_id');
let radioValor = $('#Valor_id');
let radioPorcentaje = $('#Porcentaje_id');
let selectFormaDePago = $('#forma_de_pago_id_select_id');

let divFormasDePago = $('#div_formas_pago');
let divAnticipo = $('#div_anticipo');
let divActasParciales = $('#div_actas_parciales');
let divLiquidacion = $('#div_liquidacion');
let inputAnticipo = $('#anticipo_id');
let inputActasParciales = $('#actas_parciales_id');
let inputLiquidacion = $('#liquidacion_id');

$(document).ready(function () {
    cambiosPorcentajeValor(selectPorcentajeValor.val());
    combinacionesFormasDePago(selectFormaDePago.val());
});

radioValor.change(function () {
    cambiosPorcentajeValor(this.value);
    selectPorcentajeValor.val(this.value);
    sumarCombinacionFormaDePago(this.value)
});


radioPorcentaje.change(function () {
    cambiosPorcentajeValor(this.value);
    selectPorcentajeValor.val(this.value);
    sumarCombinacionFormaDePago(this.value)
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
    if (valorInput !== 0){
        if (selectPorcentajeValor.val() === '0') {
            if (Math.round10(valorInput, -2) > 100 || Math.round10(valorInput, -2) < 100){
                EVANotificacion.toast.error('El total de los valores debe ser igual al 100%');
                inputLiquidacion.val('');
                return false
            }
        }else{
            if (Math.round10(valorInput, -2) > Number(inputValorConIVA.inputmask('unmaskedvalue')) ||
                Math.round10(valorInput, -2) < Number(inputValorConIVA.inputmask('unmaskedvalue'))){
                EVANotificacion.toast.error('El total de los valores debe ser igual al valor con IVA');
                inputLiquidacion.val('');
                return false
            }
        }
    }else{
        inputLiquidacion.val('');
        inputActasParciales.val('');
        inputAnticipo.val('');
        return false;
    }
}

inputAnticipo.blur(function () {
    sumarCombinacionFormaDePago(selectFormaDePago.val())
});

inputActasParciales.blur(function () {
    sumarCombinacionFormaDePago(selectFormaDePago.val())
});

inputLiquidacion.blur(function () {
    sumarCombinacionFormaDePago(selectFormaDePago.val())
});

function sumarCombinacionFormaDePago(selectFormaDePago) {
    let sumaTotal = 0;
    if (parseInt(selectFormaDePago) === 1){
        sumaTotal = Number(inputLiquidacion.inputmask('unmaskedvalue')) +
            Number(inputAnticipo.inputmask('unmaskedvalue')) +
            Number(inputActasParciales.inputmask('unmaskedvalue'))
    }else if (parseInt(selectFormaDePago) === 2){
        sumaTotal = Number(inputLiquidacion.inputmask('unmaskedvalue')) +
            Number(inputAnticipo.inputmask('unmaskedvalue'));
        inputActasParciales.val(0.01)
    }else if (parseInt(selectFormaDePago) === 3){
        sumaTotal = Number(inputLiquidacion.inputmask('unmaskedvalue')) +
            Number(inputActasParciales.inputmask('unmaskedvalue'));
        inputAnticipo.val(0.01)
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

        inputAnticipo.inputmask('remove');
        inputLiquidacion.inputmask('remove');
        inputActasParciales.inputmask('remove');

        inputAnticipo.removeAttr('data-inputmask');
        inputLiquidacion.removeAttr('data-inputmask');
        inputActasParciales.removeAttr('data-inputmask');

        inputAnticipo.inputmask({alias:'evaNumeric', removeMaskOnSubmit:true});
        inputLiquidacion.inputmask({alias:'evaNumeric', removeMaskOnSubmit:true});
        inputActasParciales.inputmask({alias:'evaNumeric', removeMaskOnSubmit:true});

    }else{
        inputAnticipo.attr('placeholder', 'Valor');
        inputAnticipo.next('div').text('Por favor ingrese el valor');
        inputActasParciales.attr('placeholder', 'Valor');
        inputActasParciales.next('div').text('Por favor ingrese el valor');
        inputLiquidacion.attr('placeholder', 'Valor');
        inputLiquidacion.next('div').text('Por favor ingrese el valor');

        inputAnticipo.attr('placeholder', 'Ingrese un valor');
        inputAnticipo.attr('max', '99999999999999.99');
        inputAnticipo.removeAttr('onInput', 'validarLongitud(5,this)');
        inputLiquidacion.attr('placeholder', 'Ingrese un valor');
        inputLiquidacion.attr('max', '99999999999999.99');
        inputLiquidacion.removeAttr('onInput', 'validarLongitud(5,this)');
        inputActasParciales.attr('placeholder', 'Ingrese un valor');
        inputActasParciales.attr('max', '99999999999999.99');
        inputActasParciales.removeAttr('onInput', 'validarLongitud(5,this)');

        inputLiquidacion.inputmask('remove');
        inputAnticipo.inputmask('remove');
        inputActasParciales.inputmask('remove');

        inputAnticipo.removeAttr('data-inputmask');
        inputLiquidacion.removeAttr('data-inputmask');
        inputActasParciales.removeAttr('data-inputmask');

        inputAnticipo.inputmask({alias:'evaCurrency', removeMaskOnSubmit:true});
        inputLiquidacion.inputmask({alias:'evaCurrency', removeMaskOnSubmit:true});
        inputActasParciales.inputmask({alias:'evaCurrency', removeMaskOnSubmit:true});
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

            inputAnticipo.inputmask();
            inputLiquidacion.inputmask();
            inputActasParciales.inputmask();

            divAnticipo.removeClass('col-md-6');
            divAnticipo.addClass('col-md-4');
            divActasParciales.removeClass('col-md-6');
            divActasParciales.addClass('col-md-4');
            divLiquidacion.removeClass('col-md-6');
            divLiquidacion.addClass('col-md-4');
            aplicaPorcentajeValor.show();
        }else if (valor === '2'){
            divAnticipo.show();
            divActasParciales.hide();

            inputAnticipo.attr('required', true);
            inputActasParciales.removeAttr('required', true);
            inputLiquidacion.attr('required', true);
            inputAnticipo.removeAttr('disabled', true);
            inputLiquidacion.removeAttr('disabled', true);
            divFormasDePago.show();

            inputAnticipo.inputmask();
            inputLiquidacion.inputmask();
            inputActasParciales.inputmask('remove');

            divAnticipo.removeClass('col-md-4');
            divAnticipo.addClass('col-md-6');
            divLiquidacion.removeClass('col-md-4');
            divLiquidacion.addClass('col-md-6');
            aplicaPorcentajeValor.show();
        }else if (valor === '3'){
            divAnticipo.hide();
            divActasParciales.show();

            inputAnticipo.removeAttr('required', true);
            inputActasParciales.attr('required', true);
            inputLiquidacion.attr('required', true);
            inputActasParciales.removeAttr('disabled', true);
            inputLiquidacion.removeAttr('disabled', true);
            divFormasDePago.show();

            inputAnticipo.inputmask('remove');
            inputLiquidacion.inputmask();
            inputActasParciales.inputmask();

            divActasParciales.removeClass('col-md-4');
            divActasParciales.addClass('col-md-6');
            divLiquidacion.removeClass('col-md-4');
            divLiquidacion.addClass('col-md-6');
            aplicaPorcentajeValor.show();
        }else{
            divAnticipo.show();
            divActasParciales.show();

            inputAnticipo.inputmask('remove');
            inputLiquidacion.inputmask('remove');
            inputActasParciales.inputmask('remove');

            inputAnticipo.removeAttr('required', true);
            inputActasParciales.removeAttr('required', true);
            inputLiquidacion.removeAttr('required', true);
            divFormasDePago.hide();
            aplicaPorcentajeValor.hide();
        }
}