function uploadSubmitted() {
  var formActions = document.getElementById("submit-id-submit").parentElement; // select div that contains form's action buttons
  var uploadMessage = gettext("Uploading. Please wait.");
  formActions.innerHTML = "<div class=\"alert alert-warning\" role=\"alert\"><span class=\"spinner-border spinner-border-sm mr-2\" role=\"status\" aria-hidden=\"true\"></span>" + uploadMessage + "</div>";

  return true;
}

const form = document.getElementById("form-upload-video");
form.addEventListener('submit', uploadSubmitted);
