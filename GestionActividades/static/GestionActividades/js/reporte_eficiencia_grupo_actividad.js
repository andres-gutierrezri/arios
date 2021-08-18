'use strict';

$(document).ready(function () {
    const rangoFechasID = $('#rango_fechas_id');

    inicializarDateRangePicker('rango_fechas_id');
    rangoFechasID.daterangepicker({
            startDate: moment().add(-1, 'month'),
            endDate: moment().add(1, 'month'),
            locale: {format: 'YYYY-MM-DD',}
        }
    );

    onChangeFechas(rangoFechasID)
    rangoFechasID.on('change', onChangeFechas);

    configurarFiltroConsecutivos();

});

function onChangeFechas(e) {
    $.getJSON(`/gestion-actividades/grupos-actividades/${grupoID}/reporte-eficiencia-grafica`, {rango_fechas: $('#rango_fechas_id').val()}).then(json => {
        if (json.estado === 'OK') {
            let datos = json.datos;
            console.log(datos)
            cargarDatosGrafica(datos.progreso_estimado, datos.progreso_real);
        } else {
            EVANotificacion.toast.error(json.estado === 'error' ? json.mensaje : 'No tiene permisos para acceder a esta funcionalidad');
        }
    });
}

function cargarDatosGrafica(progreso_estimado, progreso_real) {
    let plot2 = null;
    let datosGrafica = [
        {},
        {
            label: "Progreso Estimado",
            data: formatoCoordenadasGrafica(progreso_estimado),
            color: color.info._500,
            lines:
                {
                    show: true,
                    lineWidth: 3
                },
            shadowSize: 0,
            points:
                {
                    show: true
                }
        },
        {
            label: "Progreso Real",
            data: formatoCoordenadasGrafica(progreso_real),
            color: color.danger._500,
            lines:
                {
                    show: true,
                    lineWidth: 3
                },
            shadowSize: 0,
            points:
                {
                    show: true
                }
        }
    ]

    let opcionesGrafica = {
        grid:
            {
                hoverable: true,
                clickable: true,
                tickColor: '#f2f2f2',
                borderWidth: 1,
                borderColor: '#f2f2f2'
            },
        tooltip: true,
        tooltipOpts:
            {
                cssClass: 'tooltip-inner',
                defaultTheme: false
            },
        xaxis:
            {
                mode: "time",
                timeBase: "milliseconds",
                timeformat: "%Y-%m-%d"
            },
        yaxes:
            {
                tickFormatter: function (val, axis) {
                    return "$" + val;
                },
                max: 10000
            }
    };

    /*
    El objeto js-checkbox-toggles corresponde a los selectores de la grafica, realiza solamente la grafica
    de las líneas que corresponden a los selectores que están en estado "on".
    Si todos los selectores están en esta "off" dejara la grafica de la ultima linea con el estado
    "on" en el selector.
    */
    $("#js-checkbox-toggles").find(':checkbox').on('change', function () {
        pintarGrafica(plot2, datosGrafica, opcionesGrafica);
    });

    pintarGrafica(plot2, datosGrafica, opcionesGrafica);
}

/*
Función que permite pintar los puntos correspondientes a las coordenadas de la grafica.
Se le pasa los datos con las coordenadas en formato (x, y) de cada punto y las opciones de la grafica.
*/
function pintarGrafica(plot2, datosGrafica, opcionesGrafica) {
    let data = [];
    $("#js-checkbox-toggles").find(':checkbox').each(function () {
        if ($(this).is(':checked')) {
            data.push(datosGrafica[$(this).attr("name").substr(4, 1)]);
        }
    });
    if (data.length > 0) {
        if (plot2) {
            plot2.setData(data);
            plot2.draw();
        } else {
            plot2 = $.plot($("#flot-toggles"), data, opcionesGrafica);
        }
    }
}

/*
Función que establece las coordenadas para la grafica.
Se le pasa el arreglo con las llaves-valor y mediante el bucle for va obteniendo solo los valores,
armando la coordenada (x, y) de cada punto, retornando la data.
*/
function formatoCoordenadasGrafica(lista_progreso) {
    let retorno = [];
    for (let i = 0; i < lista_progreso.length; i++) {
        retorno.push([parseDate(lista_progreso[i].fecha), lista_progreso[i].numero_actividades_pendientes]);
    }
    return retorno;
}

function parseDate(fecha) {
    return new Date(Date.parse(fecha)).getTime();
}
