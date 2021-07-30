'use strict';

const modalAccionActividad = $('#accion-actividad');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
    const columnDefs = [
        { "targets": [0], "width": '12%' },
        { "targets": [1], "width": '10%' },
        { "targets": [2], "width": '28%' },
        { "targets": [4], "width": '28%' },
        { "targets": [6], "width": '11%' },
        { "targets": [7], "width": '11%' },
    ]
    iniciarDataTableN({buscar: false, paginar: false, ordenar: false, detallesColumnas: columnDefs});
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
