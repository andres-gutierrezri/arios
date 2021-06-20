'use strict';

const modalCrearReunion = $('#crear-reunion');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
    const columnDefs = [
        { "targets": [0], "width": '10%' },
        { "targets": [1], "width": '7%' },
        { "targets": [2], "width": '26%' },
        { "targets": [3], "width": '25%' },
        { "targets": [4], "width": '11%' },
        { "targets": [5], "width": '10%' },
        { "targets": [8], "width": '5%' },
        { "targets": [9], "width": '6%' }
    ]
    iniciarDataTableN({buscar: false, paginar: false, ordenar: false, detallesColumnas: columnDefs});
});

function abrirModalCrearReunion(url) {
    modalCrearReunion.load(url, function (responseText, textStatus, req) {
        try {
            if (responseText.includes("<!DOCTYPE html>")) {
                EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                return false;
            }
            $(this).modal('show');
            configurarModalCrear();
        } catch (err) {
            console.log(err);
            EVANotificacion.toast.error('Ha ocurrido un error al cargar el archivo');
        }
    });
}

function configurarModalCrear() {
    inicializarDatePicker('fecha_id');
    agregarValidacionFormularios();
}
