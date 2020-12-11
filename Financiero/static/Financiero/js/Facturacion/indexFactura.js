'use strict';
let idFacturaAnular = null;
let motivoAnulacion = null;
let observacionesAnulacion = null;

$(document).ready(function () {
    configurarFormularios();
});

function configurarFormularios() {
    const form = $("#fanular_factura")[0];
    agregarValidacionForm(form, function (event){
        motivoAnulacion = $("#motivo_anulacion_id").val();
        observacionesAnulacion = $("#observaciones_id").val();
        $("#anular_modal").modal('hide');
        $(".modal-backdrop").remove();
        anularFactura();
        return true;
    });
}

function anularFacturaModal(idFactura) {
    idFacturaAnular = idFactura;
    $("#anular_modal").modal('show');

}

function anularFactura() {
    if(idFacturaAnular == null)
        return;

    EVANotificacion.modal.cargando("Anulando factura.");

    $.ajax({
            url: `/financiero/facturas/${idFacturaAnular}/anular`,
            context: document.body,
            type: 'POST',
            data: JSON.stringify({motivoAnulacion: motivoAnulacion, observacionesAnulacion: observacionesAnulacion}),
            contentType: "application/json; charset=utf-8;",
            dataType: "json",
    }).done(function(response) {
        if(response.hasOwnProperty('estado')){
            if (response.estado === 'OK') {
                EVANotificacion.toast.exitoso(`Se anuló la factura exitosamente`);
                setTimeout(() => window.location.reload(), 3000);

            } else {
                if (response.hasOwnProperty('mensaje'))
                    EVANotificacion.toast.error(response.mensaje);
                else
                    EVANotificacion.toast.error("Error no esperado.");
            }
        }

    }).fail(function () {
        EVANotificacion.toast.error('Falló la anulación de la factura');
    }).always(function () {
        EVANotificacion.modal.cerrar();
        idFacturaAnular = null;
    });
}
