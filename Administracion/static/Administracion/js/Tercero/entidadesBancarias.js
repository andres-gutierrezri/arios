
'use strict';

$(document).ready(function () {

});

function configurarFormularioEntidadesBancarias(url) {
    const form = $("#entidades_bancarias_form");
    agregarValidacionForm(form[0], function (event){
        enviarFormulario(url)
        return true;
    });
}

function enviarFormulario(url) {
    let  formData = new FormData(document.getElementById("entidades_bancarias_form"));
    $.ajax({
        url: url,
        type: "post",
        dataType: "html",
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        success: function (data) {
            data = JSON.parse(data);
            if(data.estado === "OK") {
                location.reload();
            }else if(data.estado === "error"){
                EVANotificacion.toast.error(data.mensaje);
            }
            else {
                EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
            }
        },
        failure: function (errMsg) {
            location.reload();
        }
    })
}

function abrirModalGestionarEntidadBancaria(url) {
    $('#gestionar_entidad_bancaria').load(url, function (responseText) {
        try {
            if (responseText.includes("<!DOCTYPE html>")) {
                EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                return false;
            }
            $(this).modal('show');
            $('.select2').select2({
                dropdownParent: $('#gestionar_entidad_bancaria'),
                "language": {
                    noResults: function () {
                      return 'No se encontraron coincidencias';
                    },
                    searching: function () {
                      return 'Buscando…';
                    },
                    removeAllItems: function () {
                      return 'Quitar todas los items';
                    }
                },
            });
            $('#certificacion_id').change(function (e) {
                let label_input = $('.custom-file-label');
                let extension = e.target.files[0].name.split('.').pop();
                if (extension === 'pdf' || extension === 'docx'){
                    label_input.html(e.target.files[0].name);
                }else{
                    label_input.html('Seleccione un archivo');
                    e.target.value = '';
                    EVANotificacion.toast.error('El archivo ingresado no tiene un formato compatible. ' +
                                                '(Formatos Aceptados: PDF)');
                    return false;
                }
            });
            configurarFormularioEntidadesBancarias(url);
        } catch (err) {
            console.log(err);
            EVANotificacion.toast.error('Ha ocurrido un error al cargar el archivo');
        }
    });
}
