'use strict';

const modalCrearPermiso = $('#crear-permiso');

$(document).ready(function () {
    activarSelect2();
    $('#tipo_permisos_select_id').change(function () {
        window.location = '/talento-humano/permisos-laborales/' + this.value + '/index';
    });

    const columnDefs = [
        { "targets": [0], "width": '18%' },
        { "targets": [1], "width": '17%' },
        { "targets": [3], "width": '10%' },
        { "targets": [4], "width": '10%' },
        { "targets": [5], "width": '25%' },
        { "targets": [6], "width": '12%' },
        { "targets": [7], "width": '4%' },
        { "targets": [8], "width": '4%' }
    ]
    iniciarDataTableN({buscar: false, paginar: false, ordenar: false, detallesColumnas: columnDefs});
});

function abrirModalCrear(url) {
    cargarAbrirModal(modalCrearPermiso, url, configurarModalCrear);
}

function configurarModalCrear() {
    inicializarSelect2('tipo_permiso_select_id', modalCrearPermiso);
    inicializarDateRangePicker('fecha_intervalo_id');

    $('#archivo_id').change(function (e) {
        let label_input = $('.custom-file-label');
        let extension = e.target.files[0].name.split('.').pop();
        if (extension === 'pdf' || extension === 'docx'){
            label_input.html(e.target.files[0].name);
        }else{
            label_input.html('Seleccione un archivo');
            e.target.value = '';
            EVANotificacion.toast.error('El archivo ingresado no tiene un formato compatible. ' +
                                        '(Formatos Aceptados: PDF o Documento Word)');
            return false;
        }
    });
    agregarValidacionFormularios();
}
