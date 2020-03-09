'use strict';

toastr.options = {
  "closeButton": true,
  "debug": false,
  "newestOnTop": true,
  "progressBar": true,
  "positionClass": "toast-top-right",
  "preventDuplicates": true,
  "onclick": null,
  "showDuration": 300,
  "hideDuration": 100,
  "timeOut": 5000,
  "extendedTimeOut": 1000,
  "showEasing": "swing",
  "hideEasing": "linear",
  "showMethod": "fadeIn",
  "hideMethod": "fadeOut"
};

const SwalEspera = Swal.mixin({
    title: 'Un momento por favor...',
    allowEscapeKey:false,
    allowOutsideClick:false
});

const EVANotificacion = {
    modal: {
        cargando(mensaje) {
            SwalEspera.fire({
                text: mensaje
            });
            SwalEspera.showLoading();
        },
        general(tipo, mensaje) {
            Swal.fire({
                type: tipo,
                text: mensaje
            });
        },
        exitoso(mensaje) {
            this.general('success', mensaje);
        },
        error(mensaje) {
            this.general('error', mensaje);
        },
        advertencia(mensaje) {
            this.general('warning', mensaje);
        },
        informacion(mensaje) {
            this.general('info', mensaje);
        },
        cerrar() {
            Swal.close();
        },
    },

    toast:{
        general(tipo, mensaje) {
            toastr[tipo](mensaje);
        },
        exitoso(mensaje) {
            this.general('success', mensaje);
        },
        error(mensaje) {
            this.general('error', mensaje);
        },
        advertencia(mensaje) {
            this.general('warning', mensaje);
        },
        informacion(mensaje) {
            this.general('info', mensaje);
        },
        cerrarTodos() {
            toastr.clear();
        }
    }
};

$(document).ready(function(){
     mostrarNotifiacionesServidor();
});

function mostrarNotifiacionesServidor() {
    let mensaje = $('#mensaje');

    if (mensaje){
        if (mensaje.hasClass('alert.success'))
            EVANotificacion.toast.exitoso(mensaje.val());
        else if (mensaje.hasClass('alert.warning'))
            EVANotificacion.toast.advertencia(mensaje.val());
        else if (mensaje.hasClass('alert.error'))
            EVANotificacion.toast.error(mensaje.val());
        else if (mensaje.hasClass('alert.info'))
            EVANotificacion.toast.informacion(mensaje.val());
        else if (mensaje.hasClass('alert.debug'))
             EVANotificacion.toast.informacion(mensaje.val());
    }
}
