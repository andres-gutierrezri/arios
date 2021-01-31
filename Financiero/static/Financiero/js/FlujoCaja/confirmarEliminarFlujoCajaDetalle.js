
'use strict';

let URLDomain = document.location.origin+"/";
let idBorrar = 0;
let rutaBorrado = $('#rutaBorrado').val();

function fConfirmarEliminar(idElemento) {

     fSweetAlert();
    idBorrar = idElemento;
}

function fSweetAlert() {
    Swal.fire({
        title: '¿Está seguro de eliminar este registro?',
        text: "Esta acción no se podrá revertir",
        icon: 'warning',
        input: "text",
        showCancelButton: true,
        confirmButtonText: '¡Sí, eliminarlo!',
        cancelButtonText: 'Cancelar',
        inputPlaceholder: "Ingrese el motivo de la eliminación",
        inputValidator: comentarios => {
            if (!comentarios) {
                return "Por favor ingresa el motivo de la eliminación";
            } else {
                return undefined;
            }
        },
        inputAttributes: {
            maxlength: 100
        }

    }).then(result => {

        if (result.value) {
            $.ajax({
                url: URLDomain + rutaBorrado + "/" + idBorrar + "/delete",
                type: 'POST',
                context: document.body,
                data: {'motivo': result.value},
                success: function (data) {
                    if(data.estado === "OK") {
                        location.reload();
                    }else if(data.estado === "error"){
                        EVANotificacion.toast.error(data.mensaje);
                    }
                    else {
                        EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                    }
                },
                failure: function (errMsg) {
                    location.reload();
                    Swal.fire("Error!", "Error");
                }
            });
        }
    });
}
