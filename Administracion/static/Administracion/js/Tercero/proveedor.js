
'use strict';

let divRepresentanteLegal = $( '.representante-legal');
let selectTipoIdentificacion = $('#tipo_identificacion_select_id');
let nombreRazonSocial = $('#nombre_id');
let divFechaConstitucion = $('#div_fecha_constitucion');
let inputFechaConstitucion = $('#fecha_constitucion_id')
let divInicioActividad = $('#div_inicio_actividad');
let inputInicioActividad = $('#fecha_inicio_actividad_id')

let inputNombreRL = $('#nombre_rl_id');
let selectTipoIdentificacionRL = $('#tipo_identificacion_rl_select_id');
let inputIdentificacionRL = $('#identificacion_rl_id');

let selectRLPais = $('#pais_rl_select_id');
let selectRLDepartamento = $('#departamento_rl_select_id');
let selectRLMunicipio = $('#municipio_rl_select_id');

let selectUbicacionPais = $('#pais_select_id');
let selectUbicacionDepartamento = $('#departamento_select_id');
let selectUbicacionMunicipio = $('#municipio_select_id');

$(document).ready(function () {
    validarTipoIdentificacion();
});

selectRLPais.change(function (){
    cargarDepartamentosDePais(selectRLPais.val(), selectRLDepartamento)
});

selectRLDepartamento.change(function (){
    cargarMunicipiosDeDepartamento(selectRLDepartamento.val(), selectRLMunicipio)
});

selectUbicacionPais.change(function (){
    cargarDepartamentosDePais(selectUbicacionPais.val(), selectUbicacionDepartamento)
});

selectUbicacionDepartamento.change(function (){
    cargarMunicipiosDeDepartamento(selectUbicacionDepartamento.val(), selectUbicacionMunicipio)
});

selectTipoIdentificacion.change(function (){
    validarTipoIdentificacion()
});

function validarTipoIdentificacion() {
    let tiposIdentificacion = JSON.parse($('#json_tipo_identificacion').val());
    tiposIdentificacion.forEach(function (obj) {
        if(parseInt(obj.id) === parseInt(selectTipoIdentificacion.val())){
            if (obj.tipo_nit === true){
                divRepresentanteLegal.show();
                nombreRazonSocial.prev("label").text('Razón Social');
                nombreRazonSocial.attr('placeholder', 'Ingrese la razón social');
                divFechaConstitucion.show();
                inputFechaConstitucion.attr('required', 'true');
                inputFechaConstitucion.removeAttr('hidden', 'true')
                divInicioActividad.hide();
                inputInicioActividad.removeAttr('required', 'true')
                inputInicioActividad.attr('hidden', 'true')

                inputNombreRL.attr('required', 'true');
                inputNombreRL.removeAttr('hidden', 'true')
                selectTipoIdentificacionRL.attr('required', 'true');
                selectTipoIdentificacionRL.removeAttr('hidden', 'true')
                inputIdentificacionRL.attr('required', 'true');
                inputIdentificacionRL.removeAttr('hidden', 'true')
                selectRLPais.attr('required', 'true');
                selectRLPais.removeAttr('hidden', 'true')
                selectRLDepartamento.attr('required', 'true');
                selectRLDepartamento.removeAttr('hidden', 'true')
                selectRLMunicipio.attr('required', 'true');
                selectRLMunicipio.removeAttr('hidden', 'true')

                selectRLPais.attr('required', 'true');
                selectRLDepartamento.attr('required', 'true');
                selectRLMunicipio.attr('required', 'true');
                return false;
            }
        }else{
            divRepresentanteLegal.hide();
            nombreRazonSocial.prev("label").text('Nombre');
            nombreRazonSocial.attr('placeholder', 'Ingrese el nombre')
            divFechaConstitucion.hide();
            inputFechaConstitucion.removeAttr('required', 'true');
            inputFechaConstitucion.attr('hidden', 'true')
            divInicioActividad.show();
            inputInicioActividad.attr('required', 'true')
            inputInicioActividad.removeAttr('hidden', 'true')

            inputNombreRL.removeAttr('required', 'true');
            inputNombreRL.attr('hidden', 'true')
            selectTipoIdentificacionRL.removeAttr('required', 'true');
            selectTipoIdentificacionRL.attr('hidden', 'true')
            inputIdentificacionRL.removeAttr('required', 'true');
            inputIdentificacionRL.attr('hidden', 'true')
            selectRLPais.removeAttr('required', 'true');
            selectRLPais.attr('hidden', 'true')
            selectRLDepartamento.removeAttr('required', 'true');
            selectRLDepartamento.attr('hidden', 'true')
            selectRLMunicipio.removeAttr('required', 'true');
            selectRLMunicipio.attr('hidden', 'true')

            selectTipoIdentificacionRL.removeAttr('required', 'true');
            inputIdentificacionRL.removeAttr('required', 'true');

            selectRLPais.removeAttr('required', 'true');
            selectRLDepartamento.removeAttr('required', 'true');
            selectRLMunicipio.removeAttr('required', 'true');
        }
    });
}