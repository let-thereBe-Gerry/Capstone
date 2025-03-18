function openForm(button) {
    event.preventDefault(); 
    console.log("Opennnnnnnnnnnnnnnnnnnnn Form Function ~~~~~~~~~~~~~~~");

    var formId = `pop`;
    var formElement = document.getElementById(formId);

    if (formElement && button) {
        // Get the position of the button
        var buttonRect = button.getBoundingClientRect();
        var buttonTop = buttonRect.top;
        var buttonLeft = buttonRect.left;

        // Set the position of the popup near the button
        formElement.style.display = "block";
        formElement.style.top = buttonTop + buttonRect.height + "px";
        formElement.style.left = buttonLeft + "px";

    } else {
        console.error(`Form element with ID not found.`);
    }
}

function closeForm() {
    console.log("Close Form Function ~~~~~~~~~~~~~~~");

    var formId = `pop`;
    var formElement = document.getElementById(formId);

    if (formElement) {
        formElement.style.display = "none";
        console.log("CLOSE Booking ID : ");
    } else {
        console.error(`Form element with ID  not found.`);
    }
}


$(document).ready(function(){
setInterval(function(){
    $.ajax({
        type: 'GET',
        url : "/getMessages_Clinic/{{cRoom}}/",
        success: function(response){
            console.log(response);
            $("#display").empty();

            for (var key in response.messages) {
                    var user = response.messages[key].user;
                    var label = response.messages[key].label;

                    var sender = response.messages[key].sender;
                    var theSender = response.messages[key].theSender;
                    var reciever = response.messages[key].clinicSender;
                    if (sender == theSender){
                        var temp = "<div class='darker left'><span class='time-right'><p>"
                            + response.messages[key].date +
                            "</p></span><b>"
                            + label +
                            "</b><p>"
                            + response.messages[key].messageContent +    
                            "</p></div>";
                        $("#display").append(temp);
                    } else {
                        var temp = "<div class='container reciever'><span class='time-left'><p>"
                            + response.messages[key].date +
                            "</p></span><b>"
                            + label +
                            "</b><p>"
                            + response.messages[key].messageContent +
                            "</p></div>";
                        $("#display").append(temp);
                    }                            
                }                    
        },
        error: function(response){
            alert('An error occured')
        } 
    });
},100);
})               

var hiddenValue = document.getElementById("name").value;
var roomID = document.getElementById("room_id").value;
console.log("User: ", hiddenValue);
console.log("Room: ", roomID);
$(document).on('submit','#post-form',function(e){
e.preventDefault();
$.ajax({
    type:'POST',
    url:'/send_Clinic',
    data:{
        username:$('#name').val(),
        room_id:$('#room_id').val(),
        message:$('#message').val(),
        patient_ID:$('#patient_ID').val(),
    csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
    },
    success: function(data){
    }
});
document.getElementById('message').value = ''
});