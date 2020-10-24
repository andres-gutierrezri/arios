
'use strict';

let divGarantias = $('#div_garantias');
let tipoGarantia = $('#tipo_garantia_id_select_id');
let porcentajeAsegurado = $('#porcentaje_asegurado_id');
let garantiaExtensiva = $('#garantia_extensiva');
let vigenciaGarantia = $('#vigencia_id');
let eliminarGarantia = $('#eliminar_garantia');
let datosGarantias = $('#datos_garantias');
let tiposGarantiasSmmlv = $('#tipos_garantias_smmlv');
let inputAmparos = $('#input_amparos');
let opcionesSelectAmparos = $('#opciones_amparos');
let valoresGarantias = [];
let contadorGarantia = 0;

function agregarGarantia(valores) {
    let datoTipoGarantia = tipoGarantia.val();
    let datoNombreTipoGarantia = $("#tipo_garantia_id_select_id option:selected").text();
    let datoPorcentajeAsegurado = porcentajeAsegurado.val();
    let datoVigenciaGarantia = vigenciaGarantia.val();
    let datoGarantiaExtensiva = vigencia.val();
    let datosAmparos = inputAmparos.val();

    if (valores){
        datoTipoGarantia = valores.tipo_garantia;
        datoNombreTipoGarantia = valores.nombre_tipo_garantia;
        datoPorcentajeAsegurado = valores.porcentaje_asegurado;
        datoVigenciaGarantia = valores.vigencia_garantia;
        datoGarantiaExtensiva = valores.garantia_extensiva;
        datosAmparos = valores.lista_amparos
    }

    let datos = JSON.parse(tiposGarantiasSmmlv.val());
    let textoLabelPorcentajeValor = 'Porcentaje';
    let textoLabelVigenciaAmparo = 'Vigencia (Meses)';
    datos.forEach(function (elemento) {
        if (parseInt(datoTipoGarantia) === elemento.id) {
            if (elemento.aplica_valor_smmlv) {
                textoLabelPorcentajeValor = 'SMMLV Asegurados';
                if (elemento.aplica_amparos){
                    textoLabelVigenciaAmparo = 'Amparos'
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
        'amparos': datosAmparos});

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
        <label>${textoLabelVigenciaAmparo}</label>
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
        <input hidden id="input_amparos_${contadorGarantia}" value='${datosAmparos}'>
        </div>`);
    contadorGarantia += 1;

    $('#select2-tipo_garantia_id_select_id-container').text('Seleccione un tipo de garantía');
    tipoGarantia.val('');
    porcentajeAsegurado.val('');
    vigenciaGarantia.val('');
    inputAmparos.val('');
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
    inputAmparos.val($('#input_amparos_'+ contadorGarantia).val());

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

let contadorAmparos = 0;

$('#div_despliegue_modal_amparo').click(function () {
    if (vigenciaGarantia.hasClass('desactivado')) {
        $('#agregar_amparo_modal').modal('show');
        $('#contenedor').empty();
        $('#contenedor_inicial').empty();
        contadorAmparos = 0;
        agregarAmparo(true);
    }
    if (inputAmparos.val() === 'undefined' || inputAmparos.val() === ''){
        $('#contenedor').empty();
        $('#contenedor_inicial').empty();
        contadorAmparos = 0;
        agregarAmparo(true);
    }else{
        let elementos = JSON.parse(inputAmparos.val());
        let opcionesAmparosJson = JSON.parse(opcionesSelectAmparos.val());
        elementos.forEach(function (e) {
            $('#amparo_select_0_id').val(e.amparo);
            $('#limite_asegurado_0_id').val(e.limite_asegurado);
            $('#select2-amparo_select_0_id-container').text(opcionesAmparosJson[1].campo_texto);
            if (e !== elementos[elementos.length - 1]){
                agregarAmparo(false);
            }
        });
    }
});

function agregarAmparo(inicial) {
    let amparoSeleccionId = $('#amparo_select_0_id');
    let limiteAsegurado = $('#limite_asegurado_0_id');
    let limiteAseguradoValor = '';

    if (limiteAsegurado.val() !== undefined){
        limiteAseguradoValor = limiteAsegurado.val();
    }

    let contenedor = $('#contenedor');
    let contenedorInicial = $('#contenedor_inicial');
    let pos = contadorAmparos;
    let opcionesAmparos = '';
    contadorAmparos += 1;
    let opcionesAmparosJson = JSON.parse(opcionesSelectAmparos.val());
    opcionesAmparosJson.forEach(function (e) {
        if (parseInt(amparoSeleccionId.val()) === e.campo_valor){
            opcionesAmparos += `<option value="${e.campo_valor}" selected>${e.campo_texto}</option>`
        }else{
            opcionesAmparos += `<option value="${e.campo_valor}">${e.campo_texto}</option>`
        }
    });

    let botonGestion;
    if (inicial){
        botonGestion = `<a class="far fa-2x far fa-plus-circle" id="agregar_amparo" href="#" 
                            onclick="agregarAmparo()" title="" data-original-title="Agregar Amparo" style=""></a>`
    }else{
        botonGestion = `<a class="far fa-2x far fa-trash-alt color-danger-900" id="eliminar_amparo" href="#"
                            onclick="quitarAmparo(${pos})" title="" data-original-title="Eliminar Amparo"></a>`;
    }

    let inputs = `
                <div class="form-row div-inputs-${pos}">
                    <div class="form-group col-5">
                       <label for="amparo_select_${pos}_id">Amparos</label>
                        <select class="amparo-select select2 form-control" id="amparo_select_${pos}_id" name="amparo_select_${pos}" tabindex="-1" required="required">
                            <option value="">Seleccione un amparo</option>
                            ${opcionesAmparos}
                        </select>
                        <div class="invalid-tooltip invalid-tooltip-modal">Por favor seleccione un amparo</div>
                    </div>
                    <div class="form-group col-6">
                        <label for="limite_asegurado_${pos}_id">Límite Asegurado</label>
                        <input id="limite_asegurado_${pos}_id" name="limite_asegurado_${pos}" placeholder="Ingrese el límite asegurado" maxlength="100"
                                  required="" class="form-control valores" value="${limiteAseguradoValor}">
                        <div class="invalid-tooltip ">Por favor ingrese el límite asegurado.</div>
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
    amparoSeleccionId.val('');
    limiteAsegurado.val('');

    $('.amparo-select').select2({
        dropdownParent: $('#agregar_amparo_modal')
    });
}

function quitarAmparo(pos) {
    $('.div-inputs-' + pos).remove();
    contadorAmparos -= 1
}

function configurarFormularioAmparo() {
    const form = $("#form_amparo")[0];
    agregarValidacionForm(form, function (event){
        guardarAmparo();
        cerrarModalAmparo();
        return true;
    });
}

function cerrarModalAmparo() {
    $("#agregar_amparo_modal").modal('hide');
    $(".modal-backdrop").remove();
}

function guardarAmparo() {
    let datos = [];

    for(let i=0; i < contadorAmparos; i++){
        datos.push({'amparo': $('#amparo_select_'+ i +'_id').val(),
            'limite_asegurado': $('#limite_asegurado_'+ i +'_id').val()
                .replace("'", "").replace('"', '')})
    }
    vigenciaGarantia.val(datos.length);
    inputAmparos.val(JSON.stringify(datos))
}

function validarTipoGarantia(){
    let datos = JSON.parse(tiposGarantiasSmmlv.val());
    let valorTipoGarantia = tipoGarantia.val();
    let labelValorPorcentajeAsegurado = $('#label_porcentaje_asegurado_id');
    let labelVigenciaAmparos = $('#label_vigencia_id');
    vigenciaGarantia.val('');

    if (valorTipoGarantia !== ''){
        datos.forEach(function (elemento) {
            if (parseInt(valorTipoGarantia) === elemento.id){
                if (elemento.aplica_valor_smmlv){
                    porcentajeAsegurado.attr('placeholder', 'Ingrese un valor');
                    porcentajeAsegurado.attr('max', '99999999999999.99');
                    porcentajeAsegurado.attr('onInput', 'validarLongitud(16,this)');
                    porcentajeAsegurado.next('div').text('Por favor ingrese un valor');
                    labelValorPorcentajeAsegurado.text('SMMLV Asegurados');
                    if (elemento.aplica_amparos){
                        labelVigenciaAmparos.text('Amparos');
                        vigenciaGarantia.attr('readonly', true);
                        vigenciaGarantia.addClass('desactivado');
                        if (inputAmparos.val() === '' || inputAmparos.val() === 'undefined' ||
                            inputAmparos.val() === undefined){
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
                if (!elemento.aplica_amparos){
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
    configurarFormularioAmparo();
});
