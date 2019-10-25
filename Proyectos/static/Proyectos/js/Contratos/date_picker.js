		let controls = {
			leftArrow: '<i class="fal fa-angle-left" style="font-size: 1.25rem"></i>',
			rightArrow: '<i class="fal fa-angle-right" style="font-size: 1.25rem"></i>'
		};

		let runDatePicker = function () {

			// minimum setup
			$('#fecha_inicio').datepicker({
				todayHighlight: true,
				orientation: "bottom left",
				templates: controls
			});
			$('#fecha_terminacion').datepicker({
				todayHighlight: true,
				orientation: "bottom left",
				templates: controls
			});
		};

		$(document).ready(function () {
			runDatePicker();
		});

