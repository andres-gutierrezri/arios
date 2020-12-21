
'use strict';

$(document).ready(function () {
    function ejecutarSweetExitoso() {
        Swal.fire({
            position: "center",
            type: "success",
            title: "Se ha registrado correctamente!",
            text: "Revise la bandeja de entrada del correo electrónico indicado para continuar con el proceso.",
            showConfirmButton: true
        });
    }

    if ($("#mensaje_exitoso").val() === 'True') {
        ejecutarSweetExitoso();
    }
});