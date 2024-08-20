'use strict';

$(document).ready(function () {
    $('.select2').select2();

    $('#filtro_ct_select_id').change(function () {
        let idUsuario = $('#id_usuario').val();
        window.location = '/talento-humano/colaboradores/' + idUsuario + '/permisos/' + this.value;
    });

    let inputFiltro = $('#js-filter-permisos');
    let listaFiltrar = $('#js-permisos');
    let labelsFuncionalidad = $('.label-funcionalidad');

    initApp.listFilter(listaFiltrar, inputFiltro);

    inputFiltro.change(function () {
        if (inputFiltro.val() !== ''){
            labelsFuncionalidad.hide();
        }else{
            labelsFuncionalidad.show();
        }
    })
});

function guardarAsignacionesPermisos() {
    let valoresPermisos = $('#valores_permisos');
    let listaPermisos = [];

    let datosPermisos = JSON.parse($('#datos_permisos').val());

    datosPermisos.forEach( function(valor) {
        if (valor.tipo_funcionalidad === true) {
            let idFuncionalidad = 'permiso_'+ valor.funcionalidad + '_id';
            if ($('#' + idFuncionalidad).prop('checked')){

                    let permisos = [];
                    let pos = 1;

                    while (pos <= 4) {
                        if ($('#accion_' + pos + '_' + idFuncionalidad).prop('checked')) {
                            permisos.push(pos)
                        }
                        pos += 1;
                    }
                    listaPermisos.push({'tipo_funcionalidad': true,'funcionalidad': valor.funcionalidad, 'permiso': permisos});
            }
        }else{
            let idFuncionalidad = 'grupo_'+ valor.grupo + '_id';
            if ($('#' + idFuncionalidad).prop('checked')) {
                listaPermisos.push({'tipo_funcionalidad': false, 'grupo': valor.grupo});
            }
        }
    });
    let enviar_form = $('#btn_enviar');
    let id_usuario = $('#id_usuario');
    if (listaPermisos.length === 0 && id_usuario.val() === undefined){
        EVANotificacion.toast.error('No se han seleccionado permisos');
        return false;
    }
    valoresPermisos.val(JSON.stringify(listaPermisos));
    enviar_form.click();
}

function activarFuncionalidad(id) {
    let funcionalidad = $('#' + id);

    if (funcionalidad.prop('checked')){
        let x = 1;
        while (x <= 4) {
            let item = $('#accion_' + x + '_' + id);
            item.prop("checked", true);
            item.prop("disabled", false);
            x += 1;
        }
    }else {
        let x = 1;
        while (x <= 4) {
            let item = $('#accion_' + x + '_' + id);
            item.prop("checked", false);
            item.prop("disabled", true);
            x += 1;
        }
    }
}