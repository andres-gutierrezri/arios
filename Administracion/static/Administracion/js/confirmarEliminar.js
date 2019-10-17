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
                        title: 'Quiere eliminar este campo?',
                        text: "Esta acción no se podrá revertir",
                        type: 'warning',
                        showCancelButton: true,
                        //confirmButtonColor: '#d33',
                        confirmButtonText: 'Sí, eliminarlo!',
                        cancelButtonText: 'Cancelar'
                    }).then(result => {
                        if (result.value) {

                            $.ajax({
                                    url: URLDomain + rutaBorrado + "/" + idBorrar + "/delete",
                                    type: 'POST',
                                    context: document.body,
                                    success: function (data) {
                                        if(data.Mensaje === "OK") {
                                            Swal.fire({
                                                title: "Eliminado!",
                                                text: "El campo ha sido eliminado.",
                                                //type: "error",
                                                confirmButtonText: "OK",
                                        preConfirm: function () {
                                            return new Promise(function (resolve) {
                                                resolve();
                    });
                }
                }).then(function () {
                    location.reload();
                });
                    }
                    else{
                        Swal.fire("Error!", "Error");
                    }


                                         //Swal.fire("Eliminado!", "El campo ha sido eliminado.");
                                    },
                                    failure: function (errMsg) {
                                        location.reload();
                                        Swal.fire("Error!", "Error");
                                    }
                            });
                        }
                    });

                }




