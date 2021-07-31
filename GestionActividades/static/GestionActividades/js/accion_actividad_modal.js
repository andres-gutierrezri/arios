'use strict';

const modalAccionActividad = $('#accion-actividad');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
    const columnDefs = [
        { "targets": [0], "width": '10%' },
        { "targets": [1], "width": '10%' },
        { "targets": [2], "width": '10%' },
        { "targets": [3], "width": '28%' },
        { "targets": [5], "width": '28%' },
        { "targets": [7], "width": '7%' },
        { "targets": [8], "width": '7%' },
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
