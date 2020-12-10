
'use strict';

let divRepresentanteLegal = $( '.representante-legal');
let selectTipoIdentificacion = $('#tipo_identificacion_select_id');
let nombreRazonSocial = $('#nombre_id');
let divFechaConstitucion = $('#div_fecha_constitucion');
let inputFechaConstitucion = $('#fecha_constitucion_id')
let divInicioActividad = $('#div_inicio_actividad');
let inputInicioActividad = $('#fecha_inicio_actividad_id');
let selectTipoPersona = $('#tipo_persona_select_id');

let inputNombreRL = $('#nombre_rl_id');
let selectTipoIdentificacionRL = $('#tipo_identificacion_rl_select_id');
let inputIdentificacionRL = $('#identificacion_rl_id');

let selectRLPais = $('#pais_rl_select_id');
let selectRLDepartamento = $('#departamento_rl_select_id');
let selectRLMunicipio = $('#municipio_rl_select_id');

let selectUbicacionPais = $('#pais_select_id');
let selectUbicacionDepartamento = $('#departamento_select_id');
let selectUbicacionMunicipio = $('#municipio_select_id');

$(document).ready(function () {
    validarTipoPersona();
});

selectRLPais.change(function (){
    cargarDepartamentosDePais(selectRLPais.val(), selectRLDepartamento)
});

selectRLDepartamento.change(function (){
    cargarMunicipiosDeDepartamento(selectRLDepartamento.val(), selectRLMunicipio)
});

selectUbicacionPais.change(function (){
    cargarDepartamentosDePais(selectUbicacionPais.val(), selectUbicacionDepartamento)
});

selectUbicacionDepartamento.change(function (){
    cargarMunicipiosDeDepartamento(selectUbicacionDepartamento.val(), selectUbicacionMunicipio)
});

selectTipoIdentificacion.change(function (){
    const tipoId =$('#tipo_identificacion_select_id option:selected').text();
    actdesInputDV(tipoId.includes('Tributaria'));
});

selectTipoPersona.change(function (){
    validarTipoPersona();
});

function validarTipoPersona() {
    if(selectTipoPersona.val() === '1'){
        divRepresentanteLegal.show();
        nombreRazonSocial.prev("label").text('Razón Social');
        nombreRazonSocial.attr('placeholder', 'Ingrese la razón social');
        divFechaConstitucion.show();
        inputFechaConstitucion.attr('required', 'true');
        inputFechaConstitucion.removeAttr('hidden', 'true')
        divInicioActividad.hide();
        inputInicioActividad.removeAttr('required', 'true')
        inputInicioActividad.attr('hidden', 'true')

        inputNombreRL.attr('required', 'true');
        inputNombreRL.removeAttr('hidden', 'true')
        selectTipoIdentificacionRL.attr('required', 'true');
        selectTipoIdentificacionRL.removeAttr('hidden', 'true')
        inputIdentificacionRL.attr('required', 'true');
        inputIdentificacionRL.removeAttr('hidden', 'true')
        selectRLPais.attr('required', 'true');
        selectRLPais.removeAttr('hidden', 'true')
        selectRLDepartamento.attr('required', 'true');
        selectRLDepartamento.removeAttr('hidden', 'true')
        selectRLMunicipio.attr('required', 'true');
        selectRLMunicipio.removeAttr('hidden', 'true')

        selectRLPais.attr('required', 'true');
        selectRLDepartamento.attr('required', 'true');
        selectRLMunicipio.attr('required', 'true');
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

        inputNombreRL.removeAttr('required', 'true');
        inputNombreRL.attr('hidden', 'true')
        selectTipoIdentificacionRL.removeAttr('required', 'true');
        selectTipoIdentificacionRL.attr('hidden', 'true')
        inputIdentificacionRL.removeAttr('required', 'true');
        inputIdentificacionRL.attr('hidden', 'true')
        selectRLPais.removeAttr('required', 'true');
        selectRLPais.attr('hidden', 'true')
        selectRLDepartamento.removeAttr('required', 'true');
        selectRLDepartamento.attr('hidden', 'true')
        selectRLMunicipio.removeAttr('required', 'true');
        selectRLMunicipio.attr('hidden', 'true')

        selectTipoIdentificacionRL.removeAttr('required', 'true');
        inputIdentificacionRL.removeAttr('required', 'true');

        selectRLPais.removeAttr('required', 'true');
        selectRLDepartamento.removeAttr('required', 'true');
        selectRLMunicipio.removeAttr('required', 'true');
    }
}

function enviarSolicitudProveedor(idProveedor) {
    Swal.fire({
        title: '¿Está seguro de enviar la solicitud?',
        text: "Una vez enviada la solicitud, no podrá seguir editando los campos hasta que sea aprobada o rechazada.",
        type: 'warning',
        showCancelButton: true,
        confirmButtonText: '¡Sí, Enviar!',
        cancelButtonText: 'Cancelar'
    }).then(result => {
        if (result.value) {
            $.ajax({
                url: "/administracion/proveedor/solicitudes/" + idProveedor + "/enviar",
                type: 'POST',
                context: document.body,
                success: function (data) {
                    if(data.estado === "OK") {
                        location.reload();
                    }else if(data.estado === "ERROR"){
                        EVANotificacion.toast.error(data.mensaje);
                    }
                },
                failure: function (errMsg) {
                    location.reload();
                }
            });
        }
    });
}

function abrir_modal_aprobar_rechazar(url) {
    $('#accion_proveedor').load(url, function (responseText) {
        try {
            if (responseText.includes("<!DOCTYPE html>")) {
                EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                return false;
            }
            $(this).modal('show');
            agregarValidacionFormularios();
        } catch (err) {
            console.log(err);
            EVANotificacion.toast.error('Ha ocurrido un error al cargar el archivo');
        }
    });
}

function modificarPerfilProveedor(idProveedor) {
    Swal.fire({
        title: '¿Está seguro de modificar su perfil?',
        text: "Si modifica su perfil, dejará de estar activo como proveedor hasta que envie la solicitud y sea aprobada nuevamente.",
        type: 'warning',
        showCancelButton: true,
        confirmButtonText: '¡Sí, Continuar!',
        cancelButtonText: 'Cancelar'
    }).then(result => {
        if (result.value) {
            $.ajax({
                url: "/administracion/proveedor/solicitudes/" + idProveedor + "/modificar",
                type: 'POST',
                context: document.body,
                success: function (data) {
                    if(data.estado === "OK") {
                        location.reload();
                    }else if(data.estado === "ERROR"){
                        EVANotificacion.toast.error(data.mensaje);
                    }
                },
                failure: function (errMsg) {
                    location.reload();
                }
            });
        }
    });
}

function actdesInputDV(activar) {
    let divIdentificacion = $('#identificacion_id').parent();
    const inputDV = $('#digito_verificacion_id');
    if(activar) {
        divIdentificacion.removeClass('col-xl-4 col-lg-4 col-md-6 col-sm-6');
        divIdentificacion.addClass('col-xl-3 col-lg-3 col-md-4 col-sm-4');
        inputDV.parent().show();
        inputDV.removeAttr('hidden', 'true');
        inputDV.attr('required', 'true');
    } else {

        if (inputDV !== undefined && inputDV != null) {
            inputDV.parent().hide();
            inputDV.attr('hidden', 'true');
            inputDV.removeAttr('required', 'true');
            divIdentificacion.removeClass('col-xl-3 col-lg-3 col-md-4 col-sm-4');
            divIdentificacion.addClass('col-xl-4 col-lg-4 col-md-6 col-sm-6');
        }
    }
}