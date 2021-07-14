'use strict';

const modalCargarSoporte = $('#cargar-soporte');

$(document).ready(function () {
    Dropzone.autoDiscover = false;
    Dropzone.prototype.defaultOptions.dictRemoveFile = "Eliminar";
    activarSelect2();
    configurarFiltroConsecutivos();
});

function abrirModalCargarSoporte(url, soporte) {
    cargarAbrirModal(modalCargarSoporte, url, function () {
        configurarModalSoporte(soporte);
        let form = $('#soporte_form')[0];
        agregarValidacionForm(form, function (event) {
            if (soporte === 'True'){
                const dzSoportes = Dropzone.forElement("#dZUpload");
                dzSoportes.on("sendingmultiple", cargarDatosForm);
                dzSoportes.on("errormultiple", (x, error) => EVANotificacion.toast.error(error));
                dzSoportes.on("successmultiple", () => location.reload());
                dzSoportes.processQueue();
                return true;
            }
            else if (soporte === 'False'){
                enviarFormularioAsync(form, url, "cargando").then(exitoso => {
                if (exitoso) {
                    modalCargarSoporte.modal('hide');
                    Swal.clickCancel();
                    setTimeout(function (){
                        location.reload();
                    },1000);
                } else {
                    Swal.clickCancel();
                }
            });
            return true;
            }
        });
    });
}

function cargarDatosForm(file, xhr, formData) {
    $('#soporte_form').serializeArray().forEach(campo => {
        formData.append(campo.name, campo.value);
    })
}
function configurarModalSoporte(soporte) {

    const archivo = $('#archivo_mostrar');
    const fechaFinal = $('#fecha_final_mostrar');
    const descripcion = $('#description_mostrar');
    let agregar = document.querySelector('#agregar');

    inicializarSelect2('estado_select_id', modalCargarSoporte);
    inicializarDatePicker('fecha_final_id');

    const idActividad = $('#id_actividad').val();

    archivo.show();
    archivo.attr('required', true);
    fechaFinal.show();
    fechaFinal.attr('required', true);
    descripcion.show();
    descripcion.attr('required', true);

    if (soporte === 'True') {
        $("#dZUpload").dropzone({
            url: `/gestion-actividades/actividades/actividad/${idActividad}/cargar`,
            autoProcessQueue: false,
            addRemoveLinks: true,
            acceptedFiles: 'image/*,application/pdf,application/msword,application/vnd.ms-excel,' +
                'application/vnd.ms-powerpoint,application/vnd.ms-excel.sheet.macroenabled.12,application/octet-stream,' +
                'image/png,image/jpeg,image/jpeg,application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            preventDuplicates: true,
            forceFallback: false,
            parallelUploads: 30,
            maxFiles: 30,
            uploadMultiple: true,
            timeout: 1000 * 60 * 5,  // 5 minutos
        });
    }

    agregarValidacionFormularios();
}

