
'use strict';

function abrirModalHistorial(url) {
    $('#historial').load(url, function (responseText) {
        try {
            if (responseText.includes("<!DOCTYPE html>")) {
                EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                return false;
            }
            $(this).modal('show');
            iniciarDataTable([1, 2, 3, 4, 5, 6, 7, 8 , 9], 'dataTableHistorial');
        } catch (err) {
            console.log(err);
            EVANotificacion.toast.error('Ha ocurrido un error interno');
        }
    });
}
