'use strict';

const modalCargarSoporte = $('#cargar-soporte');

$(document).ready(function () {
    Dropzone.autoDiscover = false;
    Dropzone.prototype.defaultOptions.dictRemoveFile = "Eliminar";
    activarSelect2();
    configurarFiltroConsecutivos();
});

function abrirModalCargarSoporte(url) {
    cargarAbrirModal(modalCargarSoporte, url, function () {
        configurarModalSoporte();
        let form = $('#soporte_form')[0];
        agregarValidacionForm(form, function (event) {
            const dzSoportes = Dropzone.forElement("#dZUpload");
            dzSoportes.on("sendingmultiple", cargarDatosForm);
            dzSoportes.on("errormultiple", (x, error) => EVANotificacion.toast.error(error));
            dzSoportes.on("successmultiple", () => location.reload());
            dzSoportes.processQueue();
            return true;
        });
    });
}

function cargarDatosForm(file, xhr, formData) {
    $('#soporte_form').serializeArray().forEach(campo => {
        formData.append(campo.name, campo.value);
    })
}
function configurarModalSoporte() {

    const archivo = $('#archivo_mostrar');
    const fechaFinal = $('#fecha_final_mostrar');
    const descripcion = $('#description_mostrar');
    let idEstado = $('#estado_id');
    let agregar = document.querySelector('#agregar');

    inicializarSelect2('estado_select_id', modalCargarSoporte);
    inicializarDatePicker('fecha_final_id');

    const idActividad = $('#id_actividad').val();

    $("#dZUpload").dropzone({
        url: `/gestion-actividades/actividades/actividad/${idActividad}/cargar`,
        autoProcessQueue: false,
        addRemoveLinks: true,
        acceptedFiles: 'image/*,application/pdf',
        preventDuplicates: true,
        forceFallback:false,
        parallelUploads: 30,
        maxFiles: 30,
        uploadMultiple: true,
        timeout:1000 * 60 * 5,  // 5 minutos
    });

    $('input:radio[name=estado]').change(function () {
        idEstado = this.value
        if (idEstado === "2") {
            archivo.hide();
            archivo.removeAttr('required');
            fechaFinal.hide();
            fechaFinal.removeAttr('required');
            descripcion.hide();
            descripcion.removeAttr('required');

        } else if (idEstado === "3") {
            archivo.show();
            archivo.attr('required', true);
            fechaFinal.show();
            fechaFinal.attr('required', true);
            descripcion.show();
            descripcion.attr('required', true);
        }
    });

    agregarValidacionFormularios();
}

