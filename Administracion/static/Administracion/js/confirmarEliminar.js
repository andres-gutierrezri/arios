let URLDomain = document.location.origin+"/";
let idBorrar = 0;
let urlFinal;
let rutaBorrado = $('#rutaBorrado').val();

function fConfirmarEliminar(idElemento, justificar, fnCallback) {
    if (justificar){
        fSweetAlertEliminarJustificado(fnCallback);
    }else{
        fSweetAlert(fnCallback);
    }

    idBorrar = idElemento;
}

function fSweetAlert(fnCallback) {
    Swal.fire({
        title: '¿Está seguro de eliminar este item?',
        text: "Esta acción no se podrá revertir",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: '¡Sí, eliminarlo!',
        cancelButtonText: 'Cancelar'
    }).then(result => {
        confirmarEliminacion(result.value, URLDomain + rutaBorrado + "/" + idBorrar + "/delete", fnCallback)
    });
}

function fSweetAlertEliminarJustificado(fnCallback) {
    Swal.fire({
        title: '¿Está seguro de eliminar este item?',
        text: "Esta acción no se podrá revertir",
        icon: 'warning',
        input: 'text',
        inputPlaceholder: '¿Por qué deseas eliminar este item?',
        inputValue: '',
        inputAttributes: {'maxlength': 100},
        showCancelButton: true,
        confirmButtonText: '¡Sí, eliminarlo!',
        cancelButtonText: 'Cancelar',
        inputValidator: (value) => {
            if (!value) {
              return '¡Debes justificar esta acción!'
            }
        }
    }).then(result => {
        confirmarEliminacion(result.value, URLDomain + rutaBorrado + "/" + idBorrar + "/delete", fnCallback)
    });
}


function confirmarEliminacion(valor, url, fnCallback) {
    if (valor) {
        $.ajax({
            url: url,
            type: 'POST',
            context: document.body,
            data:JSON.stringify({'justificacion': valor}),
            contentType: "application/json; charset=utf-8;",
            dataType: "json",
            success: function (data) {
                if(data.estado === "OK") {
                    if((fnCallback !== undefined) && (typeof(fnCallback) === 'function'))
                    {
                        fnCallback();
                    }else{
                        location.reload();
                    }
                }else if(data.estado === "error"){
                    EVANotificacion.toast.error(data.mensaje);
                }
                else {
                    EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                }
            },
            failure: function (errMsg) {
                if((fnCallback !== undefined) && (typeof(fnCallback) === 'function'))
                    {
                        fnCallback();
                    }else{
                        location.reload();
                    }
            }
        });
    }
}

