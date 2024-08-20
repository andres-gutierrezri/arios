'use strict';

function validarCaracteresPermitidos(e) {
    let tecla = (document.all) ? e.keyCode : e.which;
     //Validar el ingreso de + - * . ,
    if (tecla <= 46 && tecla >=42){
        return true;
    }

    // Permite el ingreso de la tecla para restar
    if (tecla === 8 || tecla === 95 || tecla === 32) {
        return true;
    }

    let patron = /[A-Za-z0-9]/;
    let teclaFinal = String.fromCharCode(tecla);
    return patron.test(teclaFinal);
}
