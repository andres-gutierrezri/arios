'use strict';

const modalCrearEditar = $('#crear-editar-consecutivo');
let fechaInicioID = $('#fecha_inicio_id');
let fechaFinalID = $('#fecha_final_id');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();

    iniciarDataTableN({buscar: false, paginar: false, ordenar: false});
});


function abrirModalCrear(url) {
    cargarAbrirModal(modalCrearEditar, url,function () {
        configurarModalCrear();
        const form = $("#requerimientos_form")[0];
        agregarValidacionForm(form, function (event) {
            enviarFormularioAsync(form, url).then(exitoso => {
                if (exitoso)
                    location.reload();
            });
            return true;
        });
    });
}

function configurarModalCrear() {
    inicializarSelect2('contrato_id_select_id', modalCrearEditar);
    inicializarSelect2('proceso_id_select_id', modalCrearEditar);
    inicializarDatePicker('fecha_inicio_id');
    inicializarDatePicker('fecha_final_id');

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
    agregarValidacionFormularios();
}

let item = [];

function configurarFiltroConsecutivos() {

    let opcionSelect = $("#filtro_consecutivos_select_id");
    let ruta_filtro_consecutivos = $('#ruta_filtro_consecutivos');

    opcionSelect.change(function () {
        window.location = ruta_filtro_consecutivos.val() + opcionSelect.val() + '/index';
    });
}

