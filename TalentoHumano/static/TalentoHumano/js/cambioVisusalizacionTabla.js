$(document).ready(function() {
    $('input[type=radio][name=contactview]').change(function()
    {
        if (this.value == 'grid')
        {
            $('#js-contacts .card').removeClassPrefix('mb-').addClass('mb-g');
            $('#js-contacts .col-xl-12').removeClassPrefix('col-xl-').addClass('col-xl-4');
            $('#js-contacts .js-expand-btn').addClass('d-none');
            $('#js-contacts .card-body + .card-body').addClass('show');

        }
        else if (this.value == 'table')
        {
            $('#js-contacts .card').removeClassPrefix('mb-').addClass('mb-1');
            $('#js-contacts .col-xl-4').removeClassPrefix('col-xl-').addClass('col-xl-12');
            $('#js-contacts .js-expand-btn').removeClass('d-none');
            $('#js-contacts .card-body + .card-body').removeClass('show');
        }

    });

    //initialize filter
    initApp.listFilter($('#js-contacts'), $('#js-filter-contacts'));
});