
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
const tercerDiv = $('#tercer_div')
const cuartoDiv = $('#cuarto_div')

function configuracionNormal() {
    if (primerDiv.html() !== '') {
        tercerDiv.append(primerDiv.html())
        cuartoDiv.append(segundoDiv.html())
        primerDiv.html('')
        segundoDiv.html('')
        ejecutarChart()
    }
}

function configuracionMediana() {
    if (tercerDiv.html() !== '') {
        primerDiv.append(tercerDiv.html())
        segundoDiv.append(cuartoDiv.html())
        tercerDiv.html('')
        cuartoDiv.html('')
        ejecutarChart()
    }
}

function ejecutarChart() {
    const grafico = $('.js-easy-pie-chart');
    grafico.find('canvas').remove();
    grafico.find('span').html(grafico.attr('data-percent'))
    grafico.easyPieChart({
        barColor: '#563d7c',
        scaleLength: 0,
        lineWidth: 15,
        lineCap: 'square'
    });
}