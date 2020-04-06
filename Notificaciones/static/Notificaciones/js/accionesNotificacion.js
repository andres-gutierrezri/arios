function fDetalleNotificacion(ruta, id_notificacion, id_evento, modal) {
    if (ruta.indexOf('°') > -1) {
        ruta_compuesta = ruta.replace('°', id_evento);
    }else if (!modal){
        ruta_compuesta = ruta
    }else{
        ruta_compuesta = ruta + '/' + id_evento;
    }
    if(modal){
        $.ajax({
            url: ruta_compuesta,
            context: document.body
        }).done(function (response) {
            accionesNotificacion(id_notificacion);
            let mDetalleGeneral = $("#mDetalleGeneral");
            mDetalleGeneral.html(response);
            mDetalleGeneral.modal('show');
        });
    }else {
        accionesNotificacion(id_notificacion);
        window.location = ruta_compuesta;
    }
}

function accionesNotificacion(id_notificacion){
    $.ajax({
            url: document.location.origin + '/notificaciones/'+ id_notificacion + '/actualizar',
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