'use strict';

const modalCrearEditar = $('#crear-editar-consecutivo');
let tipoActa = $('#tipo_acta_id_select_id');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
    const columnDefs = [
        { "targets": [0], "width": '20%' },
        { "targets": [1], "width": '12%' },
        { "targets": [2], "width": '12%' },
        { "targets": [3], "width": '31%' },
        { "targets": [4], "width": '10%' },
        { "targets": [7], "width": '8%' },
        { "targets": [8], "width": '7%' }
    ]
    iniciarDataTableN({buscar: false, paginar: false, ordenar: false, detallesColumnas: columnDefs});
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
    inicializarSelect2('consecutivo_contrato_id_select_id', modalCrearEditar);
    inicializarSelect2('tipo_acta_id_select_id', modalCrearEditar);
    inicializarDatePicker('fecha_suspension_id');
    inicializarDatePicker('fecha_reinicio_id');


    if ($('#tipo_acta_id_select_id').val() === "2"){
        ocultarCamposFormulario([$("#fecha_suspension_mostrar")])
        $('#fecha_reinicio_id').attr("required", true);
    }
    else{
        $('#fecha_reinicio_id').attr("required", false);
    }
     $('#tipo_acta_id_select_id').change(function () {
    let idActa = this.value;
        if (idActa === "1" || idActa === "3"){
            $('#fecha_reinicio_id').attr("required", false);
            mostrarCamposFormulario([$("#fecha_suspension_mostrar")])

        }else{
            ocultarCamposFormulario([$("#fecha_suspension_mostrar")])
        }
    });
    agregarValidacionFormularios();
}



function configurarFiltroConsecutivos() {

    let opcionSelect = $("#filtro_consecutivos_select_id");
    let ruta_filtro_consecutivos = $('#ruta_filtro_consecutivos');

    opcionSelect.change(function () {
        window.location = ruta_filtro_consecutivos.val() + opcionSelect.val() +'/index';
    });

}


