'use strict';

const modalAccionActividad = $('#accion-actividad');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
});

function abrirModalAccionActividad(url) {
    cargarAbrirModal(modalAccionActividad, url, function () {
        configurarModalAccionActividad();
        let form = $('#accion-actividad-form')[0];
        agregarValidacionForm(form, function (event) {
            enviarFormularioAsync(form, url, "cargando").then(exitoso => {
                if (exitoso) {

                    location.reload();
                }
            });
            return true;
        });
    });
}

function configurarModalAccionActividad() {

    agregarValidacionFormularios();
}
