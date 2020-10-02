
'use strict';

let divVigencias = $('#div_vigencias');
let divGarantias = $('#div_garantias');
let anho = $('#anho_vigencia_id');
let vigencia = $('#valor_vigencia_id');
let eliminarVigencia = $('#eliminar_vigencia');
let datosVigencias = $('#datos_vigencias');

let valoresVigencias = [];


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
    valoresVigencias.push({'pos': contadorVigencia, 'valor_anho': datoAnho, 'valor_vigencia': datoVigencia});
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



let divOrigenRecurso = $('#div_origen_recurso');
let inputOrigenRecurso = $('#origen_recurso_id');
let selectOrigenRecurso = $('#origen_recurso_id_select_id');

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

$(document).ready(function () {
    origenRecursos();
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


