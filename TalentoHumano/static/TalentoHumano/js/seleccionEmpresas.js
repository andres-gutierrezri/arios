
'use strict';

let lista_empresas = [];

function seleccionarEmpresas(usuario) {
    let ruta = document.location.origin + "/talento-humano/colaboradores/seleccion-empresas/" + usuario;
    $('#mSeleccionEmpresas').load(ruta, function () {
        try {
            $(this).modal('show');
            JSON.parse($('#empresas_seleccionadas').val()).forEach(function (item) {
                 adicionarSeleccionEmpresa(item);
            });
        } catch (err) {
            console.log(err);
            EVANotificacion.toast.error('Ha ocurrido un error guardar las selecciones');
        }
    });
}

function adicionarSeleccionEmpresa(idEmpresa) {
    let coincidencia = false;
    let divEmpresa = $('#div_empresa_'+ idEmpresa);
    lista_empresas.forEach(function (item, pos) {
        if (item === idEmpresa){
            coincidencia = true;
            lista_empresas.splice(pos, 1);
            divEmpresa.css('opacity','0.5')
        }
    });
    if (!coincidencia) {
        lista_empresas.push(idEmpresa);
        divEmpresa.css('opacity','1')
    }
    $('#empresas_seleccionadas').val(lista_empresas);
}