var $star_rating = $(".star-rating .fa");

var SetRatingStar = function() {
    return $star_rating.each(function() {
        if (
            parseInt($star_rating.siblings("input.rating-value").val()) >=
            parseInt($(this).data("rating"))
        ) {
            return $(this).removeClass("fa-star-o").addClass("fa-star");
        } else {
            return $(this).removeClass("fa-star").addClass("fa-star-o");
        }
    });
};

$star_rating.on("click", function() {
    $star_rating.siblings("input.rating-value").val($(this).data("rating"));
    return SetRatingStar();
});

SetRatingStar();
$(document).ready(function() {});

function validateForm() {
    var x = document.forms["RatingForm"]["rating"].value;
    if (x == "0") {
        alert("Invalid Input");
        return false;
    }
}
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