
function abrir_modal_accion_documento(url) {
    $('#accion_documento').load(url, function (responseText, textStatus, req) {
        try {
            if(responseText.includes("<!DOCTYPE html>")){
                EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                return false;
            }
        $(this).modal('show');
        agregarValidacionFormularios();
        }
    catch(err) {
            console.log(err);
        EVANotificacion.toast.error('Ha ocurrido un error al cargar el archivo');
    }
    });
}
$(document).ready(function() {
    iniciarTablaExportar([0, 1, 2, 3]);
});