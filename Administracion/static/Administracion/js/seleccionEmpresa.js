let URLDomainEmpresa = document.location.origin+"/";

$(document).ready(function () {

    $('.seleccionEmpresaGlobal').click(function () {

        $.ajax({
            url: URLDomainEmpresa + "administracion/empresas/modal-seleccion",
            context: document.body
        }).done(function (response) {
            let mdEmpresa = $("#selectEmpresaGlobal");
            mdEmpresa.html(response);
            mdEmpresa.modal('show');
        });
    });
});

function cerrarModalEmpresa() {
    $("#selectEmpresaGlobal").modal('hide');
    $(".modal-backdrop").remove();
}

function clicEmpresa(idEmpresa) {

    let jsonEmpresa = {"idEmpresa":idEmpresa};

    $.ajax({
        url: URLDomainEmpresa + "administracion/empresas/modal-seleccion",
        data: JSON.stringify(jsonEmpresa),
        type: 'POST',
        contentType: "application/json; charset=utf-8;",
        dataType: "json",
        success: function (data) {
            cerrarModalEmpresa();
            if(data.estado === "OK") {
                location.reload();
            }
        },
        failure: function (errMsg) {
            alert('Se presentó un error. No se pudo seleccionar la empresa.');
            cerrarModalEmpresa();
            location.reload();
        }
    });
}
