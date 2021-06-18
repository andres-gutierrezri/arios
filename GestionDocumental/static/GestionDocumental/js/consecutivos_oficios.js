'use strict';

const modalCrearOficio = $('#crear-oficio');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
    iniciarDataTableN({buscar: false, paginar: false, ordenar: false});
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
