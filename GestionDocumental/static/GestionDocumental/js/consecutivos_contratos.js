'use strict';
let extraTiposContrato = $('#extra_tipos_contrato');
let fechaInicioID = $('#fecha_inicio_id');
let fechaFinalID = $('#fecha_final_id');
let colaboradorSelect = $('#colaborador_mostrar_id');
let terceroSelect = $('#tercero_mostrar_id');
let colaboradorSelectID = $('#colaborador_select_id');
let terceroSelectID = $('#tercero_select_id');
let fechaFinal = $('#fecha_final_mostrar');

const modalCrear = $('#crear');
const modalCargar = $('#cargar');

$(document).ready(function () {
    activarSelect2();
    $('#tipo_consecutivos_select_id').change(function () {
        window.location = '/gestion-documental/consecutivo-contratos/' + this.value + '/index';
    });

    const columnDefs = [
        { "targets": [0], "width": '18%' },
        { "targets": [1], "width": '17%' },
        { "targets": [3], "width": '10%' },
        { "targets": [4], "width": '10%' },
        { "targets": [5], "width": '25%' },
        { "targets": [6], "width": '12%' },
        { "targets": [7], "width": '4%' },
        { "targets": [8], "width": '4%' }
    ]
    iniciarDataTableN({buscar: false, paginar: false, ordenar: false, detallesColumnas: columnDefs});
});

function abrirModalCargar(url) {
    cargarAbrirModal(modalCargar, url, configurarModalCargar);
}

function abrirModalCrear(url) {
    cargarAbrirModal(modalCrear, url, configurarModalCrear);
}

function configurarModalCrear() {
    extraTiposContrato = $('#extra_tipos_contrato');
    fechaInicioID = $('#fecha_inicio_id');
    fechaFinalID = $('#fecha_final_id');
    colaboradorSelect = $('#colaborador_mostrar_id');
    terceroSelect = $('#tercero_mostrar_id');
    colaboradorSelectID = $('#colaborador_select_id');
    terceroSelectID = $('#tercero_select_id');
    let idTipoContrato = $('#tipo_contrato_select_id').val();

    fechaFinal = $('#fecha_final_mostrar');

    inicializarDatePicker('fecha_final_id');
    inicializarDatePicker('fecha_inicio_id');
    inicializarSelect2('tipo_contrato_select_id', modalCrear);
    inicializarSelect2('colaborador_select_id', modalCrear);
    inicializarSelect2('tercero_select_id', modalCrear);

    if (idTipoContrato === ""){
        $('#tipo_contrato_select_id').change(function () {
            let actual = this.value;
            CambiarSelect(actual);
            if (actual === ""){
                 fechaFinal.show();
                 fechaFinalID.attr("required", true);
            }
        })
    }
    else{
        CambiarSelect(idTipoContrato);
        $('#tipo_contrato_select_id').change(function () {
            let actual = this.value;
            CambiarSelect(actual);
            if (actual === ""){
                 fechaFinal.show();
                 fechaFinalID.attr("required", true);
            }
        })
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

    agregarValidacionFormularios();
}

function configurarModalCargar() {
    $('#archivo_id').change(function (e) {
        let label_input = $('.custom-file-label');
        let extension = e.target.files[0].name.split('.').pop();
        if (extension === 'pdf' || extension === 'xlsx' || extension === 'docx' || extension === 'pptx'){
            label_input.html(e.target.files[0].name);
        }else{
            label_input.html('Seleccione un archivo');
            e.target.value = '';
            EVANotificacion.toast.error('El archivo ingresado no tiene un formato compatible. ' +
                                        '(Formatos Aceptados: PDF, Documento de Word, Documento de Excel, ' +
                                        'Presentacion de Power Point');
            return false;
        }
    });
    agregarValidacionFormularios();
}

function CambiarSelect (actual){
    $.each(jQuery.parseJSON(extraTiposContrato.val()), function(key, value) {
        if(actual == value.id){
            if (value.laboral){
                mostrarOcultarColaboradorTerceroTipoContrato(true)
            }else{
                mostrarOcultarColaboradorTerceroTipoContrato(false)
            }
            if(value.fecha_fin){
                fechaFinal.show();
                fechaFinalID.attr("required", true);
            }else{
                fechaFinal.hide();
                fechaFinalID.removeAttr("required", true);
            }
        }
    });
    if (actual === ""){
         fechaFinal.show();
         fechaFinalID.attr("required", true);
         mostrarOcultarColaboradorTercero("ninguno")
    }
}

function mostrarOcultarColaboradorTerceroTipoContrato(laboral) {
    if (laboral){
        colaboradorSelect.show();
        colaboradorSelectID.attr("required", true);
        terceroSelect.hide();
        terceroSelectID.removeAttr('required', true);
    }else{
        terceroSelect.show();
        terceroSelectID.attr("required", true);
        colaboradorSelect.hide();
        colaboradorSelectID.removeAttr('required', true);
    }
}
