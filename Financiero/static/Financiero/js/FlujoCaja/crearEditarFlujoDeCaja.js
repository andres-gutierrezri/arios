
'use strict';

const controls = {
    leftArrow: '<i class="fal fa-angle-left" style="font-size: 1.25rem"></i>',
    rightArrow: '<i class="fal fa-angle-right" style="font-size: 1.25rem"></i>'
};

function abrirModalCrearEditarFlujoDeCaja(url, fecha_minima_mes, fecha_maxima_mes, estado) {
    $('#crear_editar_flujo_caja').load(url, function (responseText) {
        try {
            if (responseText.includes("error")) {
                let error = JSON.parse(responseText);
                EVANotificacion.toast.error(error.mensaje);
                return false;
            }
            $(this).modal('show');
            agregarValidacionFormularios();
            let inputFecha = $('#fecha_movimiento_id');
            inputFecha.datepicker({
                todayHighlight: true,
                orientation: "bottom left",
                templates: controls,
                format: 'yyyy-mm-dd',
                autoclose: true
            });
            let btnGuardar = $('#guardar');
            inputFecha.on("change", function(){
                if (new Date(inputFecha.val()) < new Date(fecha_minima_mes)){
                    inputFecha.next().find('div').prevObject.text('La fecha del movimiento no puede ser mayor a ' + fecha_maxima_mes);
                    btnGuardar.click();
                    inputFecha.val('');
                    return false
                }
                if (new Date(inputFecha.val()) > new Date(fecha_maxima_mes)){
                    if (estado !== 1){
                        inputFecha.next().find('div').prevObject.text('La fecha del movimiento no puede ser mayor a ' + fecha_maxima_mes);
                        btnGuardar.click();
                        inputFecha.val('');
                        return false
                    }
                }
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
            EVANotificacion.toast.error('Ha ocurrido un error interno');
        }
    });
}