
'use strict';

let divVigencias = $('#div_vigencias');
let anho = $('#anho_vigencia_id');
let vigencia = $('#valor_vigencia_id');
let valorConIVA = $('#valor_con_iva_id');
let eliminarVigencia = $('#eliminar_vigencia');
let datosVigencias = $('#datos_vigencias');
let valoresVigencias = [];
let contadorVigencia = 0;

let sumaValoresVigencias = 0;

 vigencia.change(function () {
    validarVigencias(valorConIVA, vigencia);
});

valorConIVA.change(function () {
    validarVigencias(valorConIVA, vigencia)
});

function validarVigencias(valorConIVA, valorVigencia) {
        let elemento = document.getElementById(valorVigencia[0].id);
        if (sumaValoresVigencias + Math.round10(Number(valorVigencia.inputmask('unmaskedvalue')), -2) > Number(valorConIVA.inputmask('unmaskedvalue'))){
            valorVigencia.next('div').text('La suma de los valores no puede ser mayor al valor con IVA.');
            elemento.setCustomValidity('.');
            return false
        }else{
            elemento.setCustomValidity('');
        }
        if (parseInt(valorVigencia.val()) < 0){
            valorVigencia.next('div').text('El valor ingresado no debe ser menor a cero.');
            elemento.setCustomValidity('.');
            return false;
        }else{
            elemento.setCustomValidity('');
        }
    }

function agregarVigencia(valores) {
    let datoAnho = anho.val();
    let datoVigencia = vigencia.val();
    let valorDatoVigencia = Number(vigencia.inputmask('unmaskedvalue'));
    if (valores){
        datoAnho = valores.valor_anho;
        datoVigencia = valores.valor_vigencia;
        valorDatoVigencia = valores.valor_vigencia
    }
    if (datoVigencia === '' || datoAnho === ''){
        $('.sw-btn-next').click();
        return false;
    }
    if (Number(vigencia.inputmask('unmaskedvalue')) < 0){
        vigencia.next('div').text('El valor ingresado no debe ser menor a cero.');
        vigencia.val('');
        $('.sw-btn-next').click();
        return false;
    }
    sumaValoresVigencias += Number(valorDatoVigencia);
    eliminarVigencia.show();
    valoresVigencias.push({'pos': contadorVigencia, 'valor_anho': datoAnho, 'valor_vigencia': Number(valorDatoVigencia)});
    if (datoVigencia.indexOf('$') === -1) {
        datoVigencia = numToCurrencyStr(Number(datoVigencia)).replace('COP', '$')
    }
    divVigencias.append('<div class="form-row" id="vigencia_'+ contadorVigencia +'" style="margin-bottom: 0">' +
        '<div class="form-group col-md-6">\n' +
        '<label>Año</label>\n' +
        '<input disabled type="text" id="valor_anho_'+ contadorVigencia +'" value="'+ datoAnho +'" class="form-control"></div>\n' +
        '<div class="form-group col-md-5">\n' +
        '<label>Valor</label>\n' +
        '<input disabled type="text" id="valor_vigencia_'+ contadorVigencia +'" value="'+ datoVigencia +'" class="form-control" style="text-align: right;"></div>\n' +
        '<div class="col-md-1" style="padding-top:30px">\n' +
        '<a class="far fa-2x far fa-edit" href="#" onclick="editarPosVigencia('+ contadorVigencia +')" title="" data-original-title="Agregar Vigencia" style=""></a>\n' +
        '<a class="far fa-2x far fa-trash-alt color-danger-900" href="#" onclick="quitarPosVigencia('+ contadorVigencia +')" title="" data-original-title="Eliminar Vigencia"></a>\n' +
        '</div>' +
        '</div>');
    contadorVigencia += 1;
    anho.val('');
    vigencia.val('');
    datosVigencias.val(JSON.stringify(valoresVigencias));
}

function editarPosVigencia(contador) {
    if (anho.val() !== '' && vigencia.val() !== ''){
        $('#agregar_vigencia').click();
    }
    retomarCampoVigencia(contador);
    valoresVigencias.forEach(function (elemento, pos) {
       if (elemento.pos === contador){
            valoresVigencias.splice(pos, 1)
       }
    });
    datosVigencias.val(JSON.stringify(valoresVigencias));
    $('#vigencia_'+ contador).remove();
    validarVigencias(valorConIVA, vigencia)
}

function quitarPosVigencia(contador) {
    valoresVigencias.forEach(function (elemento, pos) {
       if (elemento.pos === contador){
            valoresVigencias.splice(pos, 1)
       }
    });
    $('#vigencia_'+ contador).remove();
    datosVigencias.val(JSON.stringify(valoresVigencias));
    validarVigencias(valorConIVA, vigencia)
}

function quitarVigencia() {
    contadorVigencia -= 1;
    if (contadorVigencia === 0){
        eliminarVigencia.hide();
    }
    valoresVigencias.pop();
    retomarCampoVigencia(contadorVigencia);
    $('#vigencia_'+ contadorVigencia).remove();
    datosVigencias.val(JSON.stringify(valoresVigencias));
    validarVigencias(valorConIVA, vigencia)
}

function retomarCampoVigencia(contadorVigencia){
    let valorAnho = $('#valor_anho_' + contadorVigencia).val();
    let valorVigencia = $('#valor_vigencia_' + contadorVigencia).val();
    anho.val(valorAnho);
    vigencia.val(valorVigencia);
    sumaValoresVigencias -= Number(vigencia.inputmask('unmaskedvalue'));
    validarVigencias(valorConIVA, vigencia)
}
