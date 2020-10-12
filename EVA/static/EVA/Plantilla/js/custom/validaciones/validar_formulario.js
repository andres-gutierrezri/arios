'use strict';

(function() {
    window.addEventListener('load', function() {
        agregarValidacionFormularios();
    }, false);
})();

function agregarValidacionFormularios() {
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    let forms = document.getElementsByClassName("needs-validation");
    // Loop over them and prevent submission
    let validation = Array.prototype.filter.call(forms, function(form) {
        agregarValidacionForm(form);
    });
}

/**
 * Agrega los estilos personalizados de validación, en esta validación se incluye la validación de los
 * valores min y max de los inputmask marcados con la clase 'inputmask'.
 * @param form Formulario al que se le quiere agregar los estilos personalizados en la validación
 * @param fnCallback Función que sera ejecutada cuando la validación se completa exitosamente, si esta función retorna
 * true indica  que se debe evitar el submit del formulario.
 */
function agregarValidacionForm(form, fnCallback){
    form.addEventListener('submit', function(event) {
        validarMinMaxInputMask(form);
        if (form.checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
            form.classList.add('was-validated');
        } else {
            if(fnCallback !== undefined)
                if(fnCallback(event)) {
                    event.preventDefault();
                    event.stopPropagation();
                }
        }
    }, false);
}

function validarLongitud(longitud, elemento){
    let fieldLength = elemento.value.length;
    if(fieldLength <= longitud) {
        return true;
    }
    else {
        let str = elemento.value;
        str = str.substring(0, str.length - 1);
        elemento.value = str;
    }
}

function validarMinMaxInputMask(form) {
    let valido = true;
    const inputs = form.getElementsByClassName('inputmask');
    for(let i = 0; i < inputs.length; i++) {
        const valor = Number(inputs[i].inputmask.unmaskedvalue());
        if(valor < inputs[i].min || valor > inputs[i].max) {
            if(valor < inputs[i].min)
                inputs[i].nextElementSibling.innerText = `Debe ser mayor o igual a ${inputs[i].min}`;
            else
                inputs[i].nextElementSibling.innerText = `Debe ser menor o igual a ${inputs[i].max}`;
            inputs[i].setCustomValidity('.');
            valido = false;
        }
        else
            inputs[i].setCustomValidity('');
    }
    return valido;
}

function limpiarFormulario(form) {
    form.reset();
    form.classList.remove('was-validated');
}
