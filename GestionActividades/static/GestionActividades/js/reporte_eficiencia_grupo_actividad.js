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

function parseDate(fecha) {
        return new Date(Date.parse(fecha)).getTime();
    }

function formatoFlot(dt) {
        let retorno = [];
        for (let i = 0; i < dt.length; i++) {
            retorno.push([parseDate(dt[i].fecha), dt[i].numero_actividades_pendientes]);
        }
        return retorno;
    }

function onChangeFechas(e) {
    let form = $('#rango_fechas_form')[0];
    enviarFormularioAsyncCallBack(form,  `/gestion-actividades/grupos-actividades/${grupoID}/reporte-eficiencia-grafica`, "cargando").then(json => {
        if (json.estado === 'OK') {
            var datos = json.datos;
            let coordenadas_tiempo_estimado = Object.values(datos["progreso_estimado"]);
            let coordenadas_tiempo_real = Object.values(datos["progreso_real"]);
            var flot_toggle = function () {
        var data = [
            {},
            {
                label: "Progreso Estimado",
                data: formatoFlot(coordenadas_tiempo_estimado),
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
                data: formatoFlot(coordenadas_tiempo_real),
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
            }]

        var options = {
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

        var plot2 = null;

        function plotNow() {
            let d = [];
            $("#js-checkbox-toggles").find(':checkbox').each(function () {
                if ($(this).is(':checked')) {
                    d.push(data[$(this).attr("name").substr(4, 1)]);
                }
            });
            if (d.length > 0) {
                if (plot2) {
                    plot2.setData(d);
                    plot2.draw();
                } else {
                    plot2 = $.plot($("#flot-toggles"), d, options);
                }
            }

        };

        $("#js-checkbox-toggles").find(':checkbox').on('change', function () {
            plotNow();
        });
        plotNow();

    }
    flot_toggle();

        } else {
            EVANotificacion.toast.error(json.estado === 'error' ? json.mensaje : 'No tiene permisos para acceder a esta funcionalidad');
        }
    });
}
