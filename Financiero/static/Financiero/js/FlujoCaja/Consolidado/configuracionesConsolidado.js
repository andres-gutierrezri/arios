
'use strict';

const controls = {
    leftArrow: '<i class="fal fa-angle-left" style="font-size: 1.25rem"></i>',
    rightArrow: '<i class="fal fa-angle-right" style="font-size: 1.25rem"></i>'
};

let idCategorias = $('#categorias_id');
let idContrato = $('#contrato_id');
let idProceso = $('#proceso_id');
let idEmpresa = $('#empresa_id');
let idEstados = $('#estados_id');
let idSubtipos = $('#subtipos_id');
let subtiposCategorias = JSON.parse($('#subtipos_categorias').val());
let divConsolidado = $('#div_consolidado');

// Inicio del bloque de Configuración de los Select Multiples

$('.select2').select2({
    language: {
        noResults: function() {
          return "No se encontraron coincidencias";
        },
        searching: function() {
          return "Buscando...";
        }
  }
});

$(document).ready(function() {
    let consolidadoComparativo = $('#consolidado_comparativo').val();
    let numeroMeses = $('#numero_meses').val();
    let configuracionColspan = $('.configuracion_colspan');
    if (consolidadoComparativo === 'True'){
        configuracionColspan.attr('colspan', ((parseInt(numeroMeses) * 2) + 2));
    }else{
        configuracionColspan.attr('colspan', (parseInt(numeroMeses) + 2));
    }

    // Configuración del Select Multiple de Categorias
    idCategorias.select2({
        placeholder: "Seleccione una opción",
        "language": {
            noResults: function () {
                return 'No se encontraron coincidencias';
            },
            searching: function () {
                return 'Buscando…';
            },
        },
    });
    let valoresCategorias = $('#valores_categorias').val();
    idCategorias.next().find("input").css("min-width", "200px");
    if (valoresCategorias){
        idCategorias.val(JSON.parse(valoresCategorias)).trigger("change");
    }
    //Fin del Bloque

    // Configuración del Select Multiple de Contrato
     idContrato.select2({
        placeholder: "Seleccione una opción",
        "language": {
            noResults: function () {
                return 'No se encontraron coincidencias';
            },
            searching: function () {
                return 'Buscando…';
            },
        },
    });
    let valoresContratos = $('#valores_contratos').val();
    idContrato.next().find("input").css("min-width", "200px");
    if (valoresContratos){
        idContrato.val(JSON.parse(valoresContratos)).trigger("change");
    }
    // Final del Bloque

    // Configuración del Select Multiple de Contrato
    idProceso.select2({
        placeholder: "Seleccione una opción",
        "language": {
            noResults: function () {
                return 'No se encontraron coincidencias';
            },
            searching: function () {
                return 'Buscando…';
            },
        },
    });

    let valoresProcesos = $('#valores_procesos').val();
    idProceso.next().find("input").css("min-width", "200px");
    if (valoresProcesos){
        idProceso.val(JSON.parse(valoresProcesos)).trigger("change");
    }
    // Final del Bloque

    // Configuración del Select Multiple de Empresas
    idEmpresa.select2({
        placeholder: "Seleccione una opción",
        "language": {
            noResults: function () {
                return 'No se encontraron coincidencias';
            },
            searching: function () {
                return 'Buscando…';
            },
        },
    });

    let valoresEmpresas = $('#valores_empresas').val();
    idEmpresa.next().find("input").css("min-width", "200px");
    if (valoresEmpresas){
        idEmpresa.val(JSON.parse(valoresEmpresas)).trigger("change");
    }
    // Final del Bloque

    // Configuración del Select Multiple de Estados
    idEstados.select2({
        placeholder: "Seleccione un opción",
        "language": {
            noResults: function () {
                return 'No se encontraron coincidencias';
            },
            searching: function () {
                return 'Buscando…';
            },
        },
    });
    idEstados.next().find("input").css("min-width", "200px");
    idEstados.val(JSON.parse($('#valores_estados').val())).trigger("change");
    // Final del Bloque

    // Configuración del Select Multiple de Subtipos
    idSubtipos.select2({
        placeholder: "Seleccione un opción",
        "language": {
            noResults: function () {
                return 'No se encontraron coincidencias';
            },
            searching: function () {
                return 'Buscando…';
            },
        },
    });
    let valoresSubtipos = $('#valores_subtipos').val();
    idSubtipos.next().find("input").css("min-width", "200px");
    if (valoresSubtipos){
        idSubtipos.val(JSON.parse(valoresSubtipos)).trigger("change");
    }

    idProceso.change(function () {
        cargarSeleccionesContratos();
    });

    idEmpresa.change(function () {
        cargarSeleccionesContratos();
    });
    // Fin del Bloque
});
// Fin del Bloque

function seleccionarTodos(elemento) {
    let idElemento = $('#' + elemento + '_id');
    let icono = $('#ic_all_' + elemento);
    let boton = $('#btn_all_' + elemento);
    let texto = $('#txt_all_' + elemento);
    if (icono.hasClass('fa-check')){
        boton.attr('title', 'Quitar Selecciones');
        idElemento.select2('destroy').find('option').prop('selected', 'selected').end().select2();
        icono.removeClass('fa-check');
        icono.addClass('fa-times');
        texto.html('Quitar Selecciones')
    }else{
        boton.attr('title', 'Seleccionar Todos');
        idElemento.select2('destroy').find('option').prop('selected', false).end().select2({placeholder: "Seleccione una opción"});
        icono.removeClass('fa-times');
        icono.addClass('fa-check');
        texto.html('Seleccionar Todos')
    }
    cargarSeleccionesContratos();
}

let fechaHasta = $('#fecha_hasta_id');
let fechaDesde = $('#fecha_desde_id');
let fecha_min_max = JSON.parse($('#fecha_min_max').val());
let fechaMinima = fecha_min_max.fecha_min.split(" ")[0];
let fechaMaxima = fecha_min_max.fecha_max.split(" ")[0];
let borrarFechaDesde = $('#borrarFechaDesde');
let borrarFechaHasta = $('#borrarFechaHasta');
let validarFechaDesde = $('#validar_fecha_desde');
let validarFechaHasta = $('#validar_fecha_hasta');

fechaDesde.change(function () {
    if (fechaDesde.val() !== ''){
        borrarFechaDesde.show();
    }else{
        borrarFechaDesde.hide();
    }
    if (fechaHasta.val() !== ''){
        if (new Date(fechaHasta.val()) < new Date(fechaDesde.val())) {
            fechaHasta.val('');
            fechaDesde.val('');
            borrarFechaHasta.hide();
            validarFechaDesde.html('La fecha desde no puede ser mayor a la fecha hasta seleccionada.');
            validarFechaDesde.show();
            borrarFechaDesde.hide();
            setTimeout(function() {
                validarFechaDesde.fadeOut(1000);
            }, 5000);
        }else{
            if (!validarFechaMaxMin(fechaDesde, validarFechaDesde)){
            borrarFechaDesde.hide();
            return false;
        }
            validarFechaDesde.hide();
        }
    }else{
        if (!validarFechaMaxMin(fechaDesde, validarFechaDesde)){
            borrarFechaDesde.hide();
        }else{
            validarFechaDesde.hide();
        }
    }
});

fechaHasta.change(function () {
    if (fechaHasta.val() !== ''){
        borrarFechaHasta.show();
    }else{
        borrarFechaHasta.hide();
    }
    if (fechaDesde.val() !== ''){
        if (new Date(fechaDesde.val()) > new Date(fechaHasta.val())) {
            fechaDesde.val('');
            fechaHasta.val('');
            borrarFechaDesde.hide();
            validarFechaHasta.html('La fecha hasta no puede ser inferior a la fecha desde seleccionada.');
            validarFechaHasta.show();
            borrarFechaHasta.hide();
            setTimeout(function() {
                validarFechaHasta.fadeOut(1000);
            }, 5000);
        }else{
            if (!validarFechaMaxMin(fechaDesde, validarFechaDesde)) {
                borrarFechaDesde.hide();
                return
            }
            validarFechaHasta.hide();
        }
    }else{
        if (!validarFechaMaxMin(fechaHasta, validarFechaHasta)){
            borrarFechaHasta.hide();
        }else{
            validarFechaHasta.hide();
        }
    }
});

// Configuraciones de los inputs de fecha desde hasta
$('.fecha-control ').datepicker({
		todayHighlight: true,
		orientation: "bottom left",
		templates: controls,
		format: 'yyyy-mm-dd',
		autoclose: true
	});

function validarFechaMaxMin(fecha, validador) {

    if (new Date(fechaMinima) > new Date(fecha.val())){
        validador.html('Los movimientos más antiguos van desde ' + fechaMinima);
        validador.show();
         setTimeout(function() {
                validador.fadeOut(1000);
            }, 5000);
        fecha.val('');
        return false;
    }else if (new Date(fechaMaxima) < new Date(fecha.val())){
        validador.html('Los movimientos más nuevos están hasta ' + fechaMaxima);
        validador.show();
         setTimeout(function() {
                validador.fadeOut(1000);
            }, 5000);
        fecha.val('');
        return false;
    }
    return true;
}

function borrarFecha(input) {
    if(input === 'fecha_desde'){
        fechaDesde.val('');
        borrarFechaDesde.hide();
    } else if (input === 'fecha_hasta'){
        fechaHasta.val('');
        borrarFechaHasta.hide();
    }
}

idCategorias.change(function () {
        let selecciones = [];
        $('#categorias_id option:selected').each(function() {
            selecciones.push($(this).val());
        });
        if (selecciones.length > 0) {
            idSubtipos.empty();
            for (let sel = 0; sel < selecciones.length; sel ++){
                for (let sub = 0; sub < subtiposCategorias.length; sub++) {
                    if (parseInt(selecciones[sel]) === subtiposCategorias[sub].categoria_id){
                        idSubtipos.append('<option value="' + subtiposCategorias[sub].id + '">' + subtiposCategorias[sub].nombre + '</option>');
                    }
                }
            }
        }else {
            idSubtipos.empty();
            for (let j = 0; j < subtiposCategorias.length; j++) {
                idSubtipos.append('<option value="' + subtiposCategorias[j].id + '">' + subtiposCategorias[j].nombre + '</option>');
            }
        }
    });

function desplegarDetalle(origen, idObjeto, idTipo) {
    let mas = $('#mas_'+ origen +'_' + idTipo + '_' + idObjeto);
    let boton =  $('#boton_'+ origen +'_' + idTipo + '_' + idObjeto);
    if (mas.is(':visible')) {
        mas.hide();
        boton.removeClass('fa-minus-circle');
        boton.addClass('fa-plus-circle');
    } else {
        mas.show();
        boton.removeClass('fa-plus-circle');
        boton.addClass('fa-minus-circle');
    }
}

function Imprimir() {
     let zonaImpresionConsolidado = divConsolidado.html();
     let zonaImpresionTotales = $('#div_totales').html();
     let originalContents = document.body.innerHTML;
     document.body.innerHTML = zonaImpresionConsolidado + zonaImpresionTotales;
     window.print();
     document.body.innerHTML = originalContents;
}

function cargarSeleccionesContratos() {
    let ruta = "/financiero/flujo-caja/consolidado/contratos_x_proceso/?empresas=[" + idEmpresa.val() + "]";
    if (idProceso.val().length > 0){
        ruta = "/financiero/flujo-caja/consolidado/contratos_x_proceso/?procesos=[" + idProceso.val()+ "]&empresas=[" + idEmpresa.val() + "]";
    }
    $.ajax({
        url: ruta,
        type: 'GET',
        context: document.body,
        success: function (data) {
            if(data.estado === "OK") {
                let contratoTemp = $('#contrato_id');
                let valoresContratoTemp = contratoTemp.val();
                let listaContratos = [];
                if (data.datos.includes('campo_valor')){
                    contratoTemp.empty();
                    JSON.parse(data.datos).forEach(function (index){
                        contratoTemp.append('<option value="' + index.campo_valor + '">' + index.campo_texto + '</option>')
                        $.each(valoresContratoTemp, function (ind, valContrato) {
                            if (parseInt(valContrato) === index.campo_valor){
                                listaContratos.push(valContrato);
                            }
                        });
                    });
                }else{
                    contratoTemp.empty();
                }
                if (listaContratos){
                    if (!idEmpresa.val()){
                        contratoTemp.empty();
                    }
                    contratoTemp.val(listaContratos).trigger('change');
                }
            }else {
                EVANotificacion.toast.error('Ha ocurrido un error');
            }
        },
        failure: function (errMsg) {
            EVANotificacion.toast.error('Ha ocurrido un error al enviar la solcitud.');
        }
    });
}

/*--------------------------------------------------------------------------------------------------------------------*/
/* Configuración para detectar el scroll x o y en el consolidado
 y poder invertir el position sticky y sus propiedades entre la columna y la fila. */

let ejeX = 0;
let ejeY = 0;
let movX = true;
let movY = true;
let alternarStickyTipoMovimiento1 = $('.alternar-sticky-tipo-movimiento-1');
let alternarStickyTipoMovimiento2 = $('.alternar-sticky-tipo-movimiento-2');
let alternarStickyCategoria1 = $('.alternar-sticky-categoria-1');
let alternarStickyCategoria2 = $('.alternar-sticky-categoria-2');
let alternarStickySubtipo1 = $('.alternar-sticky-subtipo-1');
let alternarStickySubtipo2 = $('.alternar-sticky-subtipo-2');
let alternarStickyConpro = $('.alternar-sticky-conpro');

divConsolidado.scroll(function() {
    if (ejeX !== divConsolidado.scrollLeft() ){
        movY=true;
       if(movX) {
           ejeX = divConsolidado.scrollLeft();
           alternarStickyTipoMovimiento1.removeClass('bg-primary-400');
           alternarStickyTipoMovimiento1.removeClass('fijar-left-tipo-movimiento-1');
           alternarStickyTipoMovimiento1.addClass('fijar-sticky-alternado-tipo-movimiento-1');
           alternarStickyTipoMovimiento2.removeClass('bg-primary-400');
           alternarStickyTipoMovimiento2.removeClass('fijar-left-tipo-movimiento-2');
           alternarStickyTipoMovimiento2.addClass('fijar-sticky-alternado-tipo-movimiento-2');

           alternarStickyCategoria1.removeClass('bg-info-700');
           alternarStickyCategoria1.removeClass('fijar-left-categoria-1');
           alternarStickyCategoria1.addClass('fijar-sticky-alternado-categoria-1');
           alternarStickyCategoria2.removeClass('bg-info-700');
           alternarStickyCategoria2.removeClass('fijar-left-categoria-2');
           alternarStickyCategoria2.addClass('fijar-sticky-alternado-categoria-2');

           alternarStickySubtipo1.removeClass('bg-success-700');
           alternarStickySubtipo1.removeClass('fijar-left-subtipo-1');
           alternarStickySubtipo1.addClass('fijar-sticky-alternado-subtipo-1');
           alternarStickySubtipo2.removeClass('bg-success-700');
           alternarStickySubtipo2.removeClass('fijar-left-subtipo-2');
           alternarStickySubtipo2.addClass('fijar-sticky-alternado-subtipo-2');

           alternarStickyConpro.removeClass('bg-fusion-50');
           alternarStickyConpro.removeClass('fijar-left-conpro');
           alternarStickyConpro.addClass('fijar-sticky-alternado-conpro');

           movX=false;
       }
    }
    if (ejeY !== divConsolidado.scrollTop()){
        movX=true;
        if(movY){
            ejeY = divConsolidado.scrollTop();
            alternarStickyTipoMovimiento1.removeClass('fijar-sticky-alternado-tipo-movimiento-1');
            alternarStickyTipoMovimiento1.addClass('bg-primary-400');
            alternarStickyTipoMovimiento1.addClass('fijar-left-tipo-movimiento-1');
            alternarStickyTipoMovimiento2.removeClass('fijar-sticky-alternado-tipo-movimiento-2');
            alternarStickyTipoMovimiento2.addClass('bg-primary-400');
            alternarStickyTipoMovimiento2.addClass('fijar-left-tipo-movimiento-2');

            alternarStickyCategoria1.removeClass('fijar-sticky-alternado-categoria-1');
            alternarStickyCategoria1.addClass('bg-info-700');
            alternarStickyCategoria1.addClass('fijar-left-categoria-1');
            alternarStickyCategoria2.removeClass('fijar-sticky-alternado-categoria-2');
            alternarStickyCategoria2.addClass('bg-info-700');
            alternarStickyCategoria2.addClass('fijar-left-categoria-2');

            alternarStickySubtipo1.removeClass('fijar-sticky-alternado-subtipo-1');
            alternarStickySubtipo1.addClass('bg-success-700');
            alternarStickySubtipo1.addClass('fijar-left-subtipo-1');
            alternarStickySubtipo2.removeClass('fijar-sticky-alternado-subtipo-2');
            alternarStickySubtipo2.addClass('bg-success-700');
            alternarStickySubtipo2.addClass('fijar-left-subtipo-2');

            alternarStickyConpro.removeClass('fijar-sticky-alternado-conpro');
            alternarStickyConpro.addClass('bg-fusion-50');
            alternarStickyConpro.addClass('fijar-left-conpro');

            movY=false;
        }
    }
});
/* fin de la configuración para el scroll del consolidado */
/*--------------------------------------------------------------------------------------------------------------------*/