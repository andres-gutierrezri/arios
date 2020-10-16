
'use strict';

let selectSupervisorInterventor = $('#supervisor_interventor_id');
let divSupervisores = $('#div_supervisores');
let divInterventores = $('#div_interventores');
let inputSupervisores = $('#supervisor_id');
let inputInteventores = $('#interventor_id');
let radioSupervisor = $('#Supervisor_id');
let radioInterventor = $('#Interventor_id');

$(document).ready(function () {
    ValidarSeleccionSupervisorInterventor();
});

radioSupervisor.change(function () {
    selectSupervisorInterventor.val(this.value);
    ValidarSeleccionSupervisorInterventor();
});

radioInterventor.change(function () {
    selectSupervisorInterventor.val(this.value);
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