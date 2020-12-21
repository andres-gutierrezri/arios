
'use strict';

function cambiarEstadoProveedor(idProveedor, opcion) {
    let titulo;
    let mensaje;
    if (opcion === 'activar'){
        titulo = '¿Desea activar este proveedor?';
        mensaje = 'Si lo activa, podrá estar disponible como proveedor.'
    }else{
        titulo = '¿Desea desactivar este proveedor?';
        mensaje = 'Si lo desactiva, dejará de estar disponible como proveedor.'
    }
    Swal.fire({
        title: titulo,
        text: mensaje,
        type: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Confirmar',
        cancelButtonText: 'Cancelar'
    }).then(result => {
        if (result.value) {
            $.ajax({
                url: '/administracion/proveedores/'+ idProveedor +'/cambiar-estado',
                type: 'POST',
                context: document.body,
                success: function (data) {
                    if(data.estado === "OK") {
                        location.reload();
                    }else if(data.estado === "ERROR"){
                        EVANotificacion.toast.error(data.mensaje);
                    }
                },
                failure: function (errMsg) {
                    location.reload();
                }
            });
        }
    });
}