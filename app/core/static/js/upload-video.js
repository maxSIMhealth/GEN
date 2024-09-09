const form = document.getElementById("form-upload-video")
const progressBar = document.getElementById("progress-bar")
const progressBarValue = document.getElementById("progress-bar-value")
const submitButton = document.getElementById("submit-id-submit")
const uploadStatus = document.getElementById("upload-status")
const log = document.getElementById("progress-status")

submitButton.addEventListener("click", event => {
  uploadFile();
  submitButton.disabled = true;
})

// form handlers

function progressHandler(event) {
  uploadStatus.style.display = "block";

  let percentComplete = Math.round((event.loaded / event.total) * 100);
  progressBar.style.width = percentComplete + '%';
  progressBarValue.innerText = percentComplete + '%';

  if (percentComplete === 100) {
    progressBar.textContent = 'Upload Complete';
  }
}

function errorHandler(event) {
  log.innerText = `Upload failed: ${event.target.responseText}`;
}

function abortHandler(event) {
  log.innerText = `Upload aborted: ${event.target.responseText}`;
}

// file upload

function uploadFile() {
  let formData = new FormData(form);
  let xhr = new XMLHttpRequest();

  progressBar.style.width = '0';
  progressBarValue.innerText = "0%";

  xhr.upload.addEventListener("progress", progressHandler, false);
  xhr.addEventListener("error", errorHandler, false);
  xhr.addEventListener("abort", abortHandler, false);
  xhr.addEventListener("loadend", function () {
    if (xhr.status === 200) {
      window.location.href = '{% url "section" course.pk section.pk %}';
    } else {
      alert('Upload failed')
    }
  });

  xhr.open("POST", '{% url "upload_video" course.pk section.pk %}', true);
  xhr.send(formData);
}
