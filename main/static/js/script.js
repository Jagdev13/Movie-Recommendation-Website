// Function to toggle the visibility of password fields
function togglePassword(fieldId) {
    console.log("togglePassword called with fieldId:", fieldId); // Debugging: log when function is called
    const field = document.getElementById(fieldId);

    // Check if the field is found and its type
    if (field) {
        console.log("Field found. Current type:", field.type); // Log field type before toggle
        field.type = field.type === "password" ? "text" : "password";
        console.log("New type after toggle:", field.type); // Log field type after toggle
    } else {
        console.log("Field not found for ID:", fieldId); // Log if field not found
    }
}


// Function For poping the msg after login
    document.querySelector("#loginModal form").onsubmit = function(event) {
        event.preventDefault(); // Prevent default form submission
        const form = event.target;
        const formData = new FormData(form);

        fetch(form.action, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Remove any existing error message
                document.querySelector("#loginModal .modal-body").querySelector(".alert")?.remove();

                // Create and display a success message in the modal
                const successMessage = document.createElement("div");
                successMessage.className = "alert alert-success text-center";
                successMessage.textContent = `Logged in as ${data.username}`;
                document.querySelector("#loginModal .modal-body").appendChild(successMessage);

                // Set a timer for 3 seconds, then redirect to the homepage
                setTimeout(() => {
                    window.location.href = '/'; // Redirect to homepage
                }, 2000);
            } else {
                // Display error message in modal if login fails
                document.querySelector("#loginModal .modal-body").querySelector(".alert")?.remove();
                const errorAlert = document.createElement("div");
                errorAlert.className = "alert alert-light";
                errorAlert.textContent = data.error_message;
                document.querySelector("#loginModal .modal-body").appendChild(errorAlert);
            }
        });
    };

