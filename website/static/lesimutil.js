function networkErrorMsg(response, err) {
    return `${err} Network response was not ok: ${response.statusText} (${response.status}) \n\nPlease try again. If the problem persists, contact support.`
}


function makeErrorMsg(error) {
    if (error && error.stack && error.message) {
        // It's probably an error object (duck typing)
        return error.message + "\n\n-----------\nStack trace:\n\n" + error.stack;
    }
    else {
        return error;
    }
}


// If there are any flash divs displayed, make them fade out
// XXX Duplicated from my_scripts.js
function makeFlashesFade() {
    var flashDivs = document.getElementsByClassName("alert");
    for (var flashDiv of flashDivs) {
        // To remove the element from DOM when faded out
        flashDiv.addEventListener('transitionend', () => flashDiv.remove());

        // Start fading out after 1000 ms
        setTimeout(function() {
            flashDiv.style.opacity = '0';
        }, 1000);
    }
}


/*
 * Programmatically create the same flash as in base.html
 *
 * <div class="alert alert-warning alert-dismissible fade show">
 *   {{ message }}
 *   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
 * </div>
 */
function displayFlashMessage(msg) {
    const flashDiv = document.createElement('div');
    flashDiv.className = "alert alert-success alert-dismissible fade show flash-close-btn tofadeout";
    flashDiv.addEventListener('transitionend', () => flashDiv.remove());  // To remove the element from DOM when faded out
    const flashDivButton = document.createElement('button');
    flashDivButton.type = "button";
    flashDivButton.className = "btn-close";
    flashDivButton.setAttribute("data-bs-dismiss", "alert");
    flashDivButton.setAttribute("aria-label", "Close");
    flashDiv.innerHTML = msg;
    flashDiv.appendChild(flashDivButton);

    // Insert the flash div efter the navbar, before {% block content %}
    flashesDiv = document.getElementById("flashes");
    flashesDiv.appendChild(flashDiv);

    // Start fading out after 1000 ms
    setTimeout(function() {
        flashDiv.style.opacity = '0';
    }, 2000);
}
