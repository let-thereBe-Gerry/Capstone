    document.addEventListener('DOMContentLoaded', function () {
        let mapOptions = {
            center: [13.93433842907902, 121.61332264989602],
            zoom: 15
        };

        let map = new L.map('map', mapOptions);

        let layer = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
        map.addLayer(layer);

        // Fetch clinic data from the API endpoint
        fetch('/api/clinics/')
            .then(response => response.json())
            .then(clinicsData => {
                let markers = [];

                for (let i = 0; i < clinicsData.length; i++) {
                    let clinic = clinicsData[i];
                    let latitude = clinic.latitude;
                    let longitude = clinic.longitude;

                    // Check if the latitude and longitude are valid
                    if (latitude !== null && longitude !== null) {
                        // Create a marker for each clinic using the fetched latitude and longitude
                        let marker = new L.Marker([latitude, longitude]).addTo(map);

                        // Create the popup content with clinic information and a button
                        let popupContent = `
                            <strong>${clinic.clinicName}</strong><br>
                            Address: ${clinic.clinicAddress}<br>
                            Contact Number: ${clinic.clinicNumber}<br>
                            <button class="popup-button" onclick="handleButtonClick(${clinic.clinicID})">Make an Appointment</button>
                            <button class="popup-button" onclick="redirectToClinicProfile(${clinic.clinicID})">View Clinic</button>
                        `;

                        // Bind the popup to the marker
                        marker.bindPopup(popupContent);

                        markers.push(marker); // Store the marker in the markers array
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

    function redirectToClinicProfile(clinicID) {
        window.location.href = `/index_ClinicsProfile/${clinicID}/`;
    }


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
                alert("Please Log In First");
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









