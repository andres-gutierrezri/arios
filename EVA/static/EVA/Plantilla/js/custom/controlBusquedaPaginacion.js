'use strict';

let timeout

function enviarBusqueda(elemento) {
    let code = (elemento.keyCode ? elemento.keyCode : elemento.which);
    if(code === 13) {
      filtrar();
    }
}

function filtrarPaginacion() {
    clearTimeout(timeout)
    timeout = setTimeout(() => {
        clearTimeout(timeout)
        filtrar()
    }, 2000)
}
let ubicacion = window.location.pathname;
function filtrar(){
    let busqueda = $('#busqueda').val();
    window.location.href =`${ubicacion}?search=${busqueda}`;
}