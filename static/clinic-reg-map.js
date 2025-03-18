document.addEventListener('DOMContentLoaded', function () {
    let mapOptions = {
        center: [13.93433842907902, 121.61332264989602],
        zoom: 15
    };

    let map = new L.map('map', mapOptions);

    let layer = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
    map.addLayer(layer);

    let markers = [];

    map.on('click', function (e) {
        let latitude = e.latlng.lat;
        let longitude = e.latlng.lng;

        markers.forEach(marker => {
            map.removeLayer(marker);
        });

        markers = [];

        let newMarker = new L.Marker([latitude, longitude]);

        newMarker.addTo(map);

        markers.push(newMarker);

        console.log('Clicked Location - Latitude: ' + latitude + ', Longitude: ' + longitude);

        // Reverse Geocoding using Nominatim API
        fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${latitude}&lon=${longitude}`)
            .then(response => response.json())
            .then(data => {
                if (data.display_name) {
                    // Update the clinic address input field with the reverse geocoded address
                    document.getElementById('clinicAddress').value = data.display_name;
                } else {
                    console.error('Unable to fetch address from Nominatim API');
                }
            })
            .catch(error => {
                console.error('Error fetching address from Nominatim API:', error);
            });
    });

    document.getElementById('contactForm').addEventListener('submit', function (event) {
        event.preventDefault();

        // Get form data
        let formData = new FormData(this);

        // Add the latitude and longitude from the last clicked location
        formData.append('latitude', markers[0].getLatLng().lat);
        formData.append('longitude', markers[0].getLatLng().lng);

        // Send the selected Ophthalmologist's username to the backend
        formData.append('users_name', document.getElementById('usernames-dropdown').value);

        // Send the form data to the backend
        fetch('/location/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ---- eyy');
            }
            return response.json();
        })
        .then(data => {
            console.log('Form data sent to backend:', data);
            // Optionally, you can redirect or perform other actions after successful submission
        })
        .catch(error => {
            console.error('Error sending form data to backend:', error);
        });
        console.log('Form Data:', formData);
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Check if this cookie string begins with the name we want
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    fetch('/api/clinics/')
        .then(response => response.json())
        .then(clinicsData => {
            let markers = [];

            for (let i = 0; i < clinicsData.length; i++) {
                let clinic = clinicsData[i];
                let latitude = clinic.latitude;
                let longitude = clinic.longitude;

                if (latitude !== null && longitude !== null) {
                    
                    let marker = new L.Marker([latitude, longitude]).addTo(map);

                    let popupContent = `
                        <strong>${clinic.clinicName}</strong><br>
                        Address: ${clinic.clinicAddress}<br>
                        Contact Number: ${clinic.clinicNumber}<br>
                        <button class="popup-button" onclick="handleButtonClick(${clinic.clinicID})">Make an Appointment</button>
                    `;

                    marker.bindPopup(popupContent);

                    markers.push(marker); 
                } else {
                    console.log('Invalid latitude or longitude for clinic:', clinic);
                }
            }

            checkAuthenticationForAllMarkers();
        })
        .catch(error => {
            console.error('Error fetching clinic data:', error);
        });
    
});

console.log('Testttttttttt Two');

function checkAuthenticationForAllMarkers() {
let clinicButtons = document.querySelectorAll('.popup-button');
clinicButtons.forEach(button => {
    let clinicID = button.getAttribute('data-clinicID');
    checkAuthentication(clinicID);
});
}

function checkAuthentication(clinicID) {
fetch(`/check_authentication/?clinic_id=${clinicID}`) // Pass the clinicID as a query parameter
    .then(response => response.json())
    .then(data => {
        if (data.authenticated) {
            // User is authenticated, redirect to the booking page
            const url = `/clinic/${clinicID}/booking_Page/`;        
            window.location.href = url;
        } else {
            window.location.href = '/login/';
        }
    })
    .catch(error => {
        console.error('Error checking authentication:', error);
    });
}

// Function to handle the button click
function handleButtonClick(clinicID) {
checkAuthentication(clinicID);
}

