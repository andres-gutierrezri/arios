'use strict';

const divIdentificacion = $('#identificacion_id').parent();
const wizard = $("#smartwizard");
const selectTipoTercero = $('#tipo_tercero_id_select_id');
const formTercero = $('#tercero-form');
let btnAnterior;
let btnSiguiente;

$(document).ready(function () {

    iniciarFormTercero();
    const tipoIdSelect = $('#tipo_identificacion_id_select_id');
    tipoIdSelect.change(function () {
        const tipoId =$('#tipo_identificacion_id_select_id option:selected').text();
        actdesInputDV(tipoId.includes('Tributaria'));
    });
    selectTipoTercero.change(function () {
        actdesInfoFacturacion();
    });
});

function actdesInputDV(activar) {

    if(activar) {
        divIdentificacion.removeClass('col-md-6');
        divIdentificacion.addClass('col-md-5');
        divIdentificacion.parent().append('<div class="col-md-1"><label for="digito_verificacion_id">DV</label><input type="number" id="digito_verificacion_id" name="digito_verificacion" value="" placeholder="Ingrese el DV" required="" min="0" max="9" class="form-control"><div class="invalid-tooltip ">Por favor ingrese el digito de verificación</div>');
    } else {
        const inputDV = $('#digito_verificacion_id');
        if (inputDV !== undefined && inputDV != null) {
            inputDV.parent().remove();
            divIdentificacion.removeClass('col-md-5');
            divIdentificacion.addClass('col-md-6');
        }
    }
}

function iniciarFormTercero() {
    wizard.smartWizard({
        selected: 0, // Initial selected step, 0 = first step
        keyNavigation: false, // Enable/Disable keyboard navigation(left and right keys are used if enabled)
        autoAdjustHeight: false, // Automatically adjust content height
        cycleSteps: false, // Allows to cycle the navigation of steps
        backButtonSupport: true, // Enable the back button support
        useURLhash: false, // Enable selection of the step based on url hash
        showStepURLhash: false,
        lang:
            { // Language variables
                next: 'Siguiente',
                previous: 'Anterior'
            },
        toolbarSettings:
            {
                toolbarPosition: 'bottom', // none, top, bottom, both
                toolbarButtonPosition: 'right', // left, right
                showNextButton: false, // show/hide a Next button
                showPreviousButton: false, // show/hide a Previous button
                toolbarExtraButtons: [
                    $('<button id="btn_anterior_id" type="button"></button>').text('Anterior')
                          .addClass('btn btn-secondary btn-pills')
                          .on('click', anterior),
                    $('<button id="btn_siguiente_id" type="button"></button>').text('Siguiente')
                          .addClass('btn btn-secondary btn-pills')
                          .on('click', siguiente)
                ]
            },
        anchorSettings:
            {
                anchorClickable: true, // Enable/Disable anchor navigation
                enableAllAnchors: false, // Activates all anchors clickable all times
                markDoneStep: true, // add done css
                enableAnchorOnDoneStep: true // Enable/Disable the done steps navigation
            },
        contentURL: null, // content url, Enables Ajax content loading. can set as data data-content-url on anchor
        contentCache: true, //ajax content
        disabledSteps: [], // Array Steps disabled,
        errorSteps: [], // Highlight step with errors
        theme: 'arrows', //dots, default, circles
        transitionEffect: 'slide', // Effect on navigation, none/slide/fade
        transitionSpeed: '400'
    });

    btnAnterior = $('#btn_anterior_id');
    btnSiguiente = $('#btn_siguiente_id');

    wizard.on("leaveStep", function(e, anchorObject, stepNumber, stepDirection) {

        let elmForm = $("#step-" + (stepNumber + 1));

        if(stepDirection === 'forward'){
            return validarForm(stepNumber)
        }
        return true;
    });

    wizard.on("showStep", function(e, anchorObject, stepNumber, stepDirection) {
        activarBtnGuardar(stepNumber === 1);
        activarBtnCancelar(stepNumber === 0);
    });

    actdesInfoFacturacion();
}

function validarForm(numPaso){
     let formPart = $(`#step-${numPaso}`);
    if(formPart){
        let form = document.getElementById("tercero-form");
        if(!form.checkValidity()){
            formPart[0].classList.add('was-validated');
        }
        let count = 0;
        formPart.find(".invalid-tooltip").each(function(){
            if($(this).is(":visible")){
                count++;
            }
        });

        if(count > 0){
            // Form validation failed
            return false;
        }
    }
    return true;
}

function anterior(){
    if(btnAnterior.text() === 'Cancelar')
        window.location = '/administracion/terceros';
    else
        wizard.smartWizard("prev");
}
function siguiente() {
    if(btnSiguiente.text() === 'Guardar') {
        if(validarForm(0) && validarForm(1))
            formTercero.submit();
    }
    else
        wizard.smartWizard("next");
}

function actdesInfoFacturacion() {
    const tipoTercero = Number(selectTipoTercero.val());
    // Cliente
    if(tipoTercero === 1) {
        activarBtnCancelar(false);
        activarBtnGuardar(false);
        wizard.smartWizard("stepState", [1], "enable");
    } else {
        activarBtnCancelar(true);
        activarBtnGuardar(true);
        wizard.smartWizard("stepState", [1], "disable");

    }
}
function activarBtnGuardar(activar) {
    if(activar){
        btnSiguiente.text("Guardar");
        btnSiguiente.removeClass('btn-secondary')
        btnSiguiente.addClass('btn-primary')
    } else {
        btnSiguiente.text("Siguiente");
        btnSiguiente.removeClass('btn-primary');
        btnSiguiente.addClass('btn-secondary');
    }
}

function activarBtnCancelar(activar) {
    if(activar){
        btnAnterior.text("Cancelar");
        btnAnterior.removeClass('btn-secondary')
        btnAnterior.addClass('btn-danger')
    } else {
        btnAnterior.text("Anterior");
        btnAnterior.removeClass('btn-danger');
        btnAnterior.addClass('btn-secondary');
    }
}
