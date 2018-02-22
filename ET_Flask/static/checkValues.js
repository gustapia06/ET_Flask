var inputs = document.getElementsByClassName('only_num');

var checkVals = function(e){
    if(!this.validity.valid) {
        e.target.setCustomValidity("Please enter a valid number");
    }
    
    // to avoid the 'sticky' invalid problem when resuming typing after getting a custom invalid message
    this.addEventListener('input', function(e) {e.target.setCustomValidity('');}, false);
}

for (i=0; i<inputs.length; i++)
{
    inputs[i].addEventListener('invalid', checkVals, false);
}
