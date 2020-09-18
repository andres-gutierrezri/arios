
'use stric';

let btnMesAnterior = $('#boton_mes_anterior');
let btnMesSiguiente = $('#boton_mes_siguiente');
let meses = $('#numero_meses').val();
let mesActual = 1;

function siguienteMes() {
    if (mesActual < parseInt(meses)){
        accionesAnteriorSiguiente(mesActual, 'ocultar');
        mesActual += 1;
        accionesAnteriorSiguiente(mesActual, 'mostrar');
    }
    if (mesActual >= parseInt(meses)){
        btnMesSiguiente.attr('disabled', true);
        btnMesAnterior.removeAttr('disabled', true);
    }else {
        btnMesSiguiente.removeAttr('disabled', true);
        btnMesAnterior.removeAttr('disabled', true);
    }
}

function anteriorMes() {
    if (mesActual > 1){
        accionesAnteriorSiguiente(mesActual, 'ocultar');
        mesActual -= 1;
        accionesAnteriorSiguiente(mesActual, 'mostrar');
    }
    if (mesActual <= 1){
        btnMesAnterior.attr('disabled', true);
        btnMesSiguiente.removeAttr('disabled', true);
    }else{
        btnMesAnterior.removeAttr('disabled', true);
        btnMesSiguiente.removeAttr('disabled', true);
    }
}

function accionesAnteriorSiguiente(mesActual, accion) {
    let mes = $('#titulo_mes_' + mesActual);
    let icg = $('.titulo_mes_' + mesActual);
    if (accion === 'mostrar'){
        mes.show();
        icg.show();
    }
    if (accion === 'ocultar'){
        mes.hide();
        icg.hide();
    }
}