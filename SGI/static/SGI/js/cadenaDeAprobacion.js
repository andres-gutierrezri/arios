let valores_selectores = $('#valores_selectores').val() ? JSON.parse($('#valores_selectores').val()) : null;
let contenedor = $('#contenedor_selectores');
let contador = valores_selectores ? valores_selectores['contador'] : null;
let selecciones = [];
let usuarios_seleccionados = $('#usuarios_seleccionados');

$(function () {
    if (valores_selectores) {
        let temp = contador;
        if (valores_selectores.opcion === 'editar') {
            let orden = 1, orden_anteior;
            while (orden <= temp) {
                $("#agregar_" + (orden - 1)).hide();
                $("#eliminar_" + (orden - 1)).hide();
                valores_selectores.selecciones.forEach(function (item) {
                    (item.orden === orden ? contenedor.append(crearSelectores(item.orden, item.usuario_id))
                        & selecciones.push(item.usuario_id) : null);
                    (orden === 1 ? $("#eliminar_" + (orden)).hide() : null);
                });
                orden++;
            }
            orden_anterior = orden - 1;
            (orden > valores_selectores.colaboradores.length ? $("#agregar_" + (orden_anterior)).hide() : null);
            $('#colaborador_id_' + orden_anterior).removeAttr('disabled', true);
            usuarios_seleccionados.val(selecciones.pop());
        } else {
            while (temp > 0) {
                contenedor.append(crearSelectores(temp));
                temp--;
            }
            $("#eliminar_1").hide();
        }
    }
});

let agregar = function () {
    let selector = $('#colaborador_id_' + contador);
    $("#agregar_" + (contador)).hide();
    $("#eliminar_" + (contador)).hide();
    selecciones.push(selector.val());
    selector.attr('disabled', true);
    (valores_selectores.colaboradores.length > contador ? contador++ & contenedor.append(crearSelectores(contador)) : null);
    (valores_selectores.colaboradores.length - contador === 0 ? $("#agregar_" + (contador)).hide() : null);
    $('.select2').select2();
    usuarios_seleccionados.val(selecciones);
};

let eliminar = function (id) {
    contador--;
    selecciones.pop();
    $("#elemento_" + id).remove();
    $("#agregar_" + (contador)).show();
    (contador !== 1 ? $("#eliminar_" + (contador)).show() : null);
    $('#colaborador_id_' + contador).removeAttr('disabled', true);
    usuarios_seleccionados.val(selecciones);
};

let crearSelectores = function (posicion, usuario_id) {
    let desactivar = usuario_id ? 'disabled="disabled"' : '';
    return `<div class="form-group" id="elemento_${posicion}">
    <div class="form-row">
        <div class="col-md-11">
            <label for="colaborador_id_${posicion}">Usuario ${posicion} </label>
            <select class="select2 form-control" ${desactivar} name="ultimo_usuario" id="colaborador_id_${posicion}"> 
                ${crearOpciones(usuario_id)}
            </select>
        </div>
        <div class="col-md-1" style="padding-top:30px" id="botones_${posicion}">
            <a class="far fa-2x far fa-plus" id="agregar_${posicion}" href="#" onclick="agregar()" title="" data-original-title="Agregar Usuario"></a>
            <a class="far fa-2x far fa-times" id="eliminar_${posicion}" href="#" onclick="eliminar(${posicion})" title="" data-original-title="Eliminar Usuario"></a>
        </div>
    </div></div>`;
};

let crearOpciones = function (usuario_id) {
    let opciones_colaborador = '';
    if (valores_selectores) {
        valores_selectores['colaboradores'].forEach(function (usuario) {
            let existe = false;
            selecciones.forEach(function (id) {
                existe = usuario['campo_valor'].toString() === id.toString() ? true : existe;
            });
            (existe ? null :
                opciones_colaborador += optionSelect((usuario_id === usuario.campo_valor ? 'selected ' : ''), usuario.campo_valor, usuario.campo_texto));
        });
        return opciones_colaborador;
    } else {
        return '';
    }
};

let optionSelect = function (seleccionar, valor, texto) {
    return `<option ${seleccionar} value="${valor}">${texto}</option>`;
};
