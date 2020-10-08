$(document).ready(function() {
    iniciarTablaExportarConsecutivos([0, 1, 2, 3, 4, 5]);
});

function iniciarTablaExportarConsecutivos(columnasExportar)
{
    $('#dataTableConsecutivos').dataTable(
    {
        "order": [[ 0, "desc" ]],
        "columnDefs": [
               { "targets": 0,
                   "max-width": "80px",
               }],
        responsive: true,
        lengthChange: false,
        dom:
            "<'row mb-3'<'col-sm-12 col-md-6 d-flex align-items-center justify-content-start'f><'col-sm-12 col-md-6 d-flex align-items-center justify-content-end'lB>>" +
            "<'row'<'col-sm-12'tr>>" +
            "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
        buttons: [
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
        ],
        language: {
            buttons: {
                copyTitle: 'Copiado al portapapeles',
                copySuccess: {
                    _: '%d registros copiados',
                    1: '1 registro copiado',

                },
            },
            info: 'Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros',
            infoEmpty:'Mostrando registros del 0 al 0 de un total de 0 registros',
            emptyTable: 'No hay registros disponibles'
        }
    });
    $("#dataTableConsecutivos_filter").find("input").attr("placeholder", "Buscar");
}