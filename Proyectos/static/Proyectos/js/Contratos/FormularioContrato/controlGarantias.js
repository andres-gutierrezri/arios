
'use strict';

let divGarantias = $('#div_garantias');
let tipoGarantia = $('#tipo_garantia_id_select_id');
let porcentajeAsegurado = $('#porcentaje_asegurado_id');
let garantiaExtensiva = $('#garantia_extensiva');
let vigenciaGarantia = $('#vigencia_id');
let eliminarGarantia = $('#eliminar_garantia');
let datosGarantias = $('#datos_garantias');
let tiposGarantiasSmmlv = $('#tipos_garantias_smmlv');
let valoresGarantias = [];
let contadorGarantia = 0;

function agregarGarantia(valores) {
    let datoTipoGarantia = tipoGarantia.val();
    let datoNombreTipoGarantia = $("#tipo_garantia_id_select_id option:selected").text();
    let datoPorcentajeAsegurado = porcentajeAsegurado.val();
    let datoVigenciaGarantia = vigenciaGarantia.val();
    let datoGarantiaExtensiva = vigencia.val();
    if (valores){
        datoTipoGarantia = valores.tipo_garantia;
        datoNombreTipoGarantia = valores.nombre_tipo_garantia;
        datoPorcentajeAsegurado = valores.porcentaje_asegurado;
        datoVigenciaGarantia = valores.vigencia_garantia;
        datoGarantiaExtensiva = valores.garantia_extensiva;
    }
    if (datoTipoGarantia === '' || datoPorcentajeAsegurado === '' || datoVigenciaGarantia === ''){
        EVANotificacion.toast.error('Debes llenar los campos disponibles antes de realizar esta acción.');
        return false;
    }
    let inputCheck;
    let checkActivo = false;
    eliminarGarantia.show();
    if (garantiaExtensiva.prop('checked') || datoGarantiaExtensiva === true){
        inputCheck = '<input disabled checked id="valor_garantia_extensiva_'+ contadorGarantia +'" type="checkbox" class="custom-control-input">';
        checkActivo = true;
    }else{
        inputCheck = '<input disabled id="valor_garantia_extensiva_'+ contadorGarantia +'" type="checkbox" class="custom-control-input">';
    }

    valoresGarantias.push({'pos': contadorGarantia, 'tipo_garantia': datoTipoGarantia, 'vigencia_garantia': datoVigenciaGarantia,
        'porcentaje_asegurado': datoPorcentajeAsegurado, 'garantia_extensiva': checkActivo, 'nombre_tipo_garantia': datoNombreTipoGarantia});

    divGarantias.append('<div class="form-group" id="garantia_'+ contadorGarantia +'" style="margin-bottom: 0">\n' +
        '<div class="form-row" style="padding-bottom: 0">\n' +
        '<div class="col-md-3">\n' +
        '<label>Tipo de Garantía</label>\n' +
        '<input hidden type="text" id="valor_tipo_garantia_'+ contadorGarantia +'" value="'+ datoTipoGarantia +'">\n' +
        '<input disabled type="text" id="texto_tipo_garantia_'+ contadorGarantia +'" value="'+ datoNombreTipoGarantia +'"\n' +
        'class="form-control">\n' +
        '</div>\n' +
        '<div class="col-md-3">\n' +
        '<label>Porcentaje Asegurado</label>\n' +
        '<input disabled type="text" id="valor_porcentaje_asegurado_'+ contadorGarantia +'" value="'+ datoPorcentajeAsegurado +'"\n' +
        'class="form-control">\n' +
        '</div>\n' +
        '<div class="col-md-3">\n' +
        '<label>Vigencia (Meses)</label>\n' +
        '<input disabled type="text" id="valor_vigencia_garantia_'+ contadorGarantia +'" value="'+ datoVigenciaGarantia +'" class="form-control">\n' +
        '</div>\n' +
        '<div class="col-md-2" style="padding-top: 33px;">\n' +
        '<div class="custom-control custom-checkbox">\n' + inputCheck +
        '<label class="custom-control-label">Garantía Extensiva</label>\n' +
        '</div></div>\n' +
        '<div class="col-md-1" style="padding-top:30px">\n' +
        '<a class="far fa-2x far fa-edit" href="#" onclick="editarPosGarantia('+ contadorGarantia +')" title="" data-original-title="Agregar Garantía" style=""></a>\n' +
        '<a class="far fa-2x far fa-trash-alt color-danger-900" href="#" onclick="quitarPosGarantia('+ contadorGarantia +')" title="" data-original-title="Eliminar Garantía"></a>\n' +
        '</div>' +
        '</div><br></div>');
    contadorGarantia += 1;

    $('#select2-tipo_garantia_id_select_id-container').text('Seleccione un tipo de garantía');
    tipoGarantia.val('');
    porcentajeAsegurado.val('');
    vigenciaGarantia.val('');
    garantiaExtensiva.prop('checked', false);
    datosGarantias.val(JSON.stringify(valoresGarantias));
}

function editarPosGarantia(contador) {
    if (tipoGarantia.val() !== '' && vigenciaGarantia.val() !== '' && porcentajeAsegurado.val() !== ''){
        $('#agregar_garantia').click();
    }
    retomarCampoGarantia(contador);
    valoresGarantias.forEach(function (elemento, pos) {
       if (elemento.pos === contador){
            valoresGarantias.splice(pos, 1)
       }
    });
    datosGarantias.val(JSON.stringify(valoresGarantias));
    $('#garantia_'+ contador).remove();
}

function quitarPosGarantia(contador) {
    valoresGarantias.forEach(function (elemento, pos) {
       if (elemento.pos === contador){
            valoresGarantias.splice(pos, 1)
       }
    });
    $('#garantia_'+ contador).remove();
    datosGarantias.val(JSON.stringify(valoresGarantias));
}

function quitarGarantia() {
    contadorGarantia -= 1;

    if (contadorGarantia === 0){
        eliminarGarantia.hide();
    }
    valoresGarantias.pop();
    retomarCampoGarantia(contadorGarantia);
    $('#garantia_'+ contadorGarantia).remove();
     datosGarantias.val(JSON.stringify(valoresGarantias));
}

function retomarCampoGarantia(contadorGarantia){
    let valorTipoGarantia = $('#valor_tipo_garantia_' + contadorGarantia).val();
    let textoTipoGarantia = $('#texto_tipo_garantia_' + contadorGarantia).val();

    $('#select2-tipo_garantia_id_select_id-container').text(textoTipoGarantia);
    tipoGarantia.val(valorTipoGarantia);

    porcentajeAsegurado.val($('#valor_porcentaje_asegurado_'+ contadorGarantia).val());
    vigenciaGarantia.val($('#valor_vigencia_garantia_'+ contadorGarantia).val());

    if ($('#valor_garantia_extensiva_'+ contadorGarantia).prop('checked')){
        garantiaExtensiva.prop('checked', true);
    }else{
       garantiaExtensiva.prop('checked', false);
    }
}

tipoGarantia.change(function () {
    validarTipoGarantia();
    validarPorcentajeAsegurado();
});

function validarTipoGarantia(){
    let datos = JSON.parse(tiposGarantiasSmmlv.val());
    let valorTipoGarantia = tipoGarantia.val();
    let labelValorPorcentajeAsegurado = $('#label_porcentaje_asegurado_id');

    if (valorTipoGarantia !== ''){
        datos.forEach(function (elemento) {
            if (parseInt(valorTipoGarantia) === elemento.id){
                if (elemento.aplica_valor_smmlv){
                    porcentajeAsegurado.attr('placeholder', 'Ingrese un valor');
                    porcentajeAsegurado.attr('max', '99999999999999.99');
                    porcentajeAsegurado.attr('onInput', 'validarLongitud(16,this)');
                    porcentajeAsegurado.next('div').text('Por favor ingrese un valor');
                    labelValorPorcentajeAsegurado.text('SMMLV Asegurados')
                }else{
                    porcentajeAsegurado.attr('placeholder', 'Ingrese el porcentaje');
                    porcentajeAsegurado.attr('max', '100');
                    porcentajeAsegurado.attr('onInput', 'validarLongitud(5,this)');
                    porcentajeAsegurado.next('div').text('Por favor ingrese el porcentaje (Maximo 100%)');
                    labelValorPorcentajeAsegurado.text('Porcentaje Asegurado')
                }
            }
        })
    }
}

porcentajeAsegurado.change(function () {
   validarPorcentajeAsegurado();
});

function validarPorcentajeAsegurado() {
    let tiposGarantiasSMMLV = JSON.parse(tiposGarantiasSmmlv.val());

    tiposGarantiasSMMLV.forEach(function (elemento) {
        if (parseInt(tipoGarantia.val()) === elemento.id){
            if (!elemento.aplica_valor_smmlv){
                if (parseFloat(porcentajeAsegurado.val()) > 100){
                    porcentajeAsegurado.val('');
                    $('#guardar').click();
                    return false
                }
            }
        }
    });
}

$(document).ready(function () {
    valoresGarantias = [];
    divGarantias.html('');
    datosGarantias.val('');
    let valores_garantias = $('#valores_garantias_actuales').val();
    if (valores_garantias){
        $.each(JSON.parse(valores_garantias), function (pos, garantia) {
            agregarGarantia(garantia)
        });
    }
    quitarGarantia();
    validarPorcentajeAsegurado();
    validarTipoGarantia()
});