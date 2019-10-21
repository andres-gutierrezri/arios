 $(document).ready(function(){
            let mensaje = $('#mensaje');
            if (mensaje){
                if (mensaje.hasClass('alert.success'))
                    toastr['success'](mensaje.val());
                else if (mensaje.hasClass('alert.warning'))
                    toastr['warning'](mensaje.val());
            }
        });