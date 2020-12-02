'use strict';

const divIdentificacion = $('#identificacion_id').parent();

$(document).ready(function () {

    const tipoIdSelect = $('#tipo_identificacion_id_select_id');
    tipoIdSelect.change(function () {
        const tipoId =$('#tipo_identificacion_id_select_id option:selected').text();
        actdesInputDV(tipoId.includes('Tributaria'));
    });
});

function actdesInputDV(activar) {

    if(activar) {
        divIdentificacion.removeClass('col-md-6')
        divIdentificacion.addClass('col-md-5')
        divIdentificacion.parent().append('<div class="col-md-1"><label for="digito_verificacion_id">DV</label><input type="number" id="digito_verificacion_id" name="digito_verificacion" value="" placeholder="Ingrese el DV" required="" min="0" max="9" class="form-control"><div class="invalid-tooltip ">Por favor ingrese el digito de verificación</div>')
    } else {
        const inputDV = $('#digito_verificacion_id');
        if (inputDV !== undefined && inputDV != null) {
            inputDV.parent().remove();
            divIdentificacion.removeClass('col-md-5')
            divIdentificacion.addClass('col-md-6')
        }
    }
    console.log('Entro por acá');
}
