function arbolDocumentos(id, id_accionador) {
    let accionador = $('#'+ id_accionador);
    let children = $("#"+id);

    if(children.is(':visible')) {
        children.hide('fast');
        accionador.removeClass('color-primary-50')
    }else{
        children.show('fast');
        accionador.addClass('color-primary-50')
    }
}