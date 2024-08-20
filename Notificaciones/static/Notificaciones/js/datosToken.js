$(document).ready(function () {
    let datos_token = $('#datos_token').val();
    if (datos_token){
        item = JSON.parse(datos_token)['lista_notificaciones'][0];
        fDetalleNotificacion(item.url ,item.id ,item.id_evento );
    }
});