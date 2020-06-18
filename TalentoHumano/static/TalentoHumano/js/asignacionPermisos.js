function guardarAsignacionesPermisos() {
    let valoresPermisos = $('#valores_permisos');
    let listaPermisos = [];

    let datosPermisos = JSON.parse($('#datos_permisos').val());

    datosPermisos.forEach( function(valor) {
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
            listaPermisos.push({'funcionalidad': valor.funcionalidad, 'permiso': permisos});
        }
    });
    valoresPermisos.val(JSON.stringify(listaPermisos));
    $("#asignacion-permisos-form").submit();
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