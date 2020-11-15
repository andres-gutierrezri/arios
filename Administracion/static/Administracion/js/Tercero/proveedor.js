
'use strict';

let divRepresentanteLegal = $( '.representante-legal');
let selectTipoIdentificacion = $('#tipo_identificacion_select_id');
let nombreRazonSocial = $('#nombre_id');
let divFechaConstitucion = $('#div_fecha_constitucion');
let inputFechaConstitucion = $('#fecha_constitucion_id')
let divInicioActividad = $('#div_inicio_actividad');
let inputInicioActividad = $('#fecha_inicio_actividad_id')

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
    validarTipoIdentificacion();
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

selectTipoIdentificacion.change(
    validarTipoIdentificacion()
);

function validarTipoIdentificacion() {
    let tiposIdentificacion = JSON.parse($('#json_tipo_identificacion').val());
    tiposIdentificacion.forEach(function (obj) {
        if(parseInt(obj.id) === parseInt(selectTipoIdentificacion.val())){
            if (obj.tipo_nit === true){
                divRepresentanteLegal.show();
                nombreRazonSocial.prev("label").text('Razón Social');
                nombreRazonSocial.attr('placeholder', 'Ingrese la razón social');
                divFechaConstitucion.show();
                inputFechaConstitucion.attr('required', 'true');
                inputFechaConstitucion.removeAttr('hidden', 'true')
                divInicioActividad.hide();
                inputInicioActividad.removeAttr('required', 'true')
                inputInicioActividad.attr('hidden', 'true')
                return false;
            }
        }else{
            divRepresentanteLegal.hide();
            nombreRazonSocial.prev("label").text('Nombre');
            nombreRazonSocial.attr('placeholder', 'Ingrese el nombre')
            divFechaConstitucion.hide();
            inputFechaConstitucion.removeAttr('required', 'true');
            inputFechaConstitucion.attr('hidden', 'true')
            divInicioActividad.show();
            inputInicioActividad.attr('required', 'true')
            inputInicioActividad.removeAttr('hidden', 'true')
        }
    });
}