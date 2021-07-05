'use strict';

const modalCrearEditar = $('#crear-crequerimiento');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
    $('#tipo_consecutivos_select_id').change(function () {
        window.location = '/gestion-documental/consecutivo-requerimientos/' + this.value + '/index';
    });

    /*const columnDefs = [
        { "targets": [0], "width": '12%' },
        { "targets": [1], "width": '10%' },
        { "targets": [2], "width": '28%' },
        { "targets": [3], "width": '28%' },
        { "targets": [4], "width": '11%' },
        { "targets": [7], "width": '5%' },
        { "targets": [8], "width": '6%' }
    ]*/
    iniciarDataTableN({buscar: false, paginar: false, ordenar: false});
});


function abrirModalCrear(url) {
   // let editar = `se ha ${url.includes("editar") ? "editar" : "crear"} la reserva para la sala de juntas`
    cargarAbrirModal(modalCrearEditar, url,function () {
        configurarModalCrear();
        const form = $("#requerimientos_form")[0];
        agregarValidacionForm(form, function (event) {
            enviarFormularioAsync(form, url).then(exitoso => {
                if (exitoso)
                    modalCrearEditar.modal('hide');
                    Swal.clickCancel();
                    setTimeout(function (){
                        location.reload();
                    },100);
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


