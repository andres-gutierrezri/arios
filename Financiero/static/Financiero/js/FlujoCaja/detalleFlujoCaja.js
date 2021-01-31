
'use strict';

let selectFiltroAnio = $('#filtro_anio_id_select_id');
let selectFiltroMes = $('#filtro_mes_id_select_id');
let idContratoDetalle = $('#id_contrato_detalle');
let idTipoDetalle = $('#id_tipo_detalle');

 $(document).ready(function () {

    iniciarDataTable([1, 2, 3, 4, 5,6], 'dataTableFlujoCaja', [[ 5, "desc" ]])

    $('.select2').select2({
        "language": {
            noResults: function () {
              return 'No se encontraron coincidencias';
            },
            searching: function () {
              return 'Buscando…';
            },
            removeAllItems: function () {
              return 'Quitar todas los items';
            }
        },
    });
    selectFiltroAnio.change(function () {
        window.location = `/financiero/flujo-caja/procesos/${idContratoDetalle.val()}/detalle/${idTipoDetalle.val()}/anio/${selectFiltroAnio.val()}/mes/${selectFiltroMes.val()}`;
    });
    selectFiltroMes.change(function () {
        window.location = `/financiero/flujo-caja/procesos/${idContratoDetalle.val()}/detalle/${idTipoDetalle.val()}/anio/${selectFiltroAnio.val()}/mes/${selectFiltroMes.val()}`;
    });
});
