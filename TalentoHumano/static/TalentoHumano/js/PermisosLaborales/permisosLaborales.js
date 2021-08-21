'use strict';

const modalCrearPermiso = $('#crear-permiso');

$(document).ready(function () {
    let selectTipoPermiso = $('#tipo_permisos_select_id');

    const columnDefs = [
        {"targets": [0], "width": '15%'},
        {"targets": [1], "width": '17%'},
        {"targets": [2], "width": '19%'},
        {"targets": [3], "width": '7%'},
        {"targets": [4], "width": '7%'},
        {"targets": [5], "width": '7%'},
        {"targets": [6], "width": '7%'},
        {"targets": [7], "width": '4%'},
        {"targets": [8], "width": '4%'}
    ]

    activarSelect2();

    iniciarDataTableN({
        buscar: false,
        paginar: false,
        ordenar: true,
        ordenInicial: [[0, 'desc']],
        detallesColumnas: columnDefs
    });

    selectTipoPermiso.change(function () {
        window.location = '/talento-humano/permisos-laborales/' + this.value + '/index';
    });
});

function abrirModalCrear(url, fechaStart = moment().format('YYYY-MM-DD HH:mm:ss'), fechaEnd = moment().add(1, 'd').format('YYYY-MM-DD HH:mm:ss')) {
    cargarAbrirModal(modalCrearPermiso, url, function () {
        configurarModalCrear(fechaStart, fechaEnd);
    });
}

function configurarModalCrear(fechaStart, fechaEnd) {
    let soporte = $('#archivo_id');
    let mensaje = $("#mensaje_soporte");
    let fechas = $('#fecha_intervalo_id');

    let idTipoPermiso = $('#tipo_permiso_select_id');
    let idTipoPermisoOtro = $('#tipo_permiso_otro_id');
    let tipoPermisoOtroMostrar = $('#tipo_permiso_otro_mostrar');

    let valorTipoPermiso = idTipoPermiso.val();
    let formEditarPermisoLaboral = $('#permiso_laboral_form_editar');

    inicializarSelect2('tipo_permiso_select_id', modalCrearPermiso);
    inicializarDateRangePicker('fecha_intervalo_id');

    if (idTipoPermiso.val() !== "7") {
        ocultarCamposFormulario([tipoPermisoOtroMostrar, idTipoPermisoOtro]);
    }

    idTipoPermiso.change(function () {
        let actual = this.value;
        if (actual === "7") {
            mensaje.html("");
            soporte.removeAttr('required');
            mostrarCamposFormulario([tipoPermisoOtroMostrar, idTipoPermisoOtro]);
        } else {
            ocultarCamposFormulario([tipoPermisoOtroMostrar, idTipoPermisoOtro]);
            if (actual === "2" || actual === "4" || actual === "5" || actual === "6") {
                if (formEditarPermisoLaboral.val() === "" && valorTipoPermiso === actual) {
                    mensaje.html("");
                    soporte.removeAttr('required');
                } else {
                    mensaje.html("Debe adjuntar documento soporte");
                    soporte.attr('required', true);
                    soporte.focus();
                }
            } else {
                mensaje.html("");
                soporte.removeAttr('required');
            }
        }
    });

    fechas.data('daterangepicker').minDate = false;
    fechas.data('daterangepicker').setStartDate(fechaStart);
    fechas.data('daterangepicker').setEndDate(fechaEnd);

    soporte.change(function (e) {
        let label_input = $('.custom-file-label');
        let extension = e.target.files[0].name.split('.').pop();
        if (extension === 'pdf' || extension === 'doc' || extension === 'docx' || extension === 'jpeg' ||
            extension === 'jpg' || extension === 'png' || extension === 'gif') {
            label_input.html(e.target.files[0].name);
        } else {
            label_input.html('Seleccione un archivo');
            e.target.value = '';
            EVANotificacion.toast.error('El archivo ingresado no tiene un formato compatible. ' +
                '(Formatos Aceptados: PDF, Documento Word o Imagen)');
            return false;
        }
    });
    agregarValidacionFormularios();
}
