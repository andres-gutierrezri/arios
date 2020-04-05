$(document).ready(function () {
    item = JSON.parse($('#datos_token').val())['lista_notificaciones'][0];
    fDetalleNotificacion(item.url ,item.id ,item.id_evento );
});