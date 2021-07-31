'use strict';
let TipoAsociado = $('#tipo_asociado');
let contratoSelect = $('#contrato_mostrar_id');
let procesoSelect = $('#proceso_mostrar_id');
let contratoSelectID = $('#contrato_id_select_id');
let procesoSelectID = $('#proceso_id_select_id');
let grupoSelectID = $('#grupo_asociado_select_id');

const modalCrearGrupoActividad = $('#crear-grupo-actividad');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
    $('input[type=radio][name=contactview]').change(function () {
        if (this.value == 'grid') {
            $('#js-contacts .card').removeClassPrefix('mb-').addClass('mb-g');
            $('#js-contacts .col-xl-12').removeClassPrefix('col-xl-').addClass('col-xl-4');
            $('#js-contacts .js-expand-btn').addClass('d-none');
            $('#js-contacts .card-body + .card-body').addClass('show');

        } else if (this.value == 'table') {
            $('#js-contacts .card').removeClassPrefix('mb-').addClass('mb-1');
            $('#js-contacts .col-xl-4').removeClassPrefix('col-xl-').addClass('col-xl-12');
            $('#js-contacts .js-expand-btn').removeClass('d-none');
            $('#js-contacts .card-body + .card-body').removeClass('show');
        }

    });

    //initialize filter
    initApp.listFilter($('#js-contacts'), $('#js-filter-contacts'));

    $('#procesos_id_select_id').on('change', function (e) {
        $('#js-filter-contacts').val($(this).select2('data')[0].text).trigger('change');
    });

    $('#contratos_id_select_id').on('change', function (e) {
        let contratosNombre = $(this).select2('data')[0].text.split(' - ');
        $('#js-filter-contacts').val(contratosNombre[0]).trigger('change');
    });

    $('#colaboradores_id_select_id').on('change', function (e) {
         $('#js-filter-contacts').val($(this).select2('data')[0].text).trigger('change');

    });
});

function abrirModalCrearGrupoActividad(url, asociado) {
    cargarAbrirModal(modalCrearGrupoActividad, url, function (){
        configurarModalCrear(asociado);
        let form = $('#grupo_actividad_form')[0];
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

function configurarModalCrear(asociado) {
    TipoAsociado = $('#tipo_asociado');
    contratoSelect = $('#contrato_mostrar_id');
    procesoSelect = $('#proceso_mostrar_id');
    contratoSelectID = $('#contrato_id_select_id');
    procesoSelectID = $('#proceso_id_select_id');
    grupoSelectID = $('#grupo_asociado_select_id');
    let idTipoAsociado = $('#tipo_asociado_id');

    inicializarSelect2('tipo_asociado_select_id', modalCrearGrupoActividad);
    inicializarSelect2('contrato_id_select_id', modalCrearGrupoActividad);
    inicializarSelect2('proceso_id_select_id', modalCrearGrupoActividad);
    inicializarSelect2('grupo_asociado_select_id', modalCrearGrupoActividad);

    //$("input:radio[name=tipo_asociado][value=asociado]").attr('checked', true);

    $('input:radio[name=tipo_asociado]').change(function() {
        mostrarOcultarTipoAsociado(this.value === "1");
    });

    if (asociado){
        idTipoAsociado.val(asociado).trigger("change");
    }

    agregarValidacionFormularios();
}

function mostrarOcultarTipoAsociado(seleccion) {
    if (seleccion){
        mostrarCamposFormulario([contratoSelect, contratoSelectID])
        ocultarCamposFormulario([procesoSelect, procesoSelectID])
    }else{
        mostrarCamposFormulario([procesoSelect, procesoSelectID])
        ocultarCamposFormulario([contratoSelect, contratoSelectID])
    }
}
