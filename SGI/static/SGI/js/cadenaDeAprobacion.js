let contenedorSelectores = $('#valores_selectores');
let valorSelectores = contenedorSelectores.val() ? JSON.parse(contenedorSelectores.val()) : null;
let contenedor = $('#contenedor_selectores');
let contador = valorSelectores ? valorSelectores['contador'] : null;
let selecciones = [];
let usuariosSeleccionados = $('#usuarios_seleccionados');

function crear_id_compuesto(texto, numero){
    return $("#" + texto + '_' + (numero));
}

$(function () {
    if (valorSelectores) {
        let temp = contador;
        if (valorSelectores.opcion === 'editar') {
            let orden = 1, orden_anterior;
            while (orden <= temp) {
                crear_id_compuesto('agregar', (orden-1)).hide();
                crear_id_compuesto('eliminar', (orden-1)).hide();
                valorSelectores.selecciones.forEach(function (item) {
                    if (item.orden === orden){
                        contenedor.append(crearSelectores(item.orden, item.usuario_id));
                        selecciones.push(item.usuario_id);
                    }
                    if (orden === 1){
                         crear_id_compuesto('eliminar', orden).hide();
                    }
                });
                orden++;
            }
            orden_anterior = orden - 1;
            (orden > valorSelectores.colaboradores.length ? crear_id_compuesto('agregar', orden_anterior).hide() : null);
            crear_id_compuesto('usuario_id', orden_anterior).removeAttr('disabled', true);
            selecciones.pop();
            usuariosSeleccionados.val(selecciones);
        } else {
            while (temp > 0) {
                contenedor.append(crearSelectores(temp));
                temp--;
            }
            crear_id_compuesto('eliminar', 1).hide();
        }
    }
});

let agregar = function () {
    let selector = crear_id_compuesto('usuario_id', contador);
    crear_id_compuesto('agregar', contador).hide();
    crear_id_compuesto('eliminar', contador).hide();
    selecciones.push(selector.val());
    selector.attr('disabled', true);
   if (valorSelectores.colaboradores.length > contador){
       contador++;
       contenedor.append(crearSelectores(contador));
   }
    (valorSelectores.colaboradores.length - contador === 0 ? crear_id_compuesto('agregar', contador).hide() : null);
    $('.select2').select2();
    usuariosSeleccionados.val(selecciones);
};

let eliminar = function (id) {
    contador--;
    selecciones.pop();
    crear_id_compuesto('elemento', id).remove();
    crear_id_compuesto('agregar', contador).show();
    (contador !== 1 ?  crear_id_compuesto('eliminar', (contador)).show() : null);
     crear_id_compuesto('usuario_id', contador).removeAttr('disabled', true);
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
            if(!existe){
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
