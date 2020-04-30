function arbolDocumentos(id) {
    let children = $("#"+id);
    (children.is(':visible') ? children.hide('fast') : children.show('fast'));
}