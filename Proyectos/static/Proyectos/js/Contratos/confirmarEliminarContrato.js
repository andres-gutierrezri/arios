var URLDomain = document.location.origin+"/";
var idBorrar = 0;
var urlFinal;
var rutaBorrado = $('#rutaBorrado').val();

function fConfirmarEliminarContrato(idElemento) {

     fSweetAlert();
    idBorrar = idElemento;
}

function fSweetAlert() {
    Swal.fire({
        title: '¿Está seguro de eliminar este Contrato?',
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
                        Swal.fire("Error!", "Error");
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





