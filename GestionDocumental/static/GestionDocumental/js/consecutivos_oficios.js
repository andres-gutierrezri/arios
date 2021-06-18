'use strict';

const modalCrearOficio = $('#crear-oficio');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
    const columnDefs = [
        { "targets": [0], "width": '12%' },
        { "targets": [1], "width": '10%' },
        { "targets": [2], "width": '28%' },
        { "targets": [3], "width": '28%' },
        { "targets": [4], "width": '11%' },
        { "targets": [7], "width": '5%' },
        { "targets": [8], "width": '6%' }
    ]
    iniciarDataTableN({buscar: false, paginar: false, ordenar: false, detallesColumnas: columnDefs});
});

function abrirModalCrearOficio(url) {
    modalCrearOficio.load(url, function (responseText, textStatus, req) {
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
    inicializarSelect2('contrato_id_select_id', modalCrearOficio);
    agregarValidacionFormularios();
}
