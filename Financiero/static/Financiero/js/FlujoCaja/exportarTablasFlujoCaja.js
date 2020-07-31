$(document).ready(function() {
    iniciarTablaExportar([0, 1, 2, 3, 4]);
    $('#dataTableFlujoCaja').dataTable({
       "iDisplayLength": -1,
       "aaSorting": [[ 0, "desc" ]]
    });
});