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


function fcopiarElemento(idElementoCopiar)
{
    let codigoConsecutivo;
    let idElemento = "copiar_"+idElementoCopiar
    let range = document.createRange();
    codigoConsecutivo = document.getElementById(idElemento);
    range.selectNode(codigoConsecutivo);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);
    document.execCommand("copy");
    window.getSelection().removeAllRanges();
    EVANotificacion.toast.informacion("Copiado cotrato: "+codigoConsecutivo.textContent)
    return codigoConsecutivo.textContent
}

