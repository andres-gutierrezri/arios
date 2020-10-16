
'use strict';

let divOrigenRecurso = $('#div_origen_recurso');
let inputOrigenRecurso = $('#origen_recurso_id');
let selectOrigenRecurso = $('#origen_recurso_select_id');
let radioPropios = $('#Propios_id');
let radioOtro = $('#Otro_id');

function origenRecursos(){
    if(selectOrigenRecurso.val() === 1 || selectOrigenRecurso.val() === '1'){
        divOrigenRecurso.show();
        inputOrigenRecurso.attr('required', true)
    }else{
        divOrigenRecurso.hide();
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
function validarIngreso_AIU(objeto){
    if (objeto.val() < 0 || objeto.val() > 100){
        objeto.next('div').text('El porcentaje debe estar entre 1% y 100%.');
        objeto.val('');
        $('.sw-btn-next').click();
        return false;
    }
}
inputA.change(function () {
    validarIngreso_AIU(inputA)
});

inputI.change(function () {
    validarIngreso_AIU(inputI)
});

inputU.change(function () {
    validarIngreso_AIU(inputU)
});

$(document).ready(function () {
    origenRecursos();
    radioPropios.change(function () {
        selectOrigenRecurso.val(this.value);
        origenRecursos();
    });

    radioOtro.change(function () {
        selectOrigenRecurso.val(this.value);
        origenRecursos();
    });
    selectOrigenRecurso.change(function () {
        origenRecursos();
    });
    verificarPorcentajeAIU();
    selectTipoContrato.change(function () {
        verificarPorcentajeAIU();
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

    quitarGarantia();

    let botonSiguiente = $('.sw-btn-next');
    let botonAnterior = $('.sw-btn-prev');

    botonSiguiente.click(function () {
        if (botonSiguiente.hasClass('disabled')){
            botonSiguiente.text('Guardar');
            botonSiguiente.removeClass('disabled');
            botonSiguiente.removeClass('btn-secondary');
            botonSiguiente.addClass('btn-primary');
            botonSiguiente.attr('onclick', '$("#guardar").click()');
        }
    });

    botonAnterior.click(function () {
        botonSiguiente.text('Siguiente');
        botonSiguiente.removeClass('btn-primary');
        botonSiguiente.addClass('btn-secondary');
        botonSiguiente.removeAttr('onclick', '$("#guardar").click()');
    });
});

$('#valor_con_iva_id').change(function () {
    validarMinMaxInputMaskPorInput([this]);
    sumarCombinacionFormaDePago($('#porcentaje_valor_id'))
});

$('#valor_sin_iva_id').change(function () {
    validarMinMaxInputMaskPorInput([this]);
});

