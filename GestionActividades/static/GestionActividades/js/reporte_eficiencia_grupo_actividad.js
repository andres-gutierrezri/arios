'use strict';

$(document).ready(function () {

    var dataTargetProfit = [
        [1627362000000, 10],
        [1627621200000, 7],
        [1628485200000, 6],
        [1628726400000, 4],
        [1628812800000, 3],
        [1628899200000, 2],
        [1630213200000, 1],
    ]
    var dataProfit = [
        [1627362000000, 10],
        [1627621200000, 7],
        [1628485200000, 6],
        [1628726400000, 4],
        [1628812800000, 3],
        [1628899200000, 2],
        [1630213200000, 1],
    ]
    var dataSignups = [
        [1627362000000, 10],
        [1627621200000, 8],
        [1628485200000, 7],
        [1628726400000, 6],
        [1628812800000, 4],
        [1628899200000, 3],
        [1630213200000, 3],
    ]
    var flot_toggle = function () {
        var data = [
            {
                label: "Target Profit",
                data: dataTargetProfit,
                color: color.danger._500,
                bars:
                    {
                        show: true,
                        align: "center",
                        barWidth: 30 * 30 * 60 * 1000 * 80,
                        lineWidth: 0,
                        fillColor:
                            {
                                colors: [color.danger._900, color.danger._100]
                            }
                    },
                highlightColor: 'rgba(255,255,255,0.3)',
                shadowSize: 0
            },
            {
                label: "Tiempo Estimado",
                data: dataProfit,
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
                label: "Tiempo Real",
                data: dataSignups,
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
                    // timeBase: "milliseconds",
                    // timeformat: "%Y/%m/%d"
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
        plotNow()
    }
    flot_toggle();

    configurarFiltroConsecutivos();
});
