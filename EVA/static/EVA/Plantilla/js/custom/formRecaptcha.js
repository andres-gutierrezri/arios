'use strict';

const form = $('.form-recaptcha')[0];

function enviarConRecaptcha(token){
    if (form.checkValidity() === false) {
        form.classList.add('was-validated');
        resetRecaptcha();
    } else {
        form.submit();
    }
}

function resetRecaptcha(){
    grecaptcha.reset();
}

function errorRecaptcha(){
    EVANotificacion.toast.error("Ocurrió un error con reCaptcha. Intente nuevamente");
}
