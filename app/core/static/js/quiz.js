var paginationInitialValue = 1;
var paginationIndex = paginationInitialValue;
var pagination = document.getElementsByClassName("pagination-item");
const quizRequireAnswers = JSON.parse(document.getElementById('quiz_require_answers').textContent); // FIXME: checking required answers this way should be temporary and done using django forms validation
// var dots = document.getElementsByClassName("dot");

showPagination(paginationIndex);

function updateNavigationText() {
  document.getElementById("pagination-navigation-position").innerHTML = paginationIndex + " of " + pagination.length;
}

 // FIXME: checking required answers this way should be temporary and done using django forms validation
function checkRequiredAnswer() {
  var questionNumber = paginationIndex - 1;
  var question = pagination[questionNumber];

  // console.log("question number: " + questionNumber);
  var items = question.querySelectorAll("input, textarea, select");
  // console.log(question);
  answers = [];
  if (items.length > 0) {
    items.forEach(function(item) {
      // console.log(item);
      // console.log("is checked? " + item.checked)
      answers.push(item.checked);
    })
    // console.log(answers);
    if (!answers.includes(true)) {
      // console.log("WARNING: user did not answer a question " + questionNumber);
      return false;
    } else {
      return true;
    }
  } else {
    return true;
  }
}

function previousPaginationItem() {
  if (paginationIndex > paginationInitialValue) {
    paginationIndex--;
    showPagination(paginationIndex);
  } else {
    // console.log(paginationIndex + " is the beginning of the pagination: " + paginationInitialValue + " of " + pagination.length);
  }
}

function nextPaginationItem() {
  // FIXME: checking required answers this way should be temporary and done using django forms validation
  if (quizRequireAnswers) {
    var answerRequiredFullfilled = checkRequiredAnswer();
  } else {
    var answerRequiredFullfilled = true;
  }

  if (answerRequiredFullfilled) {
    if (paginationIndex < pagination.length) {
      paginationIndex++;
      showPagination(paginationIndex);
    } else {
      // console.log(paginationIndex + " is the end of the pagination length: " + paginationInitialValue + " of " + pagination.length);
    }
  } else {
    alert(gettext("Please answer the question."));
  }

}

function paginationNavLinkEnable(object) {
  var element = document.querySelector(object);
  element.classList.remove("disabled");
  element.querySelector("a").removeAttribute("tabindex");
  element.querySelector("a").removeAttribute("aria-disabled");
}

function paginationNavLinkDisable(object) {
  var element = document.querySelector(object);
  element.classList.add("disabled");
  element.querySelector("a").setAttribute("tabindex","-1");
  element.querySelector("a").setAttribute("aria-disabled","true");
}

function goToPaginationItem(paginationItemNumber) {
  var paginationRangeCheck = checkPaginationRange(paginationItemNumber);
  if (paginationRangeCheck) {
    paginationIndex = paginationItemNumber;
    showPagination(paginationItemNumber);
  } else {
    // console.warn("Pagination item number out of range");
  }
}

function checkPaginationRange(paginationItemNumber) {
  if (paginationItemNumber > pagination.length || paginationItemNumber < paginationInitialValue) {
    return false;
  } else {
    return true;
  }
}

function showPagination(paginationItemNumber) {
  var i;

  var paginationRangeOk = checkPaginationRange(paginationItemNumber);

  if (paginationRangeOk) {
    for (i = 0; i < pagination.length; i++) {
      pagination[i].style.display = "none";
    }

    // for (i = 0; i < dots.length; i++) {
    //   dots[i].className = dots[i].className.replace(" active", "");
    // }

    pagination[paginationItemNumber-1].style.display = "block";
    // dots[paginationIndex-1].className += " active";

    updateNavigationText();

    if (paginationItemNumber > paginationInitialValue) {
      paginationNavLinkEnable("#pagination-navigation-previous");
    } else if (paginationItemNumber == paginationInitialValue) {
      paginationNavLinkDisable("#pagination-navigation-previous");
    }

    if (paginationItemNumber == pagination.length) {
      paginationNavLinkDisable("#pagination-navigation-next");
    } else if (paginationItemNumber < pagination.length) {
      paginationNavLinkEnable("#pagination-navigation-next");
    }
  } else {
    // console.warn("Pagination item number out of range");
  }
}

function toggleCheckboxes(event, action) {
  var parent = event.closest('ul');
  var checkboxes = parent.querySelectorAll('input[type=checkbox]');
  //console.log(checkboxes);
  if (action == "on") {
    checkboxes.forEach(function(item) {
    item.checked = true;
  	});
  } else {
    checkboxes.forEach(function(item) {
    item.checked = false;
  	});
  }
  // event.preventDefault();
}
