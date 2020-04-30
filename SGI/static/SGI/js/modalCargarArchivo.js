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
                $('.custom-file-label').html(e.target.files[0].name);
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
    let vinculoDiv = $('.div_vinculo');
    let archivo_id = $('#archivo_id');
    let vinculo_id = $('#vinculo_id');

    if(dato === 'archivo'){
        archivoDiv.show();
        archivo_id.attr('required', true);
        vinculo_id.removeAttr('required', true);
        vinculoDiv.hide();
    }else if(dato === 'vinculo'){
        vinculoDiv.show();
        vinculo_id.attr('required', true);
        archivo_id.removeAttr('required', true);
        archivoDiv.hide();


    }
}
