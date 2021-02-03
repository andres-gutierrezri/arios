
'use strict';

let selectFiltroAnio = $('#filtro_anio_id_select_id');
let selectFiltroMes = $('#filtro_mes_id_select_id');
const configuracionDFC = $('#configuracion_dfc')[0];

 $(document).ready(function () {

    const detalleColumnas = [{targets: [0, 4, 5], width: '8%'}]
    iniciarDataTable([1, 2, 3, 4, 5,6], 'dataTableFlujoCaja', [[ 5, "desc" ]], detalleColumnas);

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
        window.location = `/financiero/flujo-caja/${configuracionDFC.dataset.tipoFlujo}/${configuracionDFC.dataset.idContrato}/detalle/${configuracionDFC.dataset.idTipoDetalle}/anio/${selectFiltroAnio.val()}/mes/${selectFiltroMes.val()}`;
    });
    selectFiltroMes.change(function () {
        window.location = `/financiero/flujo-caja/${configuracionDFC.dataset.tipoFlujo}/${configuracionDFC.dataset.idContrato}/detalle/${configuracionDFC.dataset.idTipoDetalle}/anio/${selectFiltroAnio.val()}/mes/${selectFiltroMes.val()}`;
    });
});

 function cambioCheck(opcion){
    if (opcion === 'vigente') {
        location.href = window.location.pathname.split('?')[0];
    }else{
        location.href = window.location.pathname + '?eliminados=True';
    }
}
