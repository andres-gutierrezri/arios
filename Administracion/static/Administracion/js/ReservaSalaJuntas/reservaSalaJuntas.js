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
        eventRender: function(event) {
            clases = event.event.classNames.toString();
            if (clases !== "mostrar") return false
        },
        // para cambio de posición del evento.
        eventDrop: function(event) {
            modificarEventos(event);
        },
    });
    calendario.render();
    calendario.addEventSource({
        url: '/administracion/reservas-sala-juntas/json'
    });
});

function modificarEventos(event){
    let eventObj = event.event;
    if (eventObj.id) {
        let idEvento = eventObj.id
        let url = `/administracion/reservas-sala-juntas/${idEvento}/editar`;
        let fechas = {  'inicio': moment(eventObj.start).format('YYYY-MM-DD HH:mm:ss'),
                        'fin':moment(eventObj.end).format('YYYY-MM-DD HH:mm:ss')};
        abrirModalCrearReserva(url, fechas, true);
    }
}

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

function fbtnCancelar(){
    calendario.refetchEvents();
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

function configurarModalCrear(fechas) {
    inicializarSelect2('responsable_select_id', modalCrearReserva);
    inicializarDateRangePicker('fecha_intervalo_id');
    if (fechas){
        $('#fecha_intervalo_id').data('daterangepicker').setStartDate(fechas.inicio);
        $('#fecha_intervalo_id').data('daterangepicker').setEndDate(fechas.fin);
    }
    agregarValidacionFormularios();
}
