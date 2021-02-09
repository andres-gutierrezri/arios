'use strict';

$(document).ready(function() {

    let opcionSelect = $("#opcion_id_select_id");
    let esContratos = $('#dataTable')[0].dataset.flujoContrato === 'true';

    iniciarDataTable(esContratos ? [0, 1, 2, 3, 4, 5, 6, 7] : [0, 1]);

    opcionSelect.change(function () {
        window.location = '/financiero/flujos-de-caja/' + opcionSelect.val();
    });

});
