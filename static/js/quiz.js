var slideInitialValue = 1;
var slideIndex = slideInitialValue;
var slides = document.getElementsByClassName("quiz-item");
var dots = document.getElementsByClassName("dot");

showSlides(slideIndex);

function updateNavigationText() {
  document.getElementById("quiz-navigation-position").innerHTML = slideIndex + " of " + slides.length;
}

function previousSlide() {
  if (slideIndex > slideInitialValue) {
    slideIndex--;
    showSlides(slideIndex);
  } else {
    console.log(slideIndex + " is the beginning of the slide: " + slideInitialValue + " of " + slides.length);
  }
}

function nextSlide() {
  if (slideIndex < slides.length) {
    slideIndex++;
    showSlides(slideIndex);
  } else {
    console.log(slideIndex + " is the end of the slide length: " + slideInitialValue + " of " + slides.length);
  }
}

function slideNavLinkEnable(object) {
  var element = document.querySelector(object);
  element.classList.remove("disabled");
  element.querySelector("a").removeAttribute("tabindex");
  element.querySelector("a").removeAttribute("aria-disabled");
}

function slideNavLinkDisable(object) {
  var element = document.querySelector(object);
  element.classList.add("disabled");
  element.querySelector("a").setAttribute("tabindex","-1");
  element.querySelector("a").setAttribute("aria-disabled","true");
}

function goToSlide(slideNumber) {
  var slideRangeCheck = checkSlideRange(slideNumber);
  if (slideRangeCheck) {
    slideIndex = slideNumber;
    showSlides(slideNumber);
  } else {
    console.warn("Slide number out of range");
  }
}

function checkSlideRange(slideNumber) {
  if (slideNumber > slides.length || slideNumber < slideInitialValue) {
    return false;
  } else {
    return true;
  }
}

function showSlides(slideNumber) {
  var i;

  // console.log("current slide " + slideNumber);

  var slideRangeCheck = checkSlideRange(slideNumber);

  if (slideRangeCheck) {
    for (i = 0; i < slides.length; i++) {
      slides[i].style.display = "none";
    }

    // for (i = 0; i < dots.length; i++) {
    //   dots[i].className = dots[i].className.replace(" active", "");
    // }

    slides[slideNumber-1].style.display = "block";
    // dots[slideIndex-1].className += " active";

    updateNavigationText();

    if (slideNumber > slideInitialValue) {
      slideNavLinkEnable("#quiz-navigation-previous");
    } else if (slideNumber == slideInitialValue) {
      slideNavLinkDisable("#quiz-navigation-previous");
    }

    if (slideNumber == slides.length) {
      slideNavLinkDisable("#quiz-navigation-next");
    } else if (slideNumber < slides.length) {
      slideNavLinkEnable("#quiz-navigation-next");
    }
  } else {
    console.warn("Slide number out of range");
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
  event.preventDefault();
}
