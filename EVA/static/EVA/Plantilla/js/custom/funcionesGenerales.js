'use strict';

function mostrarCamposFormulario(lista){
    lista.forEach(function (objeto){
        objeto.attr('required', 'true');
        objeto.removeAttr('hidden', 'true')
    })
}

function ocultarCamposFormulario(lista) {
    lista.forEach(function (objeto){
        objeto.removeAttr('required', 'true')
        objeto.attr('hidden', 'true')
    })
}

function abrirModalVistaPrevia(urlDocumento) {
    const ifVista =  $("#if_vista_previa");

    ifVista.attr('src', '');
    ifVista.attr('src', urlDocumento);

    $("#vista_previa_modal").modal('show');
}

const CONTROLES_DATEPICKER = {
	leftArrow: '<i class="fal fa-angle-left" style="font-size: 1.25rem"></i>',
	rightArrow: '<i class="fal fa-angle-right" style="font-size: 1.25rem"></i>'
};

/**
 * Inicializa un input como un datepicker.
 * @param inputId id del input que se quiere inicializar.
 */
function inicializarDatePicker(inputId) {

    $(`#${inputId}`).datepicker({
        todayHighlight: true,
        orientation: "bottom left",
        templates: CONTROLES_DATEPICKER,
        format: 'yyyy-mm-dd',
        autoclose: true
    });
}

const CONFIG_BASE_SELECT2 = {
    language: {
        noResults: function () {
            return 'No se encontraron coincidencias';
            },
        searching: function () {
            return 'Buscando…';
            },
        removeAllItems: function () {
            return 'Quitar todas los items';
            }
        }
}

/**
 * Inicializa un select como un select2.
 * @param selectId id del input que se quiere inicializar.
 * @param modal Si el select esta en un modal se debe pasar este para que se visualice correctamente.
 */
function inicializarSelect2(selectId, modal) {
    const conf = {};
    Object.assign(conf, CONFIG_BASE_SELECT2, (modal ? {dropdownParent: modal} : {}))
    $(`#${selectId}`).select2(conf);
}

/**
 * Activa como select2 todos los select con la clase .select2.
 */
function activarSelect2(){
    $('.select2').select2(CONFIG_BASE_SELECT2);
}

function copiarAPortapapeles(texto)
{
    navigator.clipboard.writeText(texto).then(() => {
        EVANotificacion.toast.exitoso(`Se copió ${texto} exitosamente`);
    }).catch(error => {
        console.log(error);
        EVANotificacion.toast.error(`Falló copiado`);
    });
}
