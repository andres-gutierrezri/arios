'use strict';
let TipoAsociado = $('#tipo_asociado');
let contratoSelect = $('#contrato_mostrar_id');
let procesoSelect = $('#proceso_mostrar_id');
let contratoSelectID = $('#contrato_id_select_id');
let procesoSelectID = $('#proceso_id_select_id');
let grupoSelectID = $('#grupo_asociado_select_id');

const modalCrearGrupoActividad = $('#crear-grupo-actividad');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
});

function abrirModalCrearGrupoActividad(url) {
    cargarAbrirModal(modalCrearGrupoActividad, url, function (){
        configurarModalCrear();
        let form = $('#grupo_actividad_form')[0];
        agregarValidacionForm(form, function (event) {
            enviarFormularioAsync(form, url, "cargando").then(exitoso => {
                if (exitoso) {
                    EVANotificacion.toast.exitoso(`Se ha ${url.includes("editar") ? "editado" : "creado"} el grupo de actividades`);
                    modalCrearGrupoActividad.modal('hide');
                    Swal.clickCancel();
                    setTimeout(function (){
                        location.reload();
                    },1000);
                }
                else{
                    Swal.clickCancel();
                }
            });
            return true;
        });
    });
}

function configurarModalCrear() {
    TipoAsociado = $('#tipo_asociado');
    contratoSelect = $('#contrato_mostrar_id');
    procesoSelect = $('#proceso_mostrar_id');
    contratoSelectID = $('#contrato_id_select_id');
    procesoSelectID = $('#proceso_id_select_id');
    grupoSelectID = $('#grupo_asociado_select_id');
    let idTipoAsociado = $('#tipo_asociado_select_id').val();
    let idTipoAsociadoRadio = $('#tipo_asociado_radio_id').val();

    inicializarSelect2('tipo_asociado_select_id', modalCrearGrupoActividad);
    inicializarSelect2('contrato_id_select_id', modalCrearGrupoActividad);
    inicializarSelect2('proceso_id_select_id', modalCrearGrupoActividad);
    inicializarSelect2('grupo_asociado_select_id', modalCrearGrupoActividad);

     if (idTipoAsociadoRadio === ""){
        $('#tipo_asociado_radio_id').change(function () {
            let actual = this.value;
            cambiarSelect(actual);
        })
    }
    else{
        $('#tipo_asociado_radio_id').change(function () {
            let actual = this.value;
            cambiarSelect(actual);
        }).trigger('change');
    }

    agregarValidacionFormularios();
}


function cambiarSelect (actual){
        let SELECCION_CONTRATO = "1";
            if (actual === SELECCION_CONTRATO) {
                mostrarOcultarTipoAsociado(true)
            } else {
                mostrarOcultarTipoAsociado(false)
            }
}

function mostrarOcultarTipoAsociado(seleccion) {
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
