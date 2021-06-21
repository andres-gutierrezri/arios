'use strict'

$(document).ready(function () {
    const divCalendario = $('#calendar');
    const calendario = new FullCalendar.Calendar(divCalendario[0], {
        plugins: ['dayGrid', 'list', 'timeGrid', 'interaction', 'bootstrap'],
        themeSystem: 'bootstrap',
        timeZone: 'UTC',
        buttonText: {
            today: 'Hoy',
            month: 'Mes',
            week: 'Semana',
            day: 'Día',
            list: 'Lista'
        },
        header:
        {
            left: 'prev,next today addEventButton',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },

    });
    calendario.render();
});
