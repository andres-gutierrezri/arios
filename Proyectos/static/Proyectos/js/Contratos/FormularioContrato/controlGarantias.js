
'use strict';

let divGarantias = $('#div_garantias');
let tipoGarantia = $('#tipo_garantia_id_select_id');
let porcentajeAsegurado = $('#porcentaje_asegurado_id');
let garantiaExtensiva = $('#garantia_extensiva');
let vigenciaGarantia = $('#vigencia_id');
let eliminarGarantia = $('#eliminar_garantia');
let datosGarantias = $('#datos_garantias');
let tiposGarantiasSmmlv = $('#tipos_garantias_smmlv');
let inputAdicionesAmparos = $('#input_adiciones_amparos');
let valoresGarantias = [];
let contadorGarantia = 0;

function agregarGarantia(valores) {
    let datoTipoGarantia = tipoGarantia.val();
    let datoNombreTipoGarantia = $("#tipo_garantia_id_select_id option:selected").text();
    let datoPorcentajeAsegurado = porcentajeAsegurado.val();
    let datoVigenciaGarantia = vigenciaGarantia.val();
    let datoGarantiaExtensiva = vigencia.val();
    let datosAdicionesAmparos = inputAdicionesAmparos.val();

    if (valores){
        datoTipoGarantia = valores.tipo_garantia;
        datoNombreTipoGarantia = valores.nombre_tipo_garantia;
        datoPorcentajeAsegurado = valores.porcentaje_asegurado;
        datoVigenciaGarantia = valores.vigencia_garantia;
        datoGarantiaExtensiva = valores.garantia_extensiva;
        datosAdicionesAmparos = valores.adiciones_amparos
    }

    let datos = JSON.parse(tiposGarantiasSmmlv.val());
    let textoLabelPorcentajeValor = 'Porcentaje';
    let textoLabelVigenciaAmparoAdicion = 'Vigencia (Meses)';
    datos.forEach(function (elemento) {
        if (parseInt(datoTipoGarantia) === elemento.id) {
            if (elemento.aplica_valor_smmlv) {
                textoLabelPorcentajeValor = 'SMMLV Asegurados';
                if (elemento.aplica_amparos_adiciones){
                    textoLabelVigenciaAmparoAdicion = 'Amparos y Adiciones'
                }
            }
        }
    });

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
        'porcentaje_asegurado': datoPorcentajeAsegurado, 'garantia_extensiva': checkActivo, 'nombre_tipo_garantia': datoNombreTipoGarantia,
        'adiciones_amparos': datosAdicionesAmparos});

    divGarantias.append(`<div class="form-row" id="garantia_${contadorGarantia}" style="margin-bottom: 0">
        <div class="form-group col-md-3">
        <label>Tipo de Garantía</label>
        <input hidden type="text" id="valor_tipo_garantia_${contadorGarantia}" value="${datoTipoGarantia}">
        <input disabled type="text" id="texto_tipo_garantia_${contadorGarantia}" value="${datoNombreTipoGarantia}" class="form-control">
        </div>
        <div class="form-group col-md-3">
        <label>${textoLabelPorcentajeValor}</label>
        <input disabled type="text" id="valor_porcentaje_asegurado_${contadorGarantia}" value="${datoPorcentajeAsegurado}" class="form-control">
        </div>
        <div class="form-group col-md-3">
        <label>${textoLabelVigenciaAmparoAdicion}</label>
        <input disabled type="text" id="valor_vigencia_garantia_${contadorGarantia}" value="${datoVigenciaGarantia}" class="form-control">
        </div>
        <div class="col-md-2" style="padding-top: 33px;">
        <div class="custom-control custom-checkbox">${inputCheck}
        <label class="custom-control-label">Garantía Extensiva</label>
        </div></div>
        <div class="col-md-1" style="padding-top:30px">
        <a class="far fa-2x far fa-edit" href="#" onclick="editarPosGarantia(${contadorGarantia})" title="" data-original-title="Agregar Garantía" style=""></a>
        <a class="far fa-2x far fa-trash-alt color-danger-900" href="#" onclick="quitarPosGarantia(${contadorGarantia})" title="" data-original-title="Eliminar Garantía"></a>
        </div>
        <input hidden id="input_adiciones_amparos_${contadorGarantia}" value='${datosAdicionesAmparos}'>
        </div>`);
    contadorGarantia += 1;

    $('#select2-tipo_garantia_id_select_id-container').text('Seleccione un tipo de garantía');
    tipoGarantia.val('');
    porcentajeAsegurado.val('');
    vigenciaGarantia.val('');
    inputAdicionesAmparos.val('');
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
    inputAdicionesAmparos.val($('#input_adiciones_amparos_'+ contadorGarantia).val());

    if ($('#valor_garantia_extensiva_'+ contadorGarantia).prop('checked')){
        garantiaExtensiva.prop('checked', true);
    }else{
       garantiaExtensiva.prop('checked', false);
    }
    validarTipoGarantia();
}

tipoGarantia.change(function () {
    validarTipoGarantia();
    validarPorcentajeAsegurado();
});

$('#div_despliegue_modal_adicion_amparo').click(function () {
    if (vigenciaGarantia.hasClass('desactivado')) {
        $('#agregar_adicion_amparo').modal('show');
        $('#contenedor').empty();
        $('#contenedor_inicial').empty();
        contadorAdiciones = 0;
        agregarAdicionAmparo(true);
    }
    if (inputAdicionesAmparos.val() === 'undefined' || inputAdicionesAmparos.val() === ''){
        $('#contenedor').empty();
        $('#contenedor_inicial').empty();
        contadorAdiciones = 0;
        agregarAdicionAmparo(true);
    }else{
        let elementos = JSON.parse(inputAdicionesAmparos.val());
        elementos.forEach(function (e) {
            $('#descripcion_0_id').val(e.descripcion);
            $('#limite_asegurado_0_id').val(e.limite_asegurado);
            if (e.adicion_amparo === '0'){
                $('#adicion_0_id').click();
            }else{
                $('#amparo_0_id').click();
            }
            if (e !== elementos[elementos.length - 1]){
                agregarAdicionAmparo(false);
            }
        })
    }
});

let contadorAdiciones = 0;

function agregarAdicionAmparo(inicial) {
    let descripcion = $('#descripcion_0_id');
    let limiteAsegurado = $('#limite_asegurado_0_id');
    let descripcionValor = '';
    let limiteAseguradoValor = '';
    let seleccionAdicionRadio = '';
    let seleccionAmparoRadio = '';

    if (descripcion.val() !== undefined){
        descripcionValor = descripcion.val();
    }
    if (limiteAsegurado.val() !== undefined){
        limiteAseguradoValor = limiteAsegurado.val();
    }
    if ($('input:radio[name=adicion_amparo_0]:checked').val() === '0'){
        seleccionAdicionRadio = `checked`
    }else{
        seleccionAmparoRadio = `checked`
    }

    let contenedor = $('#contenedor');
    let contenedorInicial = $('#contenedor_inicial');
    let pos = contadorAdiciones;
    contadorAdiciones += 1;

    let botonGestion;
    if (inicial){
        botonGestion = `<a class="far fa-2x far fa-plus-circle" id="agregar_adicion_amparo" href="#" 
                            onclick="agregarAdicionAmparo()" title="" data-original-title="Agregar Adición o Amparo" style=""></a>`
    }else{
        botonGestion = `<a class="far fa-2x far fa-trash-alt color-danger-900" id="eliminar_garantia" href="#"
                            onclick="quitarAdicionAmparo(${pos})" title="" data-original-title="Eliminar Garantía"></a>`;
    }
    let inputs = `<div class="form-row div-inputs-${pos}">
                    <div class="form-group col-4">
                        <label for="descripcion_${pos}_id">Descripción</label>
                        <textarea id="descripcion_${pos}_id" name="descripcion" placeholder="Ingrese la descripción" maxlength="300"
                                  required="" class="form-control valores">${descripcionValor}</textarea>
                        <div class="invalid-tooltip ">Por favor ingrese el número del contrato.</div>
                    </div>
                    <div class="form-group col-4">
                        <label for="limite_asegurado_${pos}_id">Límite Asegurado</label>
                        <textarea id="limite_asegurado_${pos}_id" name="limite_asegurado" placeholder="Ingrese el límite asegurado" maxlength="100"
                                  required="" class="form-control valores">${limiteAseguradoValor}</textarea>
                        <div class="invalid-tooltip ">Por favor ingrese el número del contrato.</div>
                    </div>
                    <div class="form-group col-2">
                        <div class="form-row">
                            <div class="col-12">
                                <p>Seleccione</p>
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="col-12">
                                <div class="custom-control custom-radio custom-control-inline">
                                    <input type="radio" class="custom-control-input" id="adicion_${pos}_id" name="adicion_amparo_${pos}" value="0"
                                           required="" ${seleccionAdicionRadio}>
                                    <label class="custom-control-label" for="adicion_${pos}_id">Adición</label>
                                </div>
                                &nbsp;&nbsp;<div class="custom-control custom-radio custom-control-inline">
                                <input type="radio" class="custom-control-input" id="amparo_${pos}_id" name="adicion_amparo_${pos}" value="1"
                                       required="" ${seleccionAmparoRadio}>
                                <label class="custom-control-label" for="amparo_${pos}_id">Amparo</label>
                            </div>
                                <div class="invalid-tooltip ">Por favor seleccione una opción</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-1" style="padding-top:30px">
                        ${botonGestion}
                    </div>
                </div>`;
    if (inicial && contenedorInicial.is(':empty')){
        contenedorInicial.append(inputs);
    }else{
        contenedor.append(inputs)
    }
    descripcion.val('');
    limiteAsegurado.val('');
}

function quitarAdicionAmparo(pos) {
    $('.div-inputs-' + pos).remove();
    contadorAdiciones -= 1
}

function configurarFormularioAdicionAmparo() {
    const form = $("#form_adicion_amparo")[0];
    agregarValidacionForm(form, function (event){
        guardarAdicionAmparo();
        cerrarModalAdicionAmparo();
        return true;
    });
}

function cerrarModalAdicionAmparo() {
    $("#agregar_adicion_amparo").modal('hide');
    $(".modal-backdrop").remove();
}

function guardarAdicionAmparo() {
    let datos = [];

    for(let i=0; i < contadorAdiciones; i++){
        datos.push({'descripcion': $('#descripcion_'+ i +'_id').val(),
            'limite_asegurado': $('#limite_asegurado_'+ i +'_id').val(),
            'adicion_amparo': $('input:radio[name=adicion_amparo_'+ i +']:checked').val()})
    }
    vigenciaGarantia.val(datos.length);
    inputAdicionesAmparos.val(JSON.stringify(datos))
}

function validarTipoGarantia(){
    let datos = JSON.parse(tiposGarantiasSmmlv.val());
    let valorTipoGarantia = tipoGarantia.val();
    let labelValorPorcentajeAsegurado = $('#label_porcentaje_asegurado_id');
    let labelVigenciaAmparos = $('#label_vigencia_id');

    if (valorTipoGarantia !== ''){
        datos.forEach(function (elemento) {
            if (parseInt(valorTipoGarantia) === elemento.id){
                if (elemento.aplica_valor_smmlv){
                    porcentajeAsegurado.attr('placeholder', 'Ingrese un valor');
                    porcentajeAsegurado.attr('max', '99999999999999.99');
                    porcentajeAsegurado.attr('onInput', 'validarLongitud(16,this)');
                    porcentajeAsegurado.next('div').text('Por favor ingrese un valor');
                    labelValorPorcentajeAsegurado.text('SMMLV Asegurados');
                    if (elemento.aplica_amparos_adiciones){
                        labelVigenciaAmparos.text('Amparos o Adiciones');
                        vigenciaGarantia.attr('readonly', true);
                        vigenciaGarantia.addClass('desactivado');
                        if (inputAdicionesAmparos.val() === '' || inputAdicionesAmparos.val() === 'undefined' ||
                            inputAdicionesAmparos.val() === undefined){
                            vigenciaGarantia.val('')
                        }
                    }
                }else{
                    porcentajeAsegurado.attr('placeholder', 'Ingrese el porcentaje');
                    porcentajeAsegurado.attr('max', '100');
                    porcentajeAsegurado.attr('onInput', 'validarLongitud(5,this)');
                    porcentajeAsegurado.next('div').text('Por favor ingrese el porcentaje (Maximo 100%)');
                    labelValorPorcentajeAsegurado.text('Porcentaje Asegurado')
                }
                if (!elemento.aplica_amparos_adiciones){
                    vigenciaGarantia.removeAttr('readonly', true);
                    vigenciaGarantia.removeClass('desactivado');
                    labelVigenciaAmparos.text('Vigencia (Meses)');
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
                    document.getElementById(porcentajeAsegurado[0].id).setCustomValidity('.');
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
    validarTipoGarantia();
    configurarFormularioAdicionAmparo();
});
