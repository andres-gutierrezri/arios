
'use strict';

function abrirModalCrearEditar(url) {
    $('#crear_editar').load(url, function (responseText) {
        try {
            if (responseText.includes("<!DOCTYPE html>")) {
                EVANotificacion.toast.error('No tiene permisos para acceder a esta funcionalidad');
                return false;
            }
            $(this).modal('show');
            agregarValidacionFormularios();
            let modalSubtipoMovimiento = $('#crear_editar');
            $('#tipo_movimiento_id_select_id').select2({
                dropdownParent: modalSubtipoMovimiento,
                language: {
                    noResults: function() {
                      return "No se encontraron coincidencias";
                    },
                    searching: function() {
                      return "Buscando...";
                    }
              }
            });
            $('#categoria_movimiento_id_select_id').select2({
                dropdownParent: modalSubtipoMovimiento,
                language: {
                    noResults: function() {
                      return "No se encontraron coincidencias";
                    },
                    searching: function() {
                      return "Buscando...";
                    }
              }
            });
        } catch (err) {
            console.log(err);
            EVANotificacion.toast.error('Ha ocurrido un error interno');
        }
    });
}