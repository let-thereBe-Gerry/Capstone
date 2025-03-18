
document.addEventListener('DOMContentLoaded', function () {
    const checkboxes = document.querySelectorAll('.row-checkbox');
    const selectAllCheckbox = document.getElementById('select-all-checkbox');
    const updateButton = document.querySelector('.btn-success');
    const selectedUserIDs = [];
    const userToBeUpdate = [];

    selectAllCheckbox.addEventListener('change', function () {
        checkboxes.forEach(function (checkbox) {
            checkbox.checked = selectAllCheckbox.checked;
            const userID = checkbox.dataset.userid;
            if (selectAllCheckbox.checked && !selectedUserIDs.includes(userID)) {
                selectedUserIDs.push(userID);
            } else if (!selectAllCheckbox.checked) {
                const index = selectedUserIDs.indexOf(userID);
                if (index > -1) {
                    selectedUserIDs.splice(index, 1);
                }
            }
        });
    });

    checkboxes.forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
            const userID = this.dataset.userid;
            console.log(this.dataset)
            console.log('user id')
            if (this.checked) {
                selectedUserIDs.push(userID);
            } else {
                const index = selectedUserIDs.indexOf(userID);
                if (index > -1) {
                    selectedUserIDs.splice(index, 1);
                }
            }
            selectAllCheckbox.checked = checkboxes.length === selectedUserIDs.length;
        });
    });

    // const ids = document.getElementById('data-userid');
      updateButton.addEventListener('click', function (event) {
        // Prevent form submission
        event.preventDefault();

        if (selectedUserIDs.length === 1) {
          const selectedUserID = selectedUserIDs[0];
          // Redirect to the update page with the selected user ID
          const url = '/admin_UpdateUser/?userID=' + encodeURIComponent(selectedUserID);
          window.location.href = url;
        //   userToBeUpdate.push(userID);

          console.log('If')
          console.log(userToBeUpdate)
        } else if (selectedUserIDs.length > 1) {
          console.log(selectedUserIDs)
          // Show an alert if multiple checkboxes are selected
          alert('Please select only one user to update.');
        } else {
          console.log(selectedUserIDs)
          console.log('else')
          // Show an alert if no checkbox is selected
          alert('Please select a user to update.');
        }
      });


    const deleteButton = document.getElementById('delete-btn');
    deleteButton.addEventListener('click', function () {
        console.log(selectedUserIDs); // Array containing selected userIDs

        // Send the selected user IDs to the server for deletion
        fetch('/delete_users/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'), // Include the CSRF token in the request headers
            },
            body: JSON.stringify({ user_ids: selectedUserIDs.join(',') }), // Convert the array to a comma-separated string
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message); // Server response message
            // Refresh the page or update the user list as needed after deletion
            location.reload(); // Example: reload the page to show updated user list
        })
        .catch(error => {
            console.error('Error deleting users:', error);
        });
    });

    // Function to get the CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === name + '=') {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});