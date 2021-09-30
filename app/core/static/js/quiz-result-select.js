const resultsSelect = document.getElementById("results_select");
const currentUrl = window.location.search;
const urlParams = new URLSearchParams(currentUrl);
const currentResultValue = urlParams.get('student');
for (let option of resultsSelect.options) {
    if (option.value === currentResultValue) {
        option.selected = true;
    }
}
function navigateResult() {
    console.log("?student=" + this.value)
    window.location.href = "?student=" + this.value;
}
resultsSelect.onchange = navigateResult;