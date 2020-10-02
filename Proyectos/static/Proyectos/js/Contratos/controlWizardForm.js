function activarForm(id){
    let form = document.getElementById("contrato-form");
    let formPart= document.getElementById(id);
    if(!form.checkValidity()){
        formPart.classList.add('was-validated');
    }
}