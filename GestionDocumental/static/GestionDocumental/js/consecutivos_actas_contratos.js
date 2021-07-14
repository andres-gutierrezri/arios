'use strict';

const modalCrearEditar = $('#crear-editar-consecutivo');
let tipoActa = $('#tipo_acta_id_select_id');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
    iniciarDataTableN({buscar: false, paginar: false, ordenar: false});
});

function abrirModalCrear(url) {
    cargarAbrirModal(modalCrearEditar, url,function () {
        configurarModalCrear();
        const form = $("#actascontratos_form")[0];
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
    inicializarSelect2('tipo_acta_id_select_id');
    agregarValidacionFormularios();
}

let item = [];

function configurarFiltroConsecutivos() {

    let opcionSelect = $("#filtro_consecutivos_select_id");
    let ruta_filtro_consecutivos = $('#ruta_filtro_consecutivos');

    opcionSelect.change(function () {
        window.location = ruta_filtro_consecutivos.val() + opcionSelect.val() +'/index';
    });

}


