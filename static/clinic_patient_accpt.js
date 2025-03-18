document.addEventListener('DOMContentLoaded', function () {
    const appointmentForm = document.getElementById('appointmentForm');
    const acceptButtons = document.querySelectorAll('.accept-btn');
    const declineButtons = document.querySelectorAll('.decline-btn');
    // const appointmentElement = document.getElementById(`appointment_${bookingId}`);

    appointmentForm.addEventListener('click', function (event) {
        const target = event.target;

        // Check if the clicked element is an accept or decline button
        if (target.classList.contains('accept-btn') || target.classList.contains('decline-btn')) {
            event.preventDefault();
            // Find the closest parent element with the ID starting with 'appointment_'
            const appointmentElement = target.closest('[id^="appointment_"]');
            
            console.log('TEST ALPHA ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ A');
            if (appointmentElement) {
                console.log('TEST BRAVO ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ B');
                const bookingId = target.getAttribute('data-booking-id');
                updateBookingStatus(bookingId, target.classList.contains('accept-btn') ? 'accept' : 'decline', appointmentElement);
                appointmentElement.style.display = 'none';
                //appointmentElement.style.display = Booking.is_hidden ? 'none' : 'block';
            } else {
                console.log('TEST CHARLIE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ C');
                console.error('Parent element not found for button:', target);
            }
            event.stopPropagation();
        }
    });

    function updateBookingStatus(bookingId, status, appointmentElement) {
        console.log('Updating booking status...');
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
        // const appointmentElement = document.getElementById(`appointment_${bookingId}`); // kahit nandito ito, naka null pa rin
        // console.log('CSRF Token:', csrfToken);
        
    
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