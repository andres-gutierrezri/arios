
'use strict';

const selectAprobar = $("#Aprobar_id");
const selectRechazar = $("#Rechazar_id");
const comentario = $("#comentario_id");
const divComentario = comentario.parent()

selectAprobar.click(function () {
    if (selectAprobar) {
        $('.requiredFinal').removeAttr('required', 'true');
        divComentario.hide()
        comentario.attr('hidden', 'true');
        comentario.removeAttr('required', 'true');
    }
});

selectRechazar.click(function () {
    if (selectRechazar) {
        divComentario.show()
        comentario.removeAttr('hidden', 'true');
        comentario.attr('required', 'true');
    }
});