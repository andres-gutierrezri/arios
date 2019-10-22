 $(document).ready(function(){
            let mensaje = $('#mensaje');
            if (mensaje){
                if (mensaje.hasClass('alert.success'))
                    toastr['success'](mensaje.val());
                else if (mensaje.hasClass('alert.warning'))
                    toastr['warning'](mensaje.val());
                else if (mensaje.hasClass('alert.error'))
                    toastr['error'](mensaje.val());
                else if (mensaje.hasClass('alert.info'))
                    toastr['info'](mensaje.val());
                else if (mensaje.hasClass('alert.debug'))
                    toastr['info'](mensaje.val());
            }
 });