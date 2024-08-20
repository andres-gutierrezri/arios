'use strict';

function numToCurrencyStr(valor){
    // Se coloca 'en-CO', ya que con 'es-CO' no mostraba el separador de miles, etc.
    return valor.toLocaleString('en-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 2, maximumFractionDigits:2,
        currencyDisplay:'symbol'
    });
}

function numToDecimalStr(valor){
    // Se coloca 'en-CO', ya que con 'es-CO' no mostraba el separador de miles, etc.
    return valor.toLocaleString('en-CO', {
        style: 'decimal',
        minimumFractionDigits: 2, maximumFractionDigits:2,
    });
}

function redondear2Decimales(valor) {
    return Number(valor.toFixed(2));
}
