var paginationInitialValue = 1;
var paginationIndex = paginationInitialValue;
var pagination = document.getElementsByClassName("quiz-item");
// var dots = document.getElementsByClassName("dot");

showPagination(paginationIndex);

function updateNavigationText() {
  document.getElementById("quiz-navigation-position").innerHTML = paginationIndex + " of " + pagination.length;
}

function previousPaginationItem() {
  if (paginationIndex > paginationInitialValue) {
    paginationIndex--;
    showPagination(paginationIndex);
  } else {
    console.log(paginationIndex + " is the beginning of the pagination: " + paginationInitialValue + " of " + pagination.length);
  }
}

function nextPaginationItem() {
  if (paginationIndex < pagination.length) {
    paginationIndex++;
    showPagination(paginationIndex);
  } else {
    console.log(paginationIndex + " is the end of the pagination length: " + paginationInitialValue + " of " + pagination.length);
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
    console.warn("Pagination item number out of range");
  }
}

function checkPaginationRange(paginationItemNumber) {
  return !(paginationItemNumber > pagination.length || paginationItemNumber < paginationInitialValue);
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
      paginationNavLinkEnable("#quiz-navigation-previous");
    } else if (paginationItemNumber === paginationInitialValue) {
      paginationNavLinkDisable("#quiz-navigation-previous");
    }

    if (paginationItemNumber === pagination.length) {
      paginationNavLinkDisable("#quiz-navigation-next");
    } else if (paginationItemNumber < pagination.length) {
      paginationNavLinkEnable("#quiz-navigation-next");
    }
  } else {
    console.warn("Pagination item number out of range");
  }
}

function toggleCheckboxes(event, action) {
  var parent = event.closest('ul');
  var checkboxes = parent.querySelectorAll('input[type=checkbox]');
  //console.log(checkboxes);
  if (action === "on") {
    checkboxes.forEach(function(item) {
    item.checked = true;
  	});
  } else {
    checkboxes.forEach(function(item) {
    item.checked = false;
  	});
  }
  event.preventDefault();
}
