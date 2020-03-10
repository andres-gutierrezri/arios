$('#archivo_id').change(function(e){
    $('.custom-file-label').html(e.target.files[0].name);
});