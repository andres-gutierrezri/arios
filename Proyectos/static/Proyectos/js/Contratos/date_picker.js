'use strict';

let controls = {
	leftArrow: '<i class="fal fa-angle-left" style="font-size: 1.25rem"></i>',
	rightArrow: '<i class="fal fa-angle-right" style="font-size: 1.25rem"></i>'
};

let runDatePicker = function () {

	// minimum setup
	$('#fecha_inicio_id').datepicker({
		todayHighlight: true,
		orientation: "bottom left",
		templates: controls,
		format: 'yyyy-mm-dd',
		autoclose: true
	});

	$('#fecha_terminacion_id').datepicker({
		todayHighlight: true,
		orientation: "bottom left",
		templates: controls,
		format: 'yyyy-mm-dd',
		autoclose: true
	});
};

$(document).ready(function () {
	runDatePicker();
});

