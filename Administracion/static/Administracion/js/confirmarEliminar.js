let URLDomain = document.location.origin+"/";
let idBorrar = 0;
let urlFinal;
let rutaBorrado = $('#rutaBorrado').val();

function fConfirmarEliminar(idElemento) {
    fSweetAlert();
    idBorrar = idElemento;
}

function fSweetAlert() {
    Swal.fire({
        title: '¿Está seguro de eliminar este Tercero?',
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
                        location.reload();
                    }
                },
                failure: function (errMsg) {
                    location.reload();
                }
            });
        }
    });
}






