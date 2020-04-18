$(document).ready(function(){
    $('input[type=radio][name=filtro-general]').change(function(){
        if (this.value === 'grid')
        {
            $('#filtro-general .card').removeClassPrefix('mb-').addClass('mb-g');
            $('#filtro-general .col-xl-12').removeClassPrefix('col-xl-').addClass('col-xl-4');
            $('#filtro-general .js-expand-btn').addClass('d-none');
            $('#filtro-general .card-body + .card-body').addClass('show');
        }
        else if (this.value === 'table')
        {
            $('#filtro-general .card').removeClassPrefix('mb-').addClass('mb-1');
            $('#filtro-general .col-xl-4').removeClassPrefix('col-xl-').addClass('col-xl-12');
            $('#filtro-general .js-expand-btn').removeClass('d-none');
            $('#filtro-general .card-body + .card-body').removeClass('show');
        }
    });
    initApp.listFilter($('#filtro-general'), $('#js-filter-general'));
});