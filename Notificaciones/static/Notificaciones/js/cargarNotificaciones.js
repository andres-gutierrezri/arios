'use strict';
let ver_todas = $('#ver_todas');
let not_empty = $('#not_empty');
let tab_notificaciones = $('#tab-messages');
let icono_not = $('#icono_not');
let texto_not = $('#texto_not');

$(document).ready(function () {
    fCargarNotificaciones();
});

function fCargarNotificaciones() {
    $.ajax({
        url: document.location.origin + "/notificaciones/ver",
        context: document.body
    }).done(function (response) {
        if (response.Mensaje === 0){
            icono_not.show().hide();
            texto_not.text('No tienes notificaciones nuevas');
        }else {
            icono_not.text(response.Mensaje);
            texto_not.text('Tienes nuevas notifcaciones');
            icono_not.show()
        }
        let notificaciones = "";
        response.Notificaciones.forEach(function (item) {
            let estilo = 'read';
            if (!item.visto) {
                estilo = 'unread'
            }
            let accionClic;

            accionClic = 'fDetalleNotificacion(\''+ item.url +'\',' +
            item.id +','+ item.id_evento +',' + item.modal + ')';

            notificaciones +=(
                '<li class="'+ estilo +'">' +
                '<a href="#" onclick="'+ accionClic +'" class="d-flex align-items-center">' +
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

$('#btn_not').click(function () {
     icono_not.hide();
 });