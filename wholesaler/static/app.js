document.addEventListener("DOMContentLoaded", function () {
    // Target buttons/links with a common class
    const targets = document.querySelectorAll(".remove-body-bg, form[action$='/logout/'] button");

    targets.forEach(element => {
        element.addEventListener("click", function () {
            // Remove the class from <body>
            document.body.classList.remove("body_bg");

            // Save the change in localStorage (to persist on page reload)
            localStorage.setItem("remove_body_bg", "true");
        });
    });

    // On page load: check if class should be removed
    if (localStorage.getItem("remove_body_bg") === "true") {
        document.body.classList.remove("body_bg");
    }
});

// const customMessage = "Please select Buyer or Seller";

//   // Add event listener to all buttons with class 'regi'
//   document.querySelectorAll(".regi").forEach(button => {
//     button.addEventListener("click", () => {
//       alert(customMessage);
//     });
//   });

const popup = document.getElementById("popup");

  // Show popup on click of any .regi button
  document.querySelectorAll(".regi").forEach(button => {
    button.addEventListener("click", () => {
      popup.style.display = "flex";
    });
  });

  // Function to close the popup only when close button is clicked
  function closePopup() {
    popup.style.display = "none";
  }