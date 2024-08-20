'use strict';

$(document).ready(function (){
    Inputmask.extendAliases({
        'evaCurrency': {
            alias: 'currency',
            digitsOptional: true,
            clearMaskOnLostFocus: true
        },
        'evaNumeric':{
            alias: 'numeric',
            groupSeparator: ',',
            digitsOptional: true,
            digits: 2,
            autoGroup: true,
            placeholder: '0',
        }
    });

    $(".inputmask").inputmask();
});
