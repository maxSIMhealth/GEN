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
