
'use strict';

let controls = {
                leftArrow: '<i class="fal fa-angle-left" style="font-size: 1.25rem"></i>',
                rightArrow: '<i class="fal fa-angle-right" style="font-size: 1.25rem"></i>'
            };


function agregarNovedad(usuario) {
    let ruta = document.location.origin + "/talento-humano/colaboradores/novedad/add/" + usuario;
    $('#mAgregarNovedad').load(ruta, function () {
        try {
            $(this).modal('show');
            $('#fecha_novedad_id ').datepicker({
                todayHighlight: true,
                orientation: "bottom left",
                templates: controls,
                format: 'yyyy-mm-dd',
                autoclose: true
            });

            $('.select2').select2({
                dropdownParent: $('#mAgregarNovedad'),
                placeholder: "Seleccione un tipo de novedad",
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
            agregarValidacionFormularios();
        } catch (err) {
            console.log(err);
            EVANotificacion.toast.error('Ha ocurrido un error al cargar la foto de perfil');
        }
    });
}
