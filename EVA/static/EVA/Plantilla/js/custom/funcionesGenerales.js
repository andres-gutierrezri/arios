'use strict';

function mostrarCamposFormulario(lista){
    lista.forEach(function (objeto){
        objeto.attr('required', 'true');
        objeto.removeAttr('hidden', 'true')
    })
}

function ocultarCamposFormulario(lista) {
    lista.forEach(function (objeto){
        objeto.removeAttr('required', 'true')
        objeto.attr('hidden', 'true')
    })
}

function abrirModalVistaPrevia(urlDocumento) {
    const ifVista =  $("#if_vista_previa");

    ifVista.attr('src', '');
    ifVista.attr('src', urlDocumento);

    $("#vista_previa_modal").modal('show');
}


function fcopiarElemento(idElementoCopiar ,columna)
{
    let codigoConsecutivo;
    let idElemento = "copiar_"+idElementoCopiar
    let range = document.createRange();
    if(typeof columna !== 'undefined' || !$.isEmptyObject(columna)){
        codigoConsecutivo = document.getElementById(idElemento).parentNode.parentNode.cells[columna];
    }
    else {
        codigoConsecutivo = document.getElementById(idElemento).parentNode.parentNode
    }
    range.selectNode(codigoConsecutivo);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);
    document.execCommand("copy");
    window.getSelection().removeAllRanges();
    alert(codigoConsecutivo.textContent);
}

/*
let elementos = $('.copiarCodigo');
for (let i = 0; i < elementos.length; i++) {
        let codigoConsecutivo;
        elementos[i].addEventListener('click', function() {
        let range = document.createRange();
        codigoConsecutivo = this.parentNode.parentNode.cells[0];
        range.selectNode(codigoConsecutivo); //changed here
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);
        document.execCommand("copy");
        window.getSelection().removeAllRanges();
        alert(codigoConsecutivo.textContent);
    });
}

*/
