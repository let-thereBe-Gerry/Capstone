$(document).ready(function() {
    function checkForNewMessages() {
        $.ajax({
            type: 'GET',
            url: "/messageNotification/NewMessage/",
            success: function(response) {
                if (response.hasOwnProperty('messages')) {
                    var newMessages = response.messages;
                    if (newMessages.length > 0) {
                        $("#notification-badge").text(newMessages.length);
                        $(".toast-container").empty();
                    }
                    for (var i = 0; i < newMessages.length; i++) {
                        var message = newMessages[i];
                        var clinicID = message.clinicID; // Ensure this matches your actual data structure
                        var toastHTML = `
                            <div class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-autohide="false">
                                <div class="toast-header" style="background: blue;">
                                    <strong class="mr-auto" style="color: white;">${message.sender}</strong>
                                    <small style="color: white;">${message.date}</small>
                                </div>
                                <div class="toast-body" style = "justify-content: space-between;">
                                    ${message.message_content}
                                    <form action="${createMessageUrl}" method="post" style="display:inline;">
                                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                                        <input type="hidden" name="selectedClinicID" value="${clinicID}">
                                        <button type="submit" class="btn btn-primary">Reply</button>
                                    </form>
                                </div>
                            </div>`;
                        $(".toast-container").append(toastHTML);
                        $('.toast').toast('show');
                    }
                }
            },
            error: function(xhr, status, error) {
                console.error('Error thrown:', error);
            },
            complete: function() {
                setTimeout(checkForNewMessages, 50000); // 10 seconds interval
            }
        });
    }
    checkForNewMessages();
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');
