function arbolDocumentos(id, id_accionador) {
    let accionador = $('#'+ id_accionador);
    let children = $("#"+id);

    if(children.is(':visible')) {
        children.hide('fast');
        accionador.removeClass('color-warning-300')
    }else{
        children.show('fast');
        accionador.addClass('color-warning-300')
    }
}