'use strict';

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
