'use strict';

const modalCrearReunion = $('#crear-reunion');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
    iniciarDataTableN({buscar: false, paginar: false, ordenar: false});
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
