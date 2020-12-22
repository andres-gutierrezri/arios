
'use strict';

class DatosRegistro
{
    constructor() {
        this.nombre= '';
        this.tipoIdentificacion= '';
        this.identificacion= '';
        this.correo= '';
        this.celular= '';
    }
    setNombre(nombre) {
       this.nombre = nombre;
    }
    setTipoIdentificacion(tipoIdentificacion) {
       this.tipoIdentificacion = tipoIdentificacion;
    }
    setIdentificacion(identificacion) {
       this.identificacion = identificacion;
    }
    setCorreo(correo) {
       this.correo = correo;
    }
    setCelular(celular) {
       this.celular = celular;
    }
}

$(document).ready(function () {
    configurarFormulario();
});

let datosRegistros = new DatosRegistro();

function configurarFormulario() {
    const form = $('#registro-proveedor-form')[0];
    agregarValidacionForm(form, function (event) {
        datosRegistros.setNombre($('#nombre_id').val());
        datosRegistros.setTipoIdentificacion($('#tipo_identificacion_select_id').val());
        datosRegistros.setIdentificacion($('#identificacion_id').val());
        datosRegistros.setCorreo($('#correo_id').val());
        datosRegistros.setCelular($('#celular_id').val());
        guardarRegistro();
        return true;
    });
}

function guardarRegistro() {
    $.ajax({
            url: "/administracion/proveedor/registro",
            context: document.body,
            type:'POST',
            data:JSON.stringify(datosRegistros),
            contentType: "application/json; charset=utf-8;",
            dataType: "json",
    }).done(function(response) {
        if(response.hasOwnProperty('estado')){
            if (response.estado === 'OK') {
                Swal.fire({
                    title: "Registro Exitoso!",
                    text: `Revise el correo electrónico ${response.datos.correo} para continuar con el proceso`,
                    type: "success",
                    confirmButtonText: "Ir al inicio de sesión",
                    closeOnConfirm: true
                }).then(function () {
                    $(location).attr('href', '/administracion/proveedor/iniciar-sesion');
                })
            }else if (response.estado === 'ERROR') {
                EVANotificacion.modal.error(response.mensaje)
            } else {
                if (response.hasOwnProperty('mensaje'))
                    EVANotificacion.toast.advertencia(response.mensaje);
                else
                    EVANotificacion.toast.error("Error no esperado.");
            }
        }
    }).fail(function () {
        EVANotificacion.toast.error('Falló el registro');
    })
}

function verPoliticaconFidencialidad () {
    $.ajax({
        url: document.location.origin + "/administracion/proveedor/politica-confidencialidad",
        context: document.body
    }).done(function (response) {
        let mTerminosCondiciones = $('#modal_terminos_condiciones')
        mTerminosCondiciones.html(response);
        mTerminosCondiciones.modal('show');
    });
}