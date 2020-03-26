var ver_todas = $('#ver_todas');
var not_empty = $('#not_empty');
var tab_notificaciones = $('#tab-messages');
var icono_not = $('#icono_not');
var titulo_not = $('#titulo_not');

$(document).ready(function () {
    fCargarNotificaciones();
});

function fCargarNotificaciones() {
    $.ajax({
        url: document.location.origin + "/notificaciones/notificaciones",
        context: document.body
    }).done(function (response) {
        if (response.Mensaje === 0){
            icono_not.show().hide();
            titulo_not.attr('title', 'No tienes notificaciones');
        }else {
            icono_not.text(response.Mensaje);
            titulo_not.attr('title', 'Tienes nuevas notifcaciones');
            icono_not.show()
        }
        var notificaciones = "";
        response.Notificaciones.forEach(function (item) {
            var estilo = 'read';
            if (!item.visto) {
                estilo = 'unread'
            }
            var accionClic;

            accionClic = 'fDetalleNotificacion(\''+ item.url +'\',' +
            item.id +','+ item.id_evento +',' + item.modal + ')';

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

titulo_not.click(function () {
     icono_not.hide();
 });