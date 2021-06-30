'use strict'

const modalCrearReserva = $('#crear-reserva');
let calendario;

$(document).ready(function () {
    const divCalendario = $('#calendar');
   calendario = new FullCalendar.Calendar(divCalendario[0], {
        plugins: ['dayGrid', 'list', 'timeGrid', 'interaction', 'bootstrap'],
        themeSystem: 'bootstrap',
        timeZone: 'local', // Configurar zona horaria
        firstDay: 0, // Cambio del primer día de inicio de semana del calendario, (Domingo = 0, Lunes = 1,…)
        locale: 'es', // Cambio del lenguaje del calendario a español
        editable: true,
        eventLimit: true, // allow "more" link when too many events
        selectable: true,
        selectHelper: true,
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
         validRange: {
            start: moment().format('YYYY-MM-DD')
        },
        //evento para mostrar, ocultar o modificar los eventos al momento de hacer render.
        eventRender: function(event) {
            clases = event.event.classNames.toString();
            if (clases !== "mostrar") return false
        },
        // evento para seleccionar un evento.
        eventClick: function(event) {
            modificarEventos(event);
        },
        // para cambio de posición del evento.
        eventDrop: function(event) {
            modificarEventos(event);
        },
        select: function(start, end) {
            let url = `/administracion/reservas-sala-juntas/add`;
            let fechas = {  'inicio': start.startStr,
                            'fin':start.startStr};
            abrirModalCrearReserva(url, fechas);
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

function abrirModalCrearReserva(url, fechas) {
   // let editar = `se ha ${url.includes("editar") ? "editar" : "crear"} la reserva para la sala de juntas`
    cargarAbrirModal(modalCrearReserva, url,function () {
        configurarModalCrear(fechas);
        const form = $("#juntas_form")[0];
        agregarValidacionForm(form, function (event) {
            enviarFormularioAsync(form, url).then(exitoso => {
                if (exitoso)
                    EVANotificacion.toast.exitoso(`Se ha ${url.includes("editar") ? "editado" : "creado"} la reserva para la sala de juntas`);
                    calendario.refetchEvents();
                    modalCrearReserva.modal('hide');
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
