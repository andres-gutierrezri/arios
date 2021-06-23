'use strict'

$(document).ready(function () {
    const divCalendario = $('#calendar');
    const calendario = new FullCalendar.Calendar(divCalendario[0], {
        plugins: ['dayGrid', 'list', 'timeGrid', 'interaction', 'bootstrap'],
        themeSystem: 'bootstrap',
        timeZone: 'local', // Configurar zona horaria
        firstDay: 0, // Cambio del primer día de inicio de semana del calendario, (Domingo = 0, Lunes = 1,…)
        locale: 'es', // Cambio del lenguaje del calendario a español
        titleFormat: {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        },
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
    calendario.addEventSource({
        url: '/administracion/reservas-sala-juntas/json'
    });
});
