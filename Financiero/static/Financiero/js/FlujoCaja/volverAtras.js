
'use strict';

function volverAtras() {
    location.href = localStorage.getItem('rutaOrigen');
}

function guardarRutaLocal(destino) {
    localStorage['rutaOrigen'] = window.location.pathname;
    location.href = destino
}
