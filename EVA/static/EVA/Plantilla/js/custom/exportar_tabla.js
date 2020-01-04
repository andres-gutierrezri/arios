function iniciarTablaExportar(columnasExportar)
{
    // initialize datatable
    $('#dataTable').dataTable(
    {

        responsive: true,
        lengthChange: false,
        dom:

            /*	--- Layout Structure
                --- Options
                l	-	length changing input control
                f	-	filtering input
                t	-	The table!
                i	-	Table information summary
                p	-	pagination control
                r	-	processing display element
                B	-	buttons
                R	-	ColReorder
                S	-	Select

                --- Markup
                < and >				- div element
                <"class" and >		- div with a class
                <"#id" and >		- div with an ID
                <"#id.class" and >	- div with an ID and a class

                --- Further reading
                https://datatables.net/reference/option/dom
                --------------------------------------
             */
            "<'row mb-3'<'col-sm-12 col-md-6 d-flex align-items-center justify-content-start'f><'col-sm-12 col-md-6 d-flex align-items-center justify-content-end'lB>>" +
            "<'row'<'col-sm-12'tr>>" +
            "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
        buttons: [
            /*{
                extend:    'colvis',
                text:      'Column Visibility',
                titleAttr: 'Col visibility',
                className: 'mr-sm-3'
            },*/
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
            info: 'Mostrando registros del _START_ al _END_ de un total de  _TOTAL_ registros',

         }
    });
    $("#dataTable_filter").find("input").attr("placeholder", "Buscar");

}
