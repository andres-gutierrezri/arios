'use strict';

const modalModificarActividad = $('#modificar-actividad');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
});

function abrirModalModificarActividad(url, grupo) {
    cargarAbrirModal(modalModificarActividad, url, function () {
        configurarModalModificarActividad(grupo);
        let form = $('#modificar_actividad_form')[0];
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

function configurarModalModificarActividad(grupo) {

    const idColaboradores = $('#_responsables_id');
    const fechaInicioID = $('#_fecha_inicio_id');
    const fechaFinalID = $('#_fecha_final_id');
    const idGrupo = $('#grupo_asociado_select_id');

    inicializarDatePicker('_fecha_final_id');
    inicializarDatePicker('_fecha_inicio_id');
    inicializarSelect2('_responsables_id', modalModificarActividad);
    inicializarSelect2('_supervisor_id_select_id', modalModificarActividad);
    inicializarSelect2('_grupo_asociado_select_id', modalModificarActividad);
    inicializarSelect2('estado_select_id', modalModificarActividad);


    if ($('#responsables_actividad').length > 0) {
        idColaboradores.val(JSON.parse($('#responsables_actividad').val())).trigger("change");
        //form = $('#actividad_form_editar')[0];
    }

    fechaInicioID.change(function () {
        if (new Date(fechaInicioID.val()) > new Date(fechaFinalID.val())) {
            fechaFinalID.val('');
            EVANotificacion.toast.advertencia('La fecha inicial no puede ser mayor a la fecha final');
        }
    });

    fechaFinalID.change(function () {
        if (new Date(fechaFinalID.val()) < new Date(fechaInicioID.val())) {
            fechaInicioID.val('');
            EVANotificacion.toast.advertencia('La fecha final no puede ser menor a la fecha inicial');
        }
    });

    if (grupo) {
        idGrupo.val(grupo).trigger("change");
    }

    agregarValidacionFormularios();
}
