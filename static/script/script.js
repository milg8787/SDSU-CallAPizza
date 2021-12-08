function onlyNumberKey(evt) {

    // Only ASCII character in that range allowed
    var ASCIICode = (evt.which) ? evt.which : evt.keyCode
    if (ASCIICode > 31 && (ASCIICode < 48 || ASCIICode > 57))
        return false;

    return true;
}

$(document).ready(function() {
    var rowCount = $('#orderTbl tr').length;
    if (rowCount <= 2) {
        $('#orderButton').css('background', '#8a97a0');
        $('#orderButton').prop('disabled', true)
    }

})