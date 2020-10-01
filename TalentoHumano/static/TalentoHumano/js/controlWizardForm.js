function activarForm(id){
    let form = document.getElementById("colaboradores-form");
    let formPart= document.getElementById(id);
    if(!form.checkValidity()){
        formPart.classList.add('was-validated');
    }
}