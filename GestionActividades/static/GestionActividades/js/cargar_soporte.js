'use strict';

const modalCargarSoporte = $('#cargar-soporte');

$(document).ready(function () {
    activarSelect2();
    configurarFiltroConsecutivos();
});

function abrirModalCargarSoporte(url) {
    cargarAbrirModal(modalCargarSoporte, url, function () {
        configurarModalSoporte();
        let form = $('#soporte_form')[0];
        agregarValidacionForm(form, function (event) {
            //myDropzone.processQueue();
            Dropzone.forElement("#dZUpload").processQueue();
            enviarFormularioAsync(form, url, "cargando").then(exitoso => {
                if (exitoso) {
                    EVANotificacion.toast.exitoso(`Se ha ${url.includes("editar") ? "editado" : "cargado"} el soporte`);
                    modalCargarSoporte.modal('hide');
                    Swal.clickCancel();
                    setTimeout(function () {
                        location.reload();
                    }, 1000);
                } else {
                    Swal.clickCancel();
                }
            });
            return true;
        });
    });
}

function configurarModalSoporte() {

    const archivo = $('#archivo_mostrar');
    const fechaFinal = $('#fecha_final_mostrar');
    const descripcion = $('#description_mostrar');
    let idEstado = $('#estado_id');
    let agregar = document.querySelector('#agregar');

    inicializarSelect2('estado_select_id', modalCargarSoporte);
    inicializarDatePicker('fecha_final_id');
    const token = {csrfmiddlewaretoken: $('#soporte_form')[0]['csrfmiddlewaretoken'].value};
    Dropzone.autoDiscover = false;
    Dropzone.prototype.defaultOptions.dictRemoveFile = "Eliminar";
    $("#dZUpload").dropzone({
        url: `/gestion-actividades/actividades/actividad/13/cargar-archivo`,
        autoProcessQueue: false,
        addRemoveLinks: true,
        acceptedFiles: 'image/*,application/pdf',
        preventDuplicates: true,
        forceFallback:false,
        params: token,
        parallelUploads: false,
        init: initDZ,
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

function initDZ() {
    let myDropzone = this;
    console.log(myDropzone);
    myDropzone.on("addedfile", function (file) {
        console.log("Added file.");
        console.log(file);
    });
    myDropzone.on("removedfile", function (file) {
        console.log("removed file.");
        console.log(file);
    });
}
