'use strict';

let contenedorSelectores = $('#valores_selectores');
let valorSelectores = contenedorSelectores.val() ? JSON.parse(contenedorSelectores.val()) : null;
let contenedor = $('#contenedor_selectores');
let contador = valorSelectores ? valorSelectores['contador'] : 0;
let selecciones = [];
let usuariosSeleccionados = $('#usuarios_seleccionados');

function crearIdCompuesto(texto, numero) {
    return $("#" + texto + '_' + (numero));
}

$(function () {
    if (valorSelectores) {
        let temp = contador;
        if (valorSelectores.opcion === 'editar') {
            let orden = 1, ordenAnterior;
            while (orden <= temp) {
                crearIdCompuesto('agregar', (orden - 1)).hide();
                crearIdCompuesto('eliminar', (orden - 1)).hide();
                valorSelectores.selecciones.forEach(function (item) {
                    if (item.orden === orden) {
                        contenedor.append(crearSelectores(item.orden, item.usuario_id));
                        selecciones.push(item.usuario_id);
                    }
                    if (orden === 1) {
                        crearIdCompuesto('eliminar', orden).hide();
                    }
                });
                orden++;
            }
            ordenAnterior = orden - 1;

            if (orden > valorSelectores.colaboradores.length)
                crearIdCompuesto('agregar', ordenAnterior).hide();

            crearIdCompuesto('usuario_id', ordenAnterior).removeAttr('disabled', true);
            selecciones.pop();
            usuariosSeleccionados.val(selecciones);
        } else {
            while (temp > 0) {
                contenedor.append(crearSelectores(temp));
                temp--;
            }
            crearIdCompuesto('eliminar', 1).hide();
        }
    }
});

let agregar = function () {
    let selector = crearIdCompuesto('usuario_id', contador);

    crearIdCompuesto('agregar', contador).hide();
    crearIdCompuesto('eliminar', contador).hide();
    selecciones.push(selector.val());
    selector.attr('disabled', true);

    if (valorSelectores.colaboradores.length > contador) {
        contador++;
        contenedor.append(crearSelectores(contador));
    }

    if (valorSelectores.colaboradores.length - contador === 0)
        crearIdCompuesto('agregar', contador).hide();

    $('.select2').select2();
    usuariosSeleccionados.val(selecciones);
};

let eliminar = function (id) {
    contador--;
    selecciones.pop();
    crearIdCompuesto('elemento', id).remove();
    crearIdCompuesto('agregar', contador).show();
    if (contador !== 1)
        crearIdCompuesto('eliminar', (contador)).show();

    crearIdCompuesto('usuario_id', contador).removeAttr('disabled', true);
    usuariosSeleccionados.val(selecciones);
};

let crearSelectores = function (posicion, usuario_id) {
    let desactivar = usuario_id ? 'disabled="disabled"' : '';
    return `<div class="form-group" id="elemento_${posicion}">
    <div class="form-row">
        <div class="col-md-11">
            <label for="usuario_id_${posicion}">Usuario ${posicion} </label>
            <select class="select2 form-control" ${desactivar} name="ultimo_usuario" id="usuario_id_${posicion}"> 
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
    let opcionesColaborador = '';
    if (valorSelectores) {
        valorSelectores['colaboradores'].forEach(function (colaborador) {
            let existe = false;
            selecciones.forEach(function (id) {
                existe = colaborador['id_usuario'].toString() === id.toString() ? true : existe;
            });
            if (!existe) {
                opcionesColaborador += optionSelect((usuario_id === colaborador.id_usuario ? 'selected ' : ''),
                    colaborador.id_usuario, colaborador.nombre + ' ' + colaborador.apellido)
            }
        });
        return opcionesColaborador;
    } else {
        return '';
    }
};

let optionSelect = function (seleccionar, valor, texto) {
    return `<option ${seleccionar} value="${valor}">${texto}</option>`;
};
