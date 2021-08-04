'use strict';

const modalCrearActividad = $('#crear-actividad');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
});

function abrirModalCrearActividad(url, grupo, usuario) {
    cargarAbrirModal(modalCrearActividad, url, function () {
        configurarModalCrear(grupo, usuario);
        let form = $('#actividad_form')[0];
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

function configurarModalCrear(grupo, usuario) {

    const idColaboradores = $('#responsables_id');
    const fechaInicioID = $('#fecha_inicio_id');
    const fechaFinalID = $('#fecha_final_id');
    const fechaInicioFinID = $('#fecha_inicio_fin_id');
    const idGrupo = $('#grupo_asociado_select_id');

    inicializarDatePicker('fecha_final_id');
    inicializarDatePicker('fecha_inicio_id');
    inicializarDateRangePicker('fecha_inicio_fin_id');
    inicializarSelect2('responsables_id', modalCrearActividad);
    inicializarSelect2('supervisor_id_select_id', modalCrearActividad);
    inicializarSelect2('grupo_asociado_select_id', modalCrearActividad);
    inicializarSelect2('estado_select_id', modalCrearActividad);


    if ($('#responsables_actividad').length > 0) {
        idColaboradores.val(JSON.parse($('#responsables_actividad').val())).trigger("change");
        //form = $('#actividad_form_editar')[0];
    }

    fechaInicioFinID.daterangepicker({
            locale: { format: 'YYYY-MM-DD',}
        }
    )

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

    if (usuario) {
        if (usuario !== parseInt($('#supervisor_id_select_id').val())){
            deshabilitarCamposFormulario(['nombre_id', 'supervisor_id_select_id', 'grupo_asociado_select_id',
                                               'descripcion_id', 'responsables_id', 'soporte_requerido_id'])
        }
    }

    agregarValidacionFormularios();
}
