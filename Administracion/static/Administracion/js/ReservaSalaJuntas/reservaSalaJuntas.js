'use strict'

const modalCrearReserva = $('#crear-reserva');

let calendario;
let mostrarOcultar;

$(document).ready(function () {
    const divCalendario = $('#calendar');
    calendario = new FullCalendar.Calendar(divCalendario[0], {
        plugins: ['dayGrid', 'list', 'timeGrid', 'interaction', 'bootstrap'],
        themeSystem: 'bootstrap',
        timeZone: 'local', // Configurar zona horaria
        firstDay: 0, // Cambio del primer día de inicio de semana del calendario, (Domingo = 0, Lunes = 1,…)
        locale: 'es', // Cambio del lenguaje del calendario a español
        allDayText: 'Horas', // The text titling the "all-day" slot at the top of the calendar
        defaultView: 'dayGridMonth', // The initial view when the calendar loads 'dayGridWeek', 'timeGridDay', 'listWeek'
        editable: true,
        eventLimit: 3, // allow "more" link when too many events
        eventLimitText: 'reservas',
        selectable: true,
        selectHelper: true,
        nowIndicator:true,
        noEventsMessage: 'No hay reservas para mostrar',
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
        // Evento para mostrar, ocultar o modificar los eventos al momento de hacer render
        // Mostrar y ocultar reservas
        eventRender: function(event) {
            mostrarOcultar = event.event.classNames.toString();
            if (mostrarOcultar !== "mostrar") return false
        },
        // Evento para modificar un evento (Modificar una reserva haciendo Click sobre ella)
        eventClick: function(event) {
            let fechaActual = moment(moment(),"DD-MM-YYYY HH:mm:ss");
            let fechaFinal = moment(event.event.end,"DD-MM-YYYY HH:mm:ss");
            let color = event.event.backgroundColor;
            if (fechaFinal > fechaActual || color === "orange") {
                modificarEventos(event);
            }
        },
        // Evento para cambio de posición de un evento (Cambio de posición de una reserva)
        eventDrop: function(event) {
            if(event.view.type !== 'listWeek') {
                $(event.el).popover('dispose');
            }
            let fechaActual = moment(moment(),"DD-MM-YYYY HH:mm:ss");
            let fechaNueva = moment(event.event.start,"DD-MM-YYYY HH:mm:ss");
            let color = event.event.backgroundColor;
            if (fechaActual >= fechaNueva || color === "gray" || color === "orange" || color === "red") {
                calendario.refetchEvents();
            } else {
                modificarEventos(event);
            }
        },
        // Evento de selección haciendo Click sobre el calendario (Creación de una reserva)
        select: function(start, end) {
            let fechaActual = moment(moment(),"DD-MM-YYYY HH:mm:ss");
            let fechaFin = moment(start.end,"DD-MM-YYYY HH:mm:ss");
            let url = `/administracion/reservas-sala-juntas/add`;
            let fechas = {
                'inicio': start.startStr,
                'fin':start.endStr
            };
            if (fechaFin >= fechaActual) {
                abrirModalCrearReserva(url, fechas);
            }
        },
        // Evento de arrastre de un evento (Modificación da la fecha final de una reserva)
        eventResize: function(event) {
            if(event.view.type !== 'listWeek') {
                $(event.el).popover('dispose');
            }
            let color = event.event.backgroundColor;
            if (color === "gray" || color === "orange") {
                calendario.refetchEvents();
            } else {
                modificarEventos(event);
            }

        },
        eventMouseEnter: mouseEnterInfo => {
            if(mouseEnterInfo.view.type !== 'listWeek') {
                const elemento =  $(mouseEnterInfo.el);
                elemento.popover({content: mouseEnterInfo.event.title, placement:'top'});
                elemento.popover('show');
            }
        },
        eventMouseLeave: mouseLeaveInfo => {
            if(mouseLeaveInfo.view.type !== 'listWeek') {
                $(mouseLeaveInfo.el).popover('dispose');
            }
        },
        eventSourceSuccess: (content, xhr) => {
            return content.datos;
        },
        eventSourceFailure: (errorObj ) => {
            console.error(errorObj.message);
            EVANotificacion.toast.error("Error al cargar las reservas");
        }
    });
    calendario.render();
    calendario.addEventSource({
        url: '/administracion/reservas-sala-juntas/json'
    });
});

function modificarEventos(event) {
    let eventObj = event.event;
    if (eventObj.id) {
        let idEvento = eventObj.id
        let url = `/administracion/reservas-sala-juntas/${idEvento}/editar`;
        let fechaInicial = moment(eventObj.start).format('YYYY-MM-DD HH:mm:ss');
        let fechaFinal = moment(eventObj.end).format('YYYY-MM-DD HH:mm:ss');
        let fechas = {
            'inicio': fechaInicial,
            'fin':eventObj.end ? fechaFinal : fechaInicial
        };
        abrirModalCrearReserva(url, fechas, true);
    }
}

function abrirModalCrearReserva(url, fechas) {
    cargarAbrirModal(modalCrearReserva, url,function () {
        configurarModalCrear(fechas);
        const form = $("#juntas_form")[0];
        agregarValidacionForm(form, function (event) {
            enviarFormularioAsync(form, url).then(exitoso => {
                if (exitoso) {
                    calendario.refetchEvents();
                    modalCrearReserva.modal('hide');
                }
            });
            return true;
        });
    });
}

function fbtnCancelar() {
    calendario.refetchEvents();
}

function fEliminarReunion(valor) {
    modalCrearReserva.modal('hide');
     fConfirmarEliminar(valor, true, function () {
            EVANotificacion.toast.exitoso("La reserva ha sido eliminada");
            calendario.refetchEvents();
            modalCrearReserva.modal('hide');
         }
     );
}

function fFinalizarReunion(valor) {
    modalCrearReserva.modal('hide');
    Swal.fire({
        title: '¿Está seguro que desea finalizar la reunión?',
        text: "Esta acción no se podrá revertir",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: '¡Sí, finalizarla!',
        cancelButtonText: 'Cancelar'
    }).then(result => {
        if(result.value) {
            const form = $("#juntas_form")[0];
            let url = `/administracion/reservas-sala-juntas/${valor}/finalizar`;
            enviarFormularioAsync(form, url).then(exitoso => {
                if (exitoso) {
                    calendario.refetchEvents();
                    modalCrearReserva.modal('hide');
                }
            });
        }
    });
}

function configurarModalCrear(fechas) {
    inicializarSelect2('responsable_select_id', modalCrearReserva);
    inicializarDateRangePicker('fecha_intervalo_id');
    $('#fecha_intervalo_id').data('daterangepicker').minDate=moment();
    if (fechas){
        $('#fecha_intervalo_id').data('daterangepicker').setStartDate(fechas.inicio);
        $('#fecha_intervalo_id').data('daterangepicker').setEndDate(fechas.fin);
    }
    modalCrearReserva.on('hidden.bs.modal', function () {
        calendario.refetchEvents();
    });
    agregarValidacionFormularios();
}
