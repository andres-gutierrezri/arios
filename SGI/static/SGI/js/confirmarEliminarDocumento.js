var URLDomain = document.location.origin+"/";
var idBorrar = 0;
var urlFinal;
var rutaBorrado = $('#rutaBorrado').val();

function fConfirmarEliminarDocumento(idElemento) {

     fSweetAlert();
    idBorrar = idElemento;
}

function fSweetAlert() {
    Swal.fire({
        title: '¿Está seguro de eliminar este Documento?',
        text: "Esta acción no se podrá revertir",
        type: 'warning',
        showCancelButton: true,
        confirmButtonText: '¡Sí, eliminarlo!',
        cancelButtonText: 'Cancelar'
    }).then(result => {

        if (result.value) {
            $.ajax({
                url: URLDomain + rutaBorrado + "/" + idBorrar + "/delete",
                type: 'POST',
                context: document.body,
                success: function (data) {
                    if(data.Mensaje === "OK") {
                        location.reload();
                    }
                    else {
                        EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                    }
                },
                failure: function (errMsg) {
                    location.reload();
                    Swal.fire({
                            title: "¡Error!",
                            text: "Ha ocurrido un error eliminando el documento",
                            type: 'error',
                        });
                }
            });
        }
    });
}





