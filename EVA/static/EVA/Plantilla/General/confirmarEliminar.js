var URLDomain = document.location.origin+"/";
var idBorrar = 0;
var urlFinal;
var rutaBorrado = $('#rutaBorrado').val();
$(document).ready(function() {

    $(".confirmarEliminarSi").click(function () {
        if ($('#id_eliminar').val() === 'medidor'){

            urlFinal = URLDomain + "recuperacion-perdidas/" + rutaBorrado + "/" + idBorrar + "/delete"
        }else{
            urlFinal = URLDomain + rutaBorrado + "/" + idBorrar + "/delete"
        }
        console.log(urlFinal);
        $.ajax({
            url: urlFinal,
            type: 'POST',
            context: document.body,
            success: function (data) {
                cerrarModalEliminar();
                if(data.Mensaje === "OK") {
                    location.reload();
                }
                else{
                    alert(data.Mensaje);
                }
            },
            failure: function (errMsg) {
                alert('Se presentó un error. No se pudo eliminar.');
                cerrarModalEliminar();
                location.reload();
            }
        });
    });
});

function cerrarModalEliminar() {
    $("#confirmarEliminar").modal('hide');
    $(".modal-backdrop").remove();
}

function fConfirmarEliminar(idElemento) {
    $("#confirmarEliminar").modal('show');
    idBorrar = idElemento;
}


