'use strict';
let TipoPertenencia = $('#tipo_pertenencia');
let contratoSelect = $('#contrato_mostrar_id');
let procesoSelect = $('#proceso_mostrar_id');
let contratoSelectID = $('#contrato_id_select_id');
let procesoSelectID = $('#proceso_id_select_id');
let grupoSelectID = $('#grupo_pertenece_select_id');




const modalCrearGrupoActividad = $('#crear-grupo-actividad');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
});

function abrirModalCrearGrupoActividad(url) {
    cargarAbrirModal(modalCrearGrupoActividad, url, configurarModalCrear);
}

function configurarModalCrear() {
    TipoPertenencia = $('#tipo_pertenencia');
    contratoSelect = $('#contrato_mostrar_id');
    procesoSelect = $('#proceso_mostrar_id');
    contratoSelectID = $('#contrato_id_select_id');
    procesoSelectID = $('#proceso_id_select_id');
    grupoSelectID = $('#grupo_pertenece_select_id');
    let idTipoPertenencia = $('#tipo_pertenencia_select_id').val();

    inicializarSelect2('tipo_pertenencia_select_id', modalCrearGrupoActividad);
    inicializarSelect2('contrato_id_select_id', modalCrearGrupoActividad);
    inicializarSelect2('proceso_id_select_id', modalCrearGrupoActividad);
    inicializarSelect2('grupo_pertenece_select_id', modalCrearGrupoActividad);

     if (idTipoPertenencia === ""){
        $('#tipo_pertenencia_select_id').change(function () {
            let actual = this.value;
            cambiarSelect(actual);
        })
    }
    else{
        $('#tipo_pertenencia_select_id').change(function () {
            let actual = this.value;
            cambiarSelect(actual);
        }).trigger('change');
    }

    agregarValidacionFormularios();
}


function cambiarSelect (actual){
        let SELECCION_CONTRATO = "1";
            if (actual === SELECCION_CONTRATO) {
                mostrarOcultarTipoPertenencia(true)
            } else {
                mostrarOcultarTipoPertenencia(false)
            }
}

function mostrarOcultarTipoPertenencia(seleccion) {
    if (seleccion){
        contratoSelect.show();
        contratoSelectID.attr("required", true);
        procesoSelect.hide();
        procesoSelectID.removeAttr('required');
    }else{
        procesoSelect.show();
        procesoSelectID.attr("required", true);
        contratoSelect.hide();
        contratoSelectID.removeAttr('required');
    }
}
