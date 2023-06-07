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
        }, 1000);
        
    }
}
