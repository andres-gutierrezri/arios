
'use strict';

let checkExcentoIyc = $('#check_excento_iyc_id');
let checkContibuyenteIyc = $('#check_contribuyente_iyc_id');
let checkEntidadPublica = $('#check_entidad_publica_id');
let inputNumeroResolucion = $('#resolucion_id');
let inputContribuyenteIyc = $('#contribuyente_iyc_id');
let selectEntidadPublica = $('#entidad_publica_select_id');
let divExcentoIyc = $('#div_excento_iyc');
let divContibuyenteIyc = $('#div_contibuyente_iyc');
let divEntidadPublica = $('#div_entidad_publica');
let selectRegimen = $('#regimen_select_id');
let datosRegimenes = $('#json_datos_regimenes');

$(document).ready(function () {
    validarExcentoIyc();
    validarContribuyenteIyc();
    validarEntidadPublica();
    validarRegimen();
});

checkExcentoIyc.change(function () {
    validarExcentoIyc();
})

checkContibuyenteIyc.change(function () {
    validarContribuyenteIyc();
})

checkEntidadPublica.change(function () {
    validarEntidadPublica();
})

selectRegimen.change(function (){
    validarRegimen();
})

function validarExcentoIyc() {
    if(checkExcentoIyc.prop('checked')){
        divExcentoIyc.show();
        inputNumeroResolucion.attr('required', 'true')
        inputNumeroResolucion.removeAttr('hidden', 'true')
    }else{
        divExcentoIyc.hide();
        inputNumeroResolucion.removeAttr('required', 'true')
        inputNumeroResolucion.attr('hidden', 'true')
    }
}

function validarContribuyenteIyc() {
    if(checkContibuyenteIyc.prop('checked')){
        divContibuyenteIyc.show();
        inputContribuyenteIyc.attr('required', 'true')
        inputContribuyenteIyc.removeAttr('hidden', 'true')
    }else{
        divContibuyenteIyc.hide();
        inputContribuyenteIyc.removeAttr('required', 'true')
        inputContribuyenteIyc.attr('hidden', 'true')
    }
}

function validarEntidadPublica() {
    if(checkEntidadPublica.prop('checked')){
        divEntidadPublica.show();
        selectEntidadPublica.attr('required', 'true')
        selectEntidadPublica.removeAttr('hidden', 'true')
    }else{
        divEntidadPublica.hide();
        selectEntidadPublica.removeAttr('required', 'true')
        selectEntidadPublica.attr('hidden', 'true')
    }
}

function validarRegimen(){
    let jsonDatosRegimenes = JSON.parse(datosRegimenes.val())
    let entidadPublicaSH = $('.entidad_publica');
    let coincidencia = false;
    jsonDatosRegimenes.forEach(function (obj){
        if (obj.id === parseInt(selectRegimen.val()) && obj.aplica_publica){
            coincidencia = true;
        }
    })
    if (coincidencia){
        entidadPublicaSH.show();
    }else{
        entidadPublicaSH.hide();
        selectEntidadPublica.removeAttr('required', 'true')
        selectEntidadPublica.attr('hidden', 'true')
    }
}



