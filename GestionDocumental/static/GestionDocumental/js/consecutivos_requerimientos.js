'use strict';

const modalCrear = $('#crear-crequerimiento');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
    $('#tipo_consecutivos_select_id').change(function () {
        window.location = '/gestion-documental/consecutivo-requerimientos/' + this.value + '/index';
    });

    iniciarDataTableN({buscar: false, paginar:false, ordenar: false});
});


function abrirModalCrear(url) {
   // let editar = `se ha ${url.includes("editar") ? "editar" : "crear"} la reserva para la sala de juntas`
    cargarAbrirModal(modalCrear, url,function () {
        configurarModalCrear();
        const form = $("#requerimientos_form")[0];
        agregarValidacionForm(form, function (event) {
            enviarFormularioAsync(form, url).then(exitoso => {
                if (exitoso)
                    EVANotificacion.toast.exitoso(`Se ha ${url.includes("editar") ? "editado" : "creado"} la consecutivo`);
                    modalCrear.modal('hide');
            });
            return true;
        });
    });
}

function configurarModalCrear() {
    inicializarSelect2('contrato_id_select_id', modalCrear);
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
