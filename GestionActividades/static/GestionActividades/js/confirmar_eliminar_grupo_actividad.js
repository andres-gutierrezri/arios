let URLDomain = document.location.origin + "/";
let idBorrar = 0;
let urlFinal;
let rutaBorrado = $('#rutaBorrado').val();
let eliminarGrupoActividad = '';

function fConfirmarEliminar(idElemento, elementoEliminar) {
    /* Se pasa como parámetro a la función un número que define el tipo de elemento que se va a eliminar
    1 si se va a eliminar un grupo y 2 si se va a eliminar una actividad*/
    fSweetAlert(elementoEliminar);
    idBorrar = idElemento;
}

function fSweetAlert(elementoEliminar) {
    if (elementoEliminar === 1) {
        eliminarGrupoActividad = 'este grupo de actividades'
    }
    if (elementoEliminar === 2) {
        eliminarGrupoActividad = 'esta actividad'
    }

    Swal.fire({
        title: '¿Está seguro de eliminar ' + eliminarGrupoActividad + '?',
        text: "Esta acción no se podrá revertir",
        icon: 'warning',
        input: 'text',
        inputPlaceholder: '¿Por qué deseas eliminar '+ eliminarGrupoActividad +  '?',
        inputValue: '',
        inputAttributes: {'maxlength': 100},
        showCancelButton: true,
        confirmButtonText: '¡Sí, eliminar!',
        cancelButtonText: 'Cancelar',
        inputValidator: (value) => {
            if (!value) {
                return '¡Debes justificar esta acción!'
            }
        }
    }).then(result => {
        confirmarEliminacion(result.value, URLDomain + rutaBorrado + "/" + idBorrar + "/delete")
    });
}

function confirmarEliminacion(valor, url) {
    if (valor) {
        $.ajax({
            url: url,
            type: 'POST',
            context: document.body,
            data: JSON.stringify({'justificacion': valor}),
            contentType: "application/json; charset=utf-8;",
            dataType: "json",
            success: function (data) {
                if (data.estado === "OK") {
                    location.reload();
                } else if (data.estado === "error") {
                    EVANotificacion.toast.error(data.mensaje);
                } else {
                    EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                }
            },
            failure: function (errMsg) {
                location.reload();
            }
        });
    }
}
