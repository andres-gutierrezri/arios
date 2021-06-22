'use strict';
let extraTiposPertenencia = $('#extra_tipos_pertenencia');
let contratoSelect = $('#contrato_mostrar_id');
let procesoSelect = $('#proceso_mostrar_id');
let contratoSelectID = $('#contrato_id_select_id');
let procesoSelectID = $('#proceso_id_select_id');


const modalCrearGrupoActividad = $('#crear-grupo-actividad');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
});

function abrirModalCrearGrupoActividad(url) {
    cargarAbrirModal(modalCrearGrupoActividad, url, configurarModalCrear);
}

function configurarModalCrear() {
    extraTiposPertenencia = $('#extra_tipos_pertenencia');
    contratoSelect = $('#contrato_mostrar_id');
    procesoSelect = $('#proceso_mostrar_id');
    contratoSelectID = $('#contrato_id_select_id');
    procesoSelectID = $('#proceso_id_select_id');
    let idTipoPertenencia = $('#tipo_pertenencia_select_id').val();

    inicializarSelect2('tipo_pertenencia_select_id', modalCrearGrupoActividad);
    inicializarSelect2('contrato_id_select_id', modalCrearGrupoActividad);
    inicializarSelect2('proceso_id_select_id', modalCrearGrupoActividad);

     if (idTipoPertenencia === ""){
        $('#tipo_pertenencia_select_id').change(function () {
            let actual = this.value;
            cambiarSelect(actual);
        })
    }
    else{
        CambiarSelect(idTipoPertenencia);
        $('#tipo_pertenencia_select_id').change(function () {
            let actual = this.value;
            cambiarSelect(actual);
        })
    }

    agregarValidacionFormularios();
}


function cambiarSelect (actual){
    //$.each(jQuery.parseJSON(extraTiposPertenencia.val()), function(key, value) {
        //if (actual === 1) {
        let SELECCION_CONTRATO = "1";
            if (actual === SELECCION_CONTRATO) {
                mostrarOcultarTipoPertenencia(true)
            } else {
                mostrarOcultarTipoPertenencia(false)
            }
        //}S
   // })
}

function mostrarOcultarTipoPertenencia(tipo_pertenencia) {
    if (tipo_pertenencia){
        contratoSelect.show();
        contratoSelectID.attr("required", true);
        procesoSelect.hide();
        procesoSelectID.removeAttr('required', true);
    }else{
        procesoSelect.show();
        procesoSelectID.attr("required", true);
        contratoSelect.hide();
        contratoSelectID.removeAttr('required', true);
    }
}
