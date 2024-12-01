
'use strict';

const divRepresentanteLegal = $( '.representante-legal');
const selectTipoIdentificacion = $('#tipo_identificacion_select_id');
const nombreRazonSocial = $('#nombre_id');
const divFechaConstitucion = $('#div_fecha_constitucion');
const inputFechaConstitucion = $('#fecha_constitucion_id')
const divInicioActividad = $('#div_inicio_actividad');
const inputInicioActividad = $('#fecha_inicio_actividad_id');
const selectTipoPersona = $('#tipo_persona_select_id');

const inputNombreRL = $('#nombre_rl_id');
const selectTipoIdentificacionRL = $('#tipo_identificacion_rl_select_id');
const inputIdentificacionRL = $('#identificacion_rl_id');

const selectRLPais = $('#pais_rl_select_id');
const selectRLDepartamento = $('#departamento_rl_select_id');
const selectRLMunicipio = $('#municipio_rl_select_id');

const selectUbicacionPais = $('#pais_select_id');
const selectUbicacionDepartamento = $('#departamento_select_id');
const selectUbicacionMunicipio = $('#municipio_select_id');

$(document).ready(function () {
    validarTipoPersona();
    validarDV();
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
    validarDV();
});

selectTipoPersona.change(function (){
    validarTipoPersona();
});

function validarDV() {
    const tipoId =$('#tipo_identificacion_select_id option:selected').text();
    actdesInputDV(tipoId.includes('Tributaria'));
}

function validarTipoPersona() {
    if(selectTipoPersona.val() === '1'){
        divRepresentanteLegal.show();
        nombreRazonSocial.prev("label").text('Razón Social');
        nombreRazonSocial.attr('placeholder', 'Ingrese la razón social');
        divFechaConstitucion.show();
        divInicioActividad.hide();
        ocultarCamposFormulario([inputInicioActividad])
        mostrarCamposFormulario([inputFechaConstitucion, inputNombreRL, selectTipoIdentificacionRL,
            inputIdentificacionRL, selectRLPais, selectRLDepartamento, selectRLMunicipio])

    }else{
        divRepresentanteLegal.hide();
        nombreRazonSocial.prev("label").text('Nombre');
        nombreRazonSocial.attr('placeholder', 'Ingrese el nombre')
        divFechaConstitucion.hide();
        divInicioActividad.show();
        mostrarCamposFormulario([inputInicioActividad])
        ocultarCamposFormulario([inputFechaConstitucion, inputNombreRL, selectTipoIdentificacionRL,
            inputIdentificacionRL, selectRLPais, selectRLDepartamento, selectRLMunicipio])
    }
}

function enviarSolicitudProveedor(idProveedor) {
    Swal.fire({
        title: '¿Está seguro de enviar la solicitud?',
        text: "Una vez enviada la solicitud, no podrá seguir editando los campos hasta que sea aprobada o denegada.",
        icon: 'warning',
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

let selectAprobar = $("#Aprobar_id");
let selectRechazar = $("#Denegar_id");
let comentario = $("#comentario_id");
let divComentario = comentario.parent()

function abrir_modal_aprobar_rechazar(url) {
    $('#accion_proveedor').load(url, function (responseText) {
        try {
            if (responseText.includes("<!DOCTYPE html>")) {
                EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                return false;
            }
            $(this).modal('show');
            selectAprobar = $("#Aprobar_id");
            selectRechazar = $("#Denegar_id");
            comentario = $("#comentario_id");
            divComentario = comentario.parent()

            selectAprobar.click(function () {
                if (selectAprobar) {
                    $('.requiredFinal').removeAttr('required', 'true');
                    divComentario.hide()
                    comentario.attr('hidden', 'true');
                    comentario.removeAttr('required', 'true');
                }
            });

            selectRechazar.click(function () {
                if (selectRechazar) {
                    divComentario.show()
                    comentario.removeAttr('hidden', 'true');
                    comentario.attr('required', 'true');
                }
            });
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
        text: "Si modifica su perfil, la información aprobada será la que se encuentre vigente." +
            "Los cambios realizados solo serán validos hasta que envíe la solicitud nuevamente y sea aprobada.",
        icon: 'warning',
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
