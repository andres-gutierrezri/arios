
'use strict';

let selectSupervisorInterventor = $('#supervisor_interventor_id_select_id');
let divSupervisores = $('#div_supervisores');
let divInterventores = $('#div_interventores');
let inputSupervisores = $('#supervisor_id');
let inputInteventores = $('#interventor_id');

$(document).ready(function () {
    ValidarSeleccionSupervisorInterventor();
});

selectSupervisorInterventor.change(function () {
    ValidarSeleccionSupervisorInterventor();
});

function ValidarSeleccionSupervisorInterventor() {
    if (selectSupervisorInterventor.val() === '0'){
        divSupervisores.show();
        divInterventores.hide();
        inputSupervisores.attr('required', true);
        inputInteventores.removeAttr('required', true);
    }else{
        divSupervisores.hide();
        divInterventores.show();
        inputSupervisores.removeAttr('required', true);
        inputInteventores.attr('required', true);
    }
}