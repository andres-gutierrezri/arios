function validarCE(e) {
    tecla = (document.all) ? e.keyCode : e.which;
     //Validar el ingreso de + - * . ,
    if (tecla <= 46 && tecla >=42){
        return true;
    }

    // Permite el ingreso de la tecla para restar
    if (tecla === 8 || tecla === 95) {
        return true;
    }

    patron = /[A-Za-z0-9]/;
    tecla_final = String.fromCharCode(tecla);
    return patron.test(tecla_final);
}
