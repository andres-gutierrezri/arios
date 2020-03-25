var ver_todas = $('#ver_todas');
var not_empty = $('#not_empty');
var tab_notificaciones = $('#tab-messages');

$(document).ready(function () {
    fCargarNotificaciones();
});

function fCargarNotificaciones() {
    $.ajax({
        url: document.location.origin + "/notificaciones/notificaciones",
        context: document.body
    }).done(function (response) {
        console.log(response);
        if (response.Mensaje === 0){
            $('.alerta_nueva').hide()
        }else {
            $('#indicador_notificacion_lg').text(response.Mensaje);
            $('#indicador_notificacion_sm').text(response.Mensaje + ' New');
            $('.alerta_nueva').show()
        }
        var notificaciones = "";
        response.Notificaciones.forEach(function (item) {
            var estilo = 'read';
            if (!item.visto) {
                estilo = 'unread'
            }
            var accionClic;
            if (item.medidas === true || item.caracteristica === true){
                accionClic = 'accionEvento('+ item.id +')'
            }else {
                accionClic = 'fDetalleNotificacion(\''+ item.url +'\',' +
                item.id +','+ item.id_evento +')'
            }
            notificaciones +=(
                '<li class="'+ estilo +'">' +
                '<a onclick="'+ accionClic +'" class="d-flex align-items-center">' +
                '<span class="d-flex flex-column flex-1 ml-1">' +
                '<span class="name">' + item.titulo + '</span>' +
                '<span class="msg-b fs-xs">' + item.mensaje + '</span>' +
                '<span class="fs-nano text-muted mt-1">' + item.fecha + '</span>' +
                '</span></a></li>');
        });
        if (response.Notificaciones.length === 0){
            $('#cargar_notificaciones').hide();
            not_empty.addClass('active');
            ver_todas.attr('disabled')
        } else {
            $('#cargar_notificaciones').html(notificaciones);
            tab_notificaciones.addClass('active');
            ver_todas.removeAttr('disabled')
        }
    });
}

 $('#alertsDropdown').click(function () {
     $('.alerta_nueva').hide();
 });