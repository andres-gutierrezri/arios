function cambiarFotoPerfil(id) {
    let ruta = document.location.origin + "/talento-humano/colaboradores/" + id + "/foto-perfil";
    $('#mCambiarFotoPerfil').load(ruta, function () {
        try {
            $(this).modal('show');
            $(document).ready(function () {
                 $('#cambio_foto_perfil_id').change(function (e) {
                 $('.custom-file-label').html(e.target.files[0].name);
                 visualizarFoto(this);
                })
            });
            agregarValidacionFormularios();
        } catch (err) {
            console.log(err);
            EVANotificacion.toast.error('Ha ocurrido un error al cargar la foto de perfil');
        }
    });
}

function visualizarFoto(input) {
    if(input.files && input.files[0]){
        let reader = new FileReader();

        reader.onload = function (e) {
            $('#visualizador_imagen').html('<img src="' + e.target.result + '" class="shadow-2 cambio_foto_perfil" style="border-radius: 50% !important;" alt="">')
        };
        reader.readAsDataURL(input.files[0])
    }
}

function cerrarModalCambiarFoto() {
    $("#mCambiarFotoPerfil").modal('hide');
    $(".modal-backdrop").remove();
}
