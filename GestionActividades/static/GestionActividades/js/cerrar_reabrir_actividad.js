'use strict';

const modalCerrarReabrirActividad = $('#cerrar-reabrir-actividad');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
});

function abrirModalCerrarReabrirActividad(url) {
    cargarAbrirModal(modalCerrarReabrirActividad, url, function (){
        configurarModalCerrarReabrir();
        let form = $('#cerrar_reabrir_actividad_form')[0];
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

function configurarModalCerrarReabrir() {

    agregarValidacionFormularios();
}
