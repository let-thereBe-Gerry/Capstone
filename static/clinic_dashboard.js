// var clinicId = {{ clinic.clinicID }};
var clinicId = document.body.getAttribute('data-clinic-id');

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Patient/Appointment Management
        document.addEventListener('DOMContentLoaded', function () {
            const appointmentForm = document.getElementById('appointmentForm');
            const acceptButtons = document.querySelectorAll('.accept-btn');
            const declineButtons = document.querySelectorAll('.decline-btn');
            //const appointmentForm = document.getElementById('appointmentForm');
            const sessionButtons = document.querySelectorAll('.sesion-btn, .cancel-btn');
            // const appointmentElement = document.getElementById(`appointment_${bookingId}`);

            appointmentForm.addEventListener('click', function (event) {
                const target = event.target;        
                // Check if the clicked element is an accept or decline button
                if (target.classList.contains('accept-btn') || target.classList.contains('decline-btn')) {
                    event.preventDefault();
        
                    // Find the closest parent element with the ID starting with 'appointment_'
                    const appointmentElement = target.closest('[id^="appointment_"]');
                    
                    console.log('TEST A ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ A');
                    // NEED TO CREATE A CANCELATION REASON NOTES FOR OPTHAL AND PATIENT
                    if (appointmentElement) {
                        console.log('TEST B ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ B');
                        const bookingId = target.getAttribute('data-booking-id');
                        updateBookingStatus(bookingId, target.classList.contains('accept-btn') ? 'accept' : 'decline', appointmentElement);
                        appointmentElement.style.display = 'none';
                        //appointmentElement.style.display = Booking.is_hidden ? 'none' : 'block';
                    } else {
                        console.log('TEST C ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ C');
                        console.error('Parent element not found for button:', target);
                    }
                    event.stopPropagation();
                } else if (target.classList.contains('sesion-btn') || target.classList.contains('cancel-btn')) {
                    event.preventDefault();
    
                    // Find the closest parent element with the ID starting with 'appointment_'
                    const appointmentElement = target.closest('[id^="appointment_"]');
    
                    if (appointmentElement) {
                        const bookingId = target.getAttribute('sesion-booking-id');
                        const action = target.classList.contains('sesion-btn') ? 'end_session' : 'cancel_session';
    
                        updateSessionStatus(bookingId, action, appointmentElement);
                    } else {
                        console.error('Parent element not found for button:', target);
                    }
                    event.stopPropagation();
                } 

            });


            function updateBookingStatus(bookingId, status, appointmentElement) {
                console.log('Updating booking status...');
                const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
                // const appointmentElement = document.getElementById(`appointment_${bookingId}`); // kahit nandito ito, naka null pa rin
                console.log('CSRF Token:', csrfToken);                
            
                const url = '/update_booking_status/';
                console.log('CSRF Token Before Fetch:', csrfToken);
            
                const payload = {
                    bookingId: bookingId,
                    status: status,
                };
            
                console.log('Request Payload:', payload);
            
                fetch(url, { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: JSON.stringify(payload),
                })
                .then(function(response) {
                    return response.json();
                })

                .then(function(data) {
                    console.log('Response:', data);
                    console.log('Attempting to find element:', `appointment_${bookingId}`);
                    const appointmentElement = document.getElementById(`appointment_${bookingId}`);
                    
                    if (appointmentElement) { // PAG NAKA DENIEND, NULL ANG VALUE N'YA, ALTHOUGH NAKA PRINT S'YA
                        console.log('TEST ONE --------------------------- 1');
                        console.log('Element found:', `appointment_${bookingId}`);
                        //appointmentElement.style.display = 'none';                        
                        appointmentElement.style.display = data.is_hidden ? 'none' : 'block';
                    } else {
                        console.log('TEST TWO --------------------------- 2');
                        console.log('appointmentElement --------------------------- ', appointmentElement); // SO BAKIT NULL KA?

                        console.error('Element not found:', `appointment_${bookingId}`);
                    } // since wala pa namang epekto ito, balikan na lang muna kita
                
                    if (data.success) {
                        console.log('TEST Three --------------------------- 3');
                        // Handle success if needed
                    } else {
                        console.error('Failed to update booking status');
                    }
                })
                .catch(function(error) {
                    console.error('Error:', error);
                });
            }
        });

        function updateSessionStatus(bookingId, action, appointmentElement) {
            console.log(`Updating session status for booking ${bookingId}...`);

            const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
            const url = '/update_session_status/';

            const payload = {
                bookingId: bookingId,
                action: action,
            };

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify(payload),
            })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                    console.log('TEST ONEEEEEEEE');
                    console.log('Response:', data);

                if (appointmentElement) {
                    console.log('TEST TWOOOOOOOO');
                    appointmentElement.style.display = data.is_hidden ? 'none' : 'block';
                } else {
                    console.log('TEST THREEEEEE');
                    console.error('Element not found:', `appointment_${bookingId}`);
                }

                if (data.success) {
                    console.error('TEST FOUUUUUUUUUR');
                    // Handle success if needed
                } else {
                    console.error('Failed to update session status');
                }
            })
            .catch(function (error) {
                console.error('Error:', error);
            });
        }
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ENd Patient/Appointment Management

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CALENDAR
        function getCookie(name) {
                    var cookieValue = null;
                    if (document.cookie && document.cookie !== '') {
                        var cookies = document.cookie.split(';');
                        for (var i = 0; i < cookies.length; i++) {
                            var cookie = cookies[i].trim();
                            // Does this cookie string begin with the name we want?
                            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                break;
                            }
                        }
                    }
                    return cookieValue;
                }

         // pag nasa outside yung code, pag binabago ayaw lumabas.  
        document.addEventListener('DOMContentLoaded', function() {
          var csrfToken = "{{ csrf_token }}";
          var calendarEl = document.getElementById('calendar');
      
           // Get the current date
          var currentDate = new Date();

          // Format the date as 'YYYY-MM-DD'
          var formattedDate = currentDate.toISOString().slice(0, 10);


          var calendar = new FullCalendar.Calendar(calendarEl, {
            headerToolbar: {
              left: 'prev,next today',
              center: 'title',
              right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },

            initialDate: formattedDate,

            navLinks: true, // can click day/week names to navigate views
            selectable: true,
            selectMirror: true,

            select: function(arg) {
                var title = prompt('Event Title:');
                if (title) {
                    calendar.addEvent({
                        title: title,
                        start: arg.start,
                        end: arg.end,
                        allDay: arg.allDay
                    });
            
                    // bakit hindi lumalabas yung calendar? hmmm
                    var data_toSend = {
                        appt_title: title,
                        appt_start: arg.start.toISOString(),
                        appt_end: arg.end.toISOString(),
                        appt_allDay: arg.allDay,
                        csrfmiddlewaretoken: csrfToken
                    };
                    
            
                    fetch('/save_event/', {
                        method: 'POST',  // POST or GET? -- if ginawa ko s'yang GET, walang nag ssave even empty data
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify(data_toSend)
                    })

                    .then(response => response.json())
                    .then(data => console.log(data))
                    .catch(error => console.error('Error:', error));
                }
                calendar.unselect();
            },

            eventClick: function(arg) {
              if (confirm('Are you sure you want to delete this event?')) {
                arg.event.remove()
              }
            },
            editable: true,
            dayMaxEvents: true, // allow "more" link when too many events

            events: '/get_events/' + clinicId + '/', 
            // all the event should be coming in the database - hindi pa rin nag didisplay huhu -- maybe kaya hindi nag ddisplay kasi empty yung data? 

          });

          //console.log('TEST ONE ~~~~~~~~~~~~~~~~~~~~~~~~~ N1');
          console.log('Clinic ID:', clinicId);
          

          calendar.render();
        });
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ END CALENDAR    

        
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Move Appointment  
    document.addEventListener('DOMContentLoaded', function () {
        // Assuming each form has an ID starting with 'moveForm_'
        var forms = document.querySelectorAll('[id^="moveForm_"]');

        forms.forEach(function (form) {
            var dateInput = form.querySelector('.form-control');
            var timeSelect = form.querySelector('.form-control.time');

            if (dateInput) {
                dateInput.addEventListener('input', function () {
                    var selectedDate = new Date(this.value);
                    var currentDate = new Date();

                    if (selectedDate < currentDate) {
                        //console.log("DATE===Booking ID: ", currentBookingID); // DEBUGGING PURPOSE
                        alert('Please select a future date.');                        
                        this.value = ''; // Clear the input field if the date is invalid
                        return;
                    }

                    // If the date is valid, generate time options based on the selected date
                    generateTimeOptions(timeSelect, selectedDate);
                });
            } else {
                console.error("Date input element not found in the form:", form);
            }
        });
    });

    // Function to generate time options dynamically based on the selected date
    function generateTimeOptions(selectElement, selectedDate) {
        console.log("Generating time options...");

        // Clear existing options
        selectElement.innerHTML = '';

        // Set start and end times based on the selected date
        var startTime = 7;
        var endTime = 17;
        

        // For demonstration purposes, let's assume that times after 12 PM are not available on weekends
        if (selectedDate.getDay() === 0 || selectedDate.getDay() === 6) {
            endTime = 12;
        }

        // Generate options
        for (var i = startTime; i < endTime; i++) {
            var option = document.createElement('option');
            option.value = i.toString().padStart(2, '0') + ':00';
            var endTimeString = (i + 1).toString().padStart(2, '0') + ':00';
            option.text = `${i}:00 - ${endTimeString}`;
            selectElement.appendChild(option);
        }
    }




    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    
    var currentFormElement;
    var currentBookingID;
    
    function openForm(bookingID, event) {
        event.preventDefault(); // Prevent default form submission behavior

        var formId = `myForm_${bookingID}`;
        var formElement = document.getElementById(formId);

        console.log("OPEN FORM formElement ID : ", formElement);
        console.log("OPEN FORM form ID : ", formId);


        if (formElement) {
            formElement.style.display = "block";
            currentFormElement = formElement;
            currentBookingID = bookingID;
    
            //console.log("OPEN Booking ID : ", bookingID);
            console.log("CURRENT Booking ID : ", currentBookingID);
        } else {
            console.error(`Form element with ID ${formId} not found.`);
        }
    } 
    
    function doneForm() {
        console.log("Done Form Function ~~~~~~~~~~~~~~~");
    
        // Use the passed bookingID and formElement here
    
        // Create a new FormData instance with the form element
        //var formId = `myForm_${currentBookingID}`;


        // var formId = document.getElementById('appointmentForm');

        
        // var form = document.body.getAttribute('appointmentForm');

        var formId = document.getElementById("appointmentForm").id;
        // var formId = 'appointmentForm';
        var formElement = document.getElementById(formId);

        console.log("DONE FORM formElement ID : ", formElement);
        console.log("DONE FORM form ID : ", formId);

        if (!formElement) {
            console.error('Form element not found');
            return;
        }
        var formData = new FormData(formElement);

        formData.append('csrfmiddlewaretoken', '{{ csrf_token }}');


        console.log("DONE FORM Booking ID : ", formId);        
    
        console.log("formData: = ",formData);
        // Use the fetch API to send a POST request
        fetch(`/move_appointment/${currentBookingID}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
                // Add any other headers if needed
            },

            body: formData,
            
        })
        .then(response => response.json())
        .then(data => {
            // Handle the response data
        })
        .catch(error => {
            console.error('Error:', error);
        });
    
        //document.getElementById("myForm").style.display = "none";
        document.getElementById("myForm_" + currentBookingID).style.display = "none";
    }


    function closeForm() {
        console.log("Close Form Function ~~~~~~~~~~~~~~~");
    
        var formId = `myForm_${currentBookingID}`;
        var formElement = document.getElementById(formId);
    
        if (formElement) {
            formElement.style.display = "none";
            console.log("CLOSE Booking ID : ", currentBookingID);
        } else {
            console.error(`Form element with ID ${formId} not found.`);
        }
    }