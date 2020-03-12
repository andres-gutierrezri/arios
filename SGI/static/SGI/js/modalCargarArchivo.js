$('#archivo_id').change(function(e){
    $('.custom-file-label').html(e.target.files[0].name);
});

function abrir_modal_cargar(url) {
    $('#cargar').load(url, function () {
        $(this).modal('show');
        $('#fecha_id').datepicker({
            todayHighlight: true,
            orientation: "bottom left",
            templates: controls,
            format: 'yyyy-mm-dd',
            autoclose: true
        });
    });
}