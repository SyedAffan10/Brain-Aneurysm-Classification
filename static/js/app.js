// Header fixed
window.onscroll = function () {
  const docScrollTop = document.documentElement.scrollTop;

  if (window.innerWidth > 991) {
    if (docScrollTop > 100) {
      document.querySelector("header").classList.add("fixed");
    } else {
      document.querySelector("header").classList.remove("fixed");
    }
  }
}

// Navbar links
const navbar = document.querySelector(".navbar");
let navLinks = navbar.querySelectorAll("a");

navLinks.forEach(function (element) {
  element.addEventListener("click", function () {
    navLinks.forEach(link => link.classList.remove("active"));
    this.classList.add("active");
    document.querySelector(".navbar").classList.toggle("show");
  });
});

// Hamburger menu
const hamBurger = document.querySelector(".hamburger");
hamBurger.addEventListener("click", function () {
  document.querySelector(".navbar").classList.toggle("show");
});

// Preview Section 
$(document).ready(function () {
  let fileInput = $("#fileUpload");
  let predictBtn = $("#btn-predict");
  let resultDiv = $("#result");
  let loader = $(".loader");

  // When a new file is selected
  fileInput.change(function () {
      let file = this.files[0];

      if (file) {
          $(".upload-label");  // Show selected file name
          
          predictBtn.show();  // Show predict button again
          resultDiv.hide();   // Hide previous result
          resultDiv.find("span").text("");  // Clear previous result text
      }
  });

  // Prediction button click
  predictBtn.click(function () {
      let formData = new FormData($("#upload-file")[0]);

      $(this).hide();  // Hide button during prediction
      loader.show();   // Show loader

      $.ajax({
          type: "POST",
          url: "/predict",
          data: formData,
          contentType: false,
          processData: false,
          success: function (response) {
              loader.hide();
              resultDiv.show();
              resultDiv.find("span").text(response);  // Display prediction result
              // predictBtn.show(); // Show predict button again after result
          },
          error: function () {
              loader.hide();
              resultDiv.show();
              resultDiv.find("span").text("Error in prediction. Try again.");
              predictBtn.show(); // Show predict button again in case of error
          }
      });
  });
});
