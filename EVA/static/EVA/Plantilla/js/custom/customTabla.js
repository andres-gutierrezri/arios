'use strict'

const IDIOMA_TABLA = {
    buttons: {
        copyTitle: 'Copiado al portapapeles',
        copySuccess: {
            _: '%d registros copiados',
            1: '1 registro copiado',
        },
    },
    info: 'Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros',
    infoEmpty: 'Mostrando registros del 0 al 0 de un total de 0 registros',
    emptyTable: 'No hay registros disponibles'
}

function getBotonesExportar(columnasExportar) {
    return [
        {
            extend: 'pdfHtml5',
            text: 'PDF',
            className: 'btn-outline-danger btn-sm mr-1',
            exportOptions: {
                columns: columnasExportar,
            },
        },
        {
            extend: 'excelHtml5',
            text: 'Excel',
            className: 'btn-outline-success btn-sm mr-1',
            exportOptions: {
                columns: columnasExportar,
            },
        },
        {
            extend: 'csvHtml5',
            text: 'CSV',
            className: 'btn-outline-primary btn-sm mr-1',
            exportOptions: {
                columns: columnasExportar,
            },
        },
        {
            extend: 'copyHtml5',
            text: 'Copiar',
            className: 'btn-outline-primary btn-sm mr-1',
            exportOptions: {
                columns: columnasExportar,
            },
        },
        {
            extend: 'print',
            text: 'Imprimir',
            className: 'btn-outline-primary btn-sm',
            exportOptions: {
                columns: columnasExportar,
            },
        }
    ]
}

/**
 *  Inicializa un una tabla como un datatable con la configuración especificada. Por defecto inicaliza la tabla que tenga
 *  el id = "dataTable"
 * @param config Objeto con la configuración para iniciar la tabla
 *  {
 *     columnasExportar: [],
 *     idTabla: "dataTable",
 *     ordenInicial: [[0, 'asc']],
 *     detallesColumnas:[{targets: [0, 4, 5], width: '8%'}],
 *     buscar: true/false,
 *     paginar: true/false,
 *     ordenar: true/false
 *     botones: []
 *     select: {}
 *  }
 */
function iniciarDataTableN(config = {}) {
    // initialize datatable
    config.idTabla = config.idTabla ?? 'dataTable'
    $(`#${config.idTabla}`).dataTable(
        {
            responsive: true,
            lengthChange: false,
            dom:
                "<'row mb-3'<'col-sm-12 col-md-6 d-flex align-items-center justify-content-start'f><'col-sm-12 col-md-6 d-flex align-items-center justify-content-end'lB>>" +
                "<'row'<'col-sm-12'tr>>" +
                "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
            aaSorting: config.ordenInicial ?? [[0, 'asc']],
            columnDefs: config.detallesColumnas ?? [],
            buttons: config.columnasExportar ? getBotonesExportar(config.columnasExportar) : config.botones ?? [],
            language: IDIOMA_TABLA,
            searching: config.buscar ?? true,
            paging: config.paginar ?? true,
            ordering: config.ordenar ?? true,
            select: config.select ?? null
        });
    $(`#${config.idTabla}_filter`).find("input").attr("placeholder", "Buscar");
}
