'use strict';

const modalActualizarActividad = $('#actualizar-actividad');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
});

function abrirModalActualizarActividad(url) {
    cargarAbrirModal(modalActualizarActividad, url, function (){
        configurarModalActualizar();
        let form = $('#actualizar_actividad_form')[0];
        agregarValidacionForm(form, function (event) {
            enviarFormularioAsync(form, url, "cargando").then(exitoso => {
                if (exitoso) {
                    modalActualizarActividad.modal('hide');
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

function configurarModalActualizar() {

    inicializarDatePicker('fecha_avance_id');

    agregarValidacionFormularios();
}
