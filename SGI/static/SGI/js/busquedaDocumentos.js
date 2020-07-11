'use strict';

let textoBusqueda = $('#texto_busqueda');
let idBusqueda = $('#id_buscar');
let formBusqueda = $('#form_busqueda');

$(document).ready(function(){
      textoBusqueda.keypress(function(e) {
        if(e.which === 13) {
          ejecutarBusqueda();
        }
      });
      idBusqueda.on('click', function() {
          ejecutarBusqueda();
      });
});

function ejecutarBusqueda() {
    formBusqueda.submit();
}