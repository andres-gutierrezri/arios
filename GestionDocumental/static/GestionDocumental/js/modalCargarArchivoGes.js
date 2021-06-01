
const modalCrear = $('#crear');

function abrir_modal_cargar(url) {
    $('#cargar').load(url, function (responseText, textStatus, req) {
        try {
            if (responseText.includes("<!DOCTYPE html>")) {
                EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                return false;
            }
            $(this).modal('show');
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

function abrir_modal_crear(url) {
    modalCrear.load(url, function (responseText, textStatus, req) {
        try {
            if (responseText.includes("<!DOCTYPE html>")) {
                EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                return false;
            }
            $(this).modal('show');
            $('#fecha_inicio_id').datepicker({
                todayHighlight: true,
                orientation: "bottom left",
                templates: controls,
                format: 'yyyy-mm-dd',
                autoclose: true
            });
            $('#fecha_final_id').datepicker({
                todayHighlight: true,
                orientation: "bottom left",
                templates: controls,
                format: 'yyyy-mm-dd',
                autoclose: true
            });
            $('#tipo_contrato_select_id').select2({
                dropdownParent: modalCrear
                }
            );
            $('#colaborador_select_id').select2({
                dropdownParent: modalCrear
                }
            );
            agregarValidacionFormularios();
        } catch (err) {
            console.log(err);
            EVANotificacion.toast.error('Ha ocurrido un error al cargar el archivo');
        }
    });
}
