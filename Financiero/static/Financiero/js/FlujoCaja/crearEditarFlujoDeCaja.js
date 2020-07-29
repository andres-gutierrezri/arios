
'use strict';

const controls = {
    leftArrow: '<i class="fal fa-angle-left" style="font-size: 1.25rem"></i>',
    rightArrow: '<i class="fal fa-angle-right" style="font-size: 1.25rem"></i>'
};

function abrirModalCrearEditarFlujoDeCaja(url) {
    $('#crear_editar_flujo_caja').load(url, function (responseText) {
        try {
            if (responseText.includes("<!DOCTYPE html>")) {
                EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                return false;
            }
            $(this).modal('show');
            agregarValidacionFormularios();
            $('#fecha_movimiento_id').datepicker({
                todayHighlight: true,
                orientation: "bottom left",
                templates: controls,
                format: 'yyyy-mm-dd',
                autoclose: true
            });
            $('#subtipo_movimiento_id_select_id').select2({
                dropdownParent: $('#crear_editar_flujo_caja'),
                language: {
                    noResults: function() {
                      return "No se encontraron coincidencias";
                    },
                    searching: function() {
                      return "Buscando...";
                    }
              }
            });
        } catch (err) {
            console.log(err);
            EVANotificacion.toast.error('Ha ocurrido un error interno xxx');
        }
    });
}