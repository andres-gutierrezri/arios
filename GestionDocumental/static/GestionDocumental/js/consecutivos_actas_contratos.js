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
    inicializarSelect2('consecutivo_contrato_id_select_id', modalCrearEditar);
    inicializarSelect2('tipo_acta_id_select_id', modalCrearEditar);
    inicializarDatePicker('fecha_suspension_id');
    inicializarDatePicker('fecha_reinicio_id');


    if ($('#tipo_acta_id_select_id').val() === "1"){
        $('#fecha_suspension_mostrar').hide();
        $('#fecha_suspension_id').attr("required", false);
        $('#fecha_reinicio_id').attr("required", true);
    }
    else{
        $('#fecha_reinicio_id').attr("required", false);
    }
     $('#tipo_acta_id_select_id').change(function () {
    let idActa = this.value;
        if (idActa === "0" || idActa === "2"){
            $('#fecha_suspension_mostrar').show();
            $('#fecha_suspension_id').attr("required", true);
            $('#fecha_reinicio_id').attr("required", false);
        }else{
            $('#fecha_suspension_mostrar').hide();
            $('#fecha_suspension_id').attr("required", false);
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


