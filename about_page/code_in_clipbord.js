// we select  all the code sections in the page
let codeElements = document.getElementsByTagName("code");

// we add a message to the user
// we create a div element
let div = document.createElement("div");
// we add a class to the div element
div.classList.add("tooltips_clipboard");
// we add the div element to the body
document.body.appendChild(div);
// we add the message to the div element
div.innerText = "📌 Copied to clipboard";

// we add onclick event to each code section
for (let i = 0; i < codeElements.length; i++) {
    codeElements[i].onclick = function () {
        // we add the innerText of the code section to the clipboard
        navigator.clipboard.writeText(codeElements[i].innerText)
        // make the message visible
        div.style.visibility = "visible";
        div.style.opacity = 1;
        // make the message fadeout after 1 second
        setTimeout(function () {
            div.style.opacity = 0;
            div.style.visibility = "collapse";
        }, 1000);
        
    }
}

// we create a element when we hover over the code section
let span = document.createElement("span");
// we add a class to the span element
span.classList.add("tooltiptext_clipboard");
// we add the span element to the body
document.body.appendChild(span);
// we add the message to the span element
span.innerText = "📌";

// we add onmouseover event to each code section
for (let i = 0; i < codeElements.length; i++) {
    codeElements[i].onmouseover = function () {
        // change the position of the message
        span.style.top = codeElements[i].offsetTop - 5 + "px";
        span.style.right = codeElements[i].offsetLeft - 40 + "px";
        // make the message visible
        span.style.visibility = "visible";
        span.style.opacity = 1;
    }
}

// we add onmouseout event to each code section
for (let i = 0; i < codeElements.length; i++) {
    codeElements[i].onmouseout = function () {
        // make the message invisible
        span.style.visibility = "collapse";
        span.style.opacity = 0;
        
    }
}


