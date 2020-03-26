function fDetalleNotificacion(ruta, id_notificacion, id_evento) {
    if (ruta.indexOf('°') > -1){
        accionesNotificacion(id_notificacion);
        window.location = ruta.replace('°', id_evento);
    }else {
        $.ajax({
            url: ruta + '/' + id_evento,
            context: document.body
        }).done(function (response) {
            accionesNotificacion(id_notificacion);
            var mDetalleGeneral = $("#mDetalleGeneral");
            mDetalleGeneral.html(response);

            mDetalleGeneral.modal('show');
        });
    }
}

function accionesNotificacion(id_notificacion){
    $.ajax({
            url: document.location.origin + '/notificaciones/notificaciones/'+ id_notificacion + '/actualizar',
            type: 'POST',
            context: document.body,
            success: function (data) {
                if(data.Mensaje === "FAIL") {
                    console.log(data.Mensaje);
                }
            },
            failure: function (errMsg) {
                console.log('Se ha presentado un error al actualizar la notificacion. ' + errMsg)
            }
        });
}