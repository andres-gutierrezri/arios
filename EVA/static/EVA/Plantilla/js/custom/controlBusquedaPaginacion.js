'use strict';

let timeout

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