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


// const seperate = id => {
//     const element = document.getElementById(id),
//           text = element.innerText.split("");
//     element.innerText = "";
//     text.forEach(letter =>{
//       const span = document.createElement("span");
//       span.className = "letter";
//       span.innerText = letter;
//       element.appendChild(span);
//     });
// }

// seperate("main-title");

const caracters = "ABCDEFGHIJKMNLOPQRSTUVWXYZ";

const element = document.getElementById("main-title");
element.onmouseover = (event) => {
    glitch("main-title");
};

const glitch = id => {
    const glitchElement = document.getElementById(id);
    let iterations = -5;
    // a list going to 0 to the length of the text
    const letterToFix = glitchElement.innerText.split("").map((letter, index) => index);
    const letterOrderToFix = letterToFix.sort(() => Math.random() - 0.5);
    const interval = setInterval(() => {
      glitchElement.innerText = glitchElement.innerText
        .split("")
        .map((letter, index) => {
            // create the list of the n first letters to fix
            let letterIndex = [];
            if (iterations > 0) {
                letterIndex =  letterOrderToFix.slice(0, iterations);
            }
            
            if (letterIndex.includes(index)) {
                return glitchElement.dataset.value[index];
            }
            return caracters[Math.floor(Math.random() * 26)];
        })
        .join("");
      if (iterations >= glitchElement.dataset.value.length) {
        clearInterval(interval);
      }

      iterations += 1 / 3;
    }, 30);
}

// every 20 seconds we glitch the title
setInterval(function () {
    glitch("main-title");
}, 20000);

const blob = document.getElementById("blob");

document.addEventListener('mousemove', (e) => {
    // blob.style.left = e.pageX + 'px';
    // blob.style.top = e.pageY + 'px';

    blob.animate({
        left: `${e.pageX}px`,
        top: `${e.pageY}px`
    }, {
        duration: 10000,
        fill: "forwards"
    });
});

