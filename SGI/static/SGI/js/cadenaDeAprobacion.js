var valores_selectores = JSON.parse($('#valores_selectores').val());
var contenedor = $('#contenedor_selectores');
var contador = valores_selectores['contador'];
var selecciones = [];
var usuarios_seleccionados = $('#usuarios_seleccionados');

$(document).ready(function () {
    var temp  = contador;

    while(temp > 0){
        contenedor.append(crearSelectores(temp, true));
        temp -= 1;
    }
    $("#eliminar_1").hide();
});

function agregar() {
    var selector = $('#colaborador_id_' + contador);
    $("#agregar_" + (contador)).hide();
    $("#eliminar_" + (contador)).hide();
    selecciones.push(selector.val());
    selector.attr('disabled',true);
    if (valores_selectores.colaboradores.length > (contador)) {
        contador += 1;
        contenedor.append(crearSelectores(contador));
    }
    if (valores_selectores.colaboradores.length - contador === 0) {
        $("#agregar_" + (contador)).hide();
    }
    $('.select2').select2();
    usuarios_seleccionados.val(selecciones);
}

function eliminar(id) {
    contador -= 1;
    selecciones.pop();
    $("#elemento_" + id).remove();
    $("#agregar_" + (contador)).show();
    if(contador !== 1){
    $("#eliminar_" + (contador)).show();}
    $('#colaborador_id_' + contador).removeAttr('disabled',true);
    usuarios_seleccionados.val(selecciones);
}

function crearSelectores(posicion) {
    var valor;
    var opciones_colaborador = crearOpciones();

    valor = '<div class="form-group" id="elemento_'+ posicion +'"><div class="form-row">' +
            '<div class="col-md-11">' +
            '<label for="colaborador_id_'+ posicion +'">Usuario '+ posicion +' </label>'+
            '<select class="select2 form-control" name="ultimo_usuario" id="colaborador_id_'+ posicion +'">'+ opciones_colaborador +'</select></div>'+
            '<div class="col-md-1" style="padding-top:30px" id="botones_'+ posicion +'">'+
            '<a class="far fa-2x far fa-plus" id="agregar_'+ posicion +'" href="#" onclick="agregar()" title="" data-original-title="Agregar Usuario"></a>'+
            '<a class="far fa-2x far fa-times" id="eliminar_'+ posicion +'" href="#" onclick="eliminar('+posicion+')" title="" data-original-title="Eliminar Usuario"></a>'+
            '</div></div></div>';
    return valor;
}

function crearOpciones() {
    opciones_colaborador = [];
    valores_selectores['colaboradores'].forEach(function(usuario) {
        var existe = false;
        selecciones.forEach(function (id) {
            if (usuario['campo_valor'].toString() === id){
                existe = true}
        });
        if (!existe){
            opciones_colaborador += ('<option value="'+ usuario['campo_valor']+ '">'+ usuario['campo_texto']+ '</option>')}
    });
    return opciones_colaborador;
}
