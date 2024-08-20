
'use sctric';

const selectTipoIdentificacion = $('#tipo_identificacion_select_id');

$(document).ready(function () {
    validarDV();
});


selectTipoIdentificacion.change(function (){
    validarDV();
});
function validarDV() {
    const tipoId =$('#tipo_identificacion_select_id option:selected').text();
    actdesInputDV(tipoId.includes('Tributaria'));
}

function actdesInputDV(activar) {
    let divIdentificacion = $('#identificacion_id').parent();
    const inputDV = $('#digito_verificacion_id');
    if(activar) {
        divIdentificacion.removeClass('col-xl-6 col-lg-6 col-md-12 col-sm-12');
        divIdentificacion.addClass('col-xl-4 col-lg-4 col-md-9 col-sm-9');
        inputDV.parent().show();
        inputDV.removeAttr('hidden', 'true');
        inputDV.attr('required', 'true');
    } else {

        if (inputDV !== undefined && inputDV != null) {
            inputDV.parent().hide();
            inputDV.attr('hidden', 'true');
            inputDV.removeAttr('required', 'true');
            divIdentificacion.removeClass('col-xl-4 col-lg-4 col-md-9 col-sm-9');
            divIdentificacion.addClass('col-xl-6 col-lg-6 col-md-12 col-sm-12');
        }
    }
}