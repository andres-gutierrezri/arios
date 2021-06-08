
const modalCrear = $('#crear');
const modalCrearReunion = $('#crear-reunion');

function abrirModalCargar(url) {
    $('#cargar').load(url, function (responseText, textStatus, req) {
        try {
            if (responseText.includes("<!DOCTYPE html>")) {
                EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                return false;
            }
            $(this).modal('show');
            $('#archivo_id').change(function (e) {
                let label_input = $('.custom-file-label');
                let extension = e.target.files[0].name.split('.').pop();
                if (extension === 'pdf' || extension === 'xlsx' || extension === 'docx' || extension === 'pptx'){
                    label_input.html(e.target.files[0].name);
                }else{
                    label_input.html('Seleccione un archivo');
                    e.target.value = '';
                    EVANotificacion.toast.error('El archivo ingresado no tiene un formato compatible. ' +
                                                '(Formatos Aceptados: PDF, Documento de Word, Documento de Excel, ' +
                                                'Presentacion de Power Point');
                    return false;
                }
            });
            agregarValidacionFormularios();
        } catch (err) {
            console.log(err);
            EVANotificacion.toast.error('Ha ocurrido un error al cargar el archivo');
        }
    });
}

function abrirModalCrear(url) {
    modalCrear.load(url, function (responseText, textStatus, req) {
        try {
            if (responseText.includes("<!DOCTYPE html>")) {
                EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                return false;
            }
            $(this).modal('show');
            configurarModalCrear ();
        } catch (err) {
            console.log(err);
            EVANotificacion.toast.error('Ha ocurrido un error al cargar el archivo');
        }
    });
}

function abrirModalCrearReunion(url) {
    modalCrearReunion.load(url, function (responseText, textStatus, req) {
        try {
            if (responseText.includes("<!DOCTYPE html>")) {
                EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                return false;
            }
            $(this).modal('show');
            configurarModalCrearReunion();
        } catch (err) {
            console.log(err);
            EVANotificacion.toast.error('Ha ocurrido un error');
        }
    });
}

function configurarModalCrearReunion() {
    inicializarDatePicker('fecha_id');
    agregarValidacionFormularios();
}

function configurarModalCrear() {
    extraTiposContrato = $('#extra_tipos_contrato');
    fechaInicioID = $('#fecha_inicio_id');
    fechaFinalID = $('#fecha_final_id');
    colaboradorSelect = $('#colaborador_mostrar_id');
    terceroSelect = $('#tercero_mostrar_id');
    colaboradorSelectID = $('#colaborador_select_id');
    terceroSelectID = $('#tercero_select_id');
    let idTipoContrato = $('#tipo_contrato_select_id').val();

    fechaFinal = $('#fecha_final_mostrar');
    $('#fecha_inicio_id').datepicker({
        todayHighlight: true,
        orientation: "bottom left",
        templates: controls,
        format: 'yyyy-mm-dd',
        autoclose: true
    });

    inicializarDatePicker('fecha_final_id');
    inicializarDatePicker('fecha_inicio_id');
    inicializarSelect2('tipo_contrato_select_id', modalCrear);
    inicializarSelect2('colaborador_select_id', modalCrear);
    inicializarSelect2('tercero_select_id', modalCrear);

    if (idTipoContrato === ""){
        $('#tipo_contrato_select_id').change(function () {
            let actual = this.value;
            CambiarSelect(actual);
            if (actual === ""){
                 fechaFinal.show();
                 fechaFinalID.attr("required", true);
                 mostrarOcultarColaboradorTercero("ninguno")
            }
        })
    }
    else{
        CambiarSelect(idTipoContrato);
        $('#tipo_contrato_select_id').change(function () {
            let actual = this.value;
            CambiarSelect(actual);
            if (actual === ""){
                 fechaFinal.show();
                 fechaFinalID.attr("required", true);
                 mostrarOcultarColaboradorTercero("ninguno")
            }
        })
    }

    fechaInicioID.change(function () {
        if (new Date(fechaInicioID.val()) > new Date(fechaFinalID.val())) {
            fechaFinalID.val('');
            EVANotificacion.toast.advertencia('La fecha inicial no puede ser mayor a la fecha final');
        }
    });

    fechaFinalID.change(function () {
        if (new Date(fechaFinalID.val()) < new Date(fechaInicioID.val())) {
            fechaInicioID.val('');
            EVANotificacion.toast.advertencia('La fecha final no puede ser menor a la fecha inicial');
        }
    });

    agregarValidacionFormularios();
}

function CambiarSelect (actual){
    $.each(jQuery.parseJSON(extraTiposContrato.val()), function(key, value) {
        if(actual == value.id){
            if (value.laboral){
                mostrarOcultarColaboradorTerceroTipoContrato(true)
            }else{
                mostrarOcultarColaboradorTerceroTipoContrato(false)
            }
            if(value.fecha_fin){
                fechaFinal.show();
                fechaFinalID.attr("required", true);
            }else{
                fechaFinal.hide();
                fechaFinalID.removeAttr("required", true);
            }
        }
    });
    if (actual === ""){
         fechaFinal.show();
         fechaFinalID.attr("required", true);
         mostrarOcultarColaboradorTercero("ninguno")
    }
}

function mostrarOcultarColaboradorTerceroTipoContrato(laboral) {
    if (laboral){
        colaboradorSelect.show();
        colaboradorSelectID.attr("required", true);
        terceroSelect.hide();
        terceroSelectID.removeAttr('required', true);
    }else{
        terceroSelect.show();
        terceroSelectID.attr("required", true);
        colaboradorSelect.hide();
        colaboradorSelectID.removeAttr('required', true);
    }
}
