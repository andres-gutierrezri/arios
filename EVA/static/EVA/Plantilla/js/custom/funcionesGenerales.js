'use strict';

function abrirModalVistaPrevia(urlDocumento) {
    $("#if_vista_previa").attr('src', urlDocumento);
    $("#vista_previa_modal").modal('show');
}
