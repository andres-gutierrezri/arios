'use strict';

let textoBusqueda = $('#texto_busqueda');
let formBusqueda = $('#form_busqueda');

$(document).ready(function(){
      textoBusqueda.keypress(function(e) {
        if(e.which === 13) {
          formBusqueda.submit();
        }
      });
});