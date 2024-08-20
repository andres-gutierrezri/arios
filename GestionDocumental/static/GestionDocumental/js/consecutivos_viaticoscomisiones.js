'use strict';

const modalCrearEditar = $('#crear-editar-consecutivo');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
    const columnDefs = [
        { "targets": [0], "width": '17%' },
        { "targets": [1], "width": '12%' },
        { "targets": [2], "width": '28%' },
        { "targets": [3], "width": '23%' },
        { "targets": [4], "width": '11%' },
        { "targets": [6], "width": '5%' },
        { "targets": [7], "width": '6%' }
    ]
    iniciarDataTableN({buscar: false, paginar: false, ordenar: false, detallesColumnas: columnDefs});
});


function abrirModalCrear(url) {
    cargarAbrirModal(modalCrearEditar, url,function () {
        configurarModalCrear();
        const form = $("#viaticoscomisiones_form")[0];
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


