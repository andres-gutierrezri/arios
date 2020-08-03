
'use strict';

function abrirModalHistorial(url) {
    $('#historial').load(url, function (responseText) {
        try {
            if (responseText.includes("<!DOCTYPE html>")) {
                EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                return false;
            }
            $(this).modal('show');
            $('#dataTableHistorial').dataTable({
                "iDisplayLength": -1,
               "aaSorting": [[ 3, "desc" ]],
                responsive: true,
                lengthChange: false,
                language: {
                info: 'Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros',
                infoEmpty:'Mostrando registros del 0 al 0 de un total de 0 registros',
                emptyTable: 'No hay registros disponibles',
                zeroRecords: 'No hay registros que coincidan'
        }
    });
    $("#dataTableHistorial_filter").find("input").attr("placeholder", "Buscar");
        } catch (err) {
            console.log(err);
            EVANotificacion.toast.error('Ha ocurrido un error interno');
        }
    });
}