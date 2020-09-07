$(document).ready(function() {

    let opcionSelect = $("#opcion_id_select_id");

    opcionSelect.change(function () {
        window.location = '/financiero/flujos-de-caja/' + opcionSelect.val();
    });

});