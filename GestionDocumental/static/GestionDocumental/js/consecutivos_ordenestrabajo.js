'use strict';

const modalCrearEditar = $('#crear-editar-consecutivo');
let fechaInicioID = $('#fecha_inicio_id');
let fechaFinalID = $('#fecha_final_id');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
     const columnDefs = [
        { "targets": [0], "width": '16%' },
        { "targets": [1], "width": '8%' },
        { "targets": [2], "width": '8%' },
        { "targets": [3], "width": '26%' },
        { "targets": [4], "width": '20%' },
        { "targets": [5], "width": '9%' },
        { "targets": [8], "width": '5%' },
        { "targets": [9], "width": '8%' }
    ]
    iniciarDataTableN({buscar: false, paginar: false, ordenar: false, detallesColumnas: columnDefs});
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
    $('#fecha_final_id').attr("required", false);

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


