$(document).ready(function () {
    activarSelect2();
});

function activarSelect2(){
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
}