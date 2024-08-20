'use strict';

const controls = {
    leftArrow: '<i class="fal fa-angle-left" style="font-size: 1.25rem"></i>',
    rightArrow: '<i class="fal fa-angle-right" style="font-size: 1.25rem"></i>'
};

function abrir_modal_cargar(url) {
    $('#cargar').load(url, function (responseText, textStatus, req) {
        try {
            if (responseText.includes("<!DOCTYPE html>")) {
                EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                return false;
            }
            $(this).modal('show');
            $('#fecha_documento_id').datepicker({
                todayHighlight: true,
                orientation: "bottom left",
                templates: controls,
                format: 'yyyy-mm-dd',
                autoclose: true
            });
            $('#archivo_id').change(function (e) {
                let label_input = $('.custom-file-label');
                let extension = e.target.files[0].name.split('.').pop();
                if (extension === 'pdf' || extension === 'xlsx' || extension === 'docx' || extension === 'pptx'){
                    label_input.html(e.target.files[0].name);
                }else{
                    label_input.html('Seleccione un archivo');
                    e.target.value = '';
                    EVANotificacion.toast.error('El archivo ingresado no tiene un formato compatible. ' +
                                                '(Formatos Aceptados: PDF, Documento de Word, Documento de Excel, ' +
                                                'Presentacion de Power Point');
                    return false;
                }


            });
            agregarValidacionFormularios();
        } catch (err) {
            console.log(err);
            EVANotificacion.toast.error('Ha ocurrido un error al cargar el archivo');
        }
    });
}

function cambioCheck(dato) {
    let archivoDiv = $('.div_archivo');
    let enlaceDiv = $('.div_enlace');
    let archivoId = $('#archivo_id');
    let enlaceId = $('#enlace_id');

    if(dato === 'archivo'){
        archivoDiv.show();
        archivoId.attr('required', true);
        enlaceId.removeAttr('required', true);
        enlaceDiv.hide();
    }else if(dato === 'enlace'){
        enlaceDiv.show();
        enlaceId.attr('required', true);
        archivoId.removeAttr('required', true);
        archivoDiv.hide();


    }
}
