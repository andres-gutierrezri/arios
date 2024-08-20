
'use strict';

class DatosRegistro
{
    constructor() {
        this.nombre= '';
        this.tipoIdentificacion= '';
        this.identificacion= '';
        this.digitoVerificacion= '';
        this.correo= '';
        this.celular= '';
        this.tokenRecaptcha = '';
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
    setDigitoVerificacion(digitoVerificacion) {
       this.digitoVerificacion = digitoVerificacion;
    }
    setCorreo(correo) {
       this.correo = correo;
    }
    setCelular(celular) {
       this.celular = celular;
    }
    setTokenRecaptcha(tokenRecaptcha) {
       this.tokenRecaptcha = tokenRecaptcha;
    }
}

let datosRegistros = new DatosRegistro();
const formRegistro = $('#registro-proveedor-form')[0];

function enviarFormulario(tokenRecaptcha) {
    if(formRegistro.checkValidity())
    {
        datosRegistros.setNombre($('#nombre_id').val());
        datosRegistros.setTipoIdentificacion($('#tipo_identificacion_select_id').val());
        datosRegistros.setIdentificacion($('#identificacion_id').val());
        datosRegistros.setDigitoVerificacion($('#digito_verificacion_id').val());
        datosRegistros.setCorreo($('#correo_id').val());
        datosRegistros.setCelular($('#celular_id').val());
        datosRegistros.setTokenRecaptcha(tokenRecaptcha);
        guardarRegistro();
        return true;
    } else {
        formRegistro.classList.add('was-validated');
        resetRecaptcha();
    }
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
        resetRecaptcha();
        if(response.hasOwnProperty('estado')){
            if (response.estado === 'OK') {
                EVANotificacion.modal
                    .confirmacionBotonMensaje("Registro Exitoso!",
                    `Revise el correo electrónico ${response.datos.correo} para continuar con el proceso`,
                    "Ir al inicio de sesión", '/administracion/proveedor/iniciar-sesion')
            }else if (response.estado === 'ERROR') {
                EVANotificacion.modal.error(response.mensaje);
            } else {
                if (response.hasOwnProperty('mensaje'))
                    EVANotificacion.toast.advertencia(response.mensaje);
                else
                    EVANotificacion.toast.error("Error no esperado.");
            }
        }
    }).fail(function () {
        resetRecaptcha();
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
