var URLDomain = document.location.origin+"/";
var idBorrar = 0;
var urlFinal;
var rutaBorrado = $('#rutaBorrado').val();

function fConfirmarEliminar(idElemento) {
    // $("#confirmarEliminar").modal('show');
     fSweetAlert();
    idBorrar = idElemento;
}

function fSweetAlert() {
    Swal.fire({
                        title: '¿Está seguro de eliminar este Tercero?',
                        text: "Esta acción no se podrá revertir",
                        type: 'warning',
                        showCancelButton: true,
                        //confirmButtonColor: '#d33',
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






