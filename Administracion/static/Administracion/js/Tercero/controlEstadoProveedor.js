
'use strict'

let resizeTimer;

$(window).resize(function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(validarTamano, 100);
});

$(document).ready(function () {
    validarTamano();
});

function validarTamano() {
    let tamano = $(window).width();
    if (tamano > 1400) {
        configuracionNormal();
    } else if (tamano < 574) {
        configuracionNormal();
    } else if (tamano < 1400 && tamano > 574) {
        configuracionMediana();
    }
}

const primerDiv = $('#primer_div')
const segundoDiv = $('#segundo_div')

function configuracionNormal() {
    if (primerDiv.html() !== '') {
        segundoDiv.append(primerDiv.html())
        primerDiv.html('')
    }
}

function configuracionMediana() {
    if (segundoDiv.html() !== '') {
        primerDiv.append(segundoDiv.html())
        segundoDiv.html('')
    }
}