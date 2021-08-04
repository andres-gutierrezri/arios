'use strict';

const modalAccionActividad = $('#accion-actividad');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
    const columnDefs = [
        { "targets": [0], "width": '10%' },
        { "targets": [1], "width": '22%' },
        { "targets": [2], "width": '10%' },
        { "targets": [3], "width": '22%' },
        { "targets": [5], "width": '22%' },
        { "targets": [7], "width": '7%' },
        { "targets": [8], "width": '7%' },
    ]
    iniciarDataTableN({buscar: false, paginar: false, ordenar: false, detallesColumnas: columnDefs});
});

function abrirModalAccionActividad(url) {
    cargarAbrirModal(modalAccionActividad, url, function () {
        configurarModalAccionActividad();
        let form = $('#accion-actividad-form')[0];
        agregarValidacionForm(form, function (event) {
            enviarFormularioAsync(form, url, "cargando").then(exitoso => {
                if (exitoso) {

                    location.reload();
                }
            });
            return true;
        });
    });
}

function configurarModalAccionActividad() {

    const comentarioSupervisor = $('#comentario_supervisor');
    const comentarioSupervisorId = $('#comentario_supervisor_id');
    let accionActividad = $('#accion_actividad_id');

    if (accionActividad !== "2" || accionActividad !== "3" ){
        comentarioSupervisor.hide();
    }

    $('input:radio[name=accion_actividad]').change(function() {
        if (this.value === "2"){
            ocultarCamposFormulario([comentarioSupervisor, comentarioSupervisorId])

        }
        else{
            mostrarCamposFormulario([comentarioSupervisor, comentarioSupervisorId])
        }
    });

    agregarValidacionFormularios();
}


