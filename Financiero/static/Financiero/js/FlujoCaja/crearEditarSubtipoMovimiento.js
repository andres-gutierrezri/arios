
'use strict';

function abrirModalCrearEditarSubtipoMovimiento(url) {
    $('#crear_editar').load(url, function (responseText) {
        try {
            if (responseText.includes("<!DOCTYPE html>")) {
                EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                return false;
            }
            $(this).modal('show');
        } catch (err) {
            console.log(err);
            EVANotificacion.toast.error('Ha ocurrido un error interno');
        }
    });
}