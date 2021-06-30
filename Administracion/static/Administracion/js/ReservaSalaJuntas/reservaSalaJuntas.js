'use strict'

const modalCrearReserva = $('#crear-reserva');

$(document).ready(function () {
    const divCalendario = $('#calendar');
    const calendario = new FullCalendar.Calendar(divCalendario[0], {
        eventClick: function(info) {
        let eventObj = info.event;
            if (eventObj.id) {
                let idEvento = eventObj.id
                let url = "/administracion/reservas-sala-juntas/" + idEvento + "/editar";
                abrirModalCrearReserva(url);
            }
        },
        plugins: ['dayGrid', 'list', 'timeGrid', 'interaction', 'bootstrap'],
        themeSystem: 'bootstrap',
        timeZone: 'local', // Configurar zona horaria
        firstDay: 0, // Cambio del primer día de inicio de semana del calendario, (Domingo = 0, Lunes = 1,…)
        locale: 'es', // Cambio del lenguaje del calendario a español
        editable: true, // don't allow event dragging
        eventResourceEditable: true, // except for between resources

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

function abrirModalCrearReserva(url) {
    cargarAbrirModal(modalCrearReserva, url,function () {
        configurarModalCrear();
        const form = $("#juntas_form")[0];
        agregarValidacionForm(form, function (event) {
            enviarFormularioAsync(form, url).then(exitoso => {
                if (exitoso)
                    location.reload();
            });
            return true;
        });
    });
}

function fEliminarReunion(valor){
    modalCrearReserva.modal('hide');
     fConfirmarEliminar(valor, true, function (){
            EVANotificacion.toast.exitoso("funciono")
            calendario.refetchEvents();
            modalCrearReserva.modal('hide');
         }
     );
}

function configurarModalCrear() {
    inicializarSelect2('responsable_select_id', modalCrearReserva);
    inicializarDateRangePicker('fecha_intervalo_id');
    agregarValidacionFormularios();
}
