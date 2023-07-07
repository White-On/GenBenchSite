import { HeatMap } from "./heatMapChart.js";

// let themeName = document.getElementById('entry-title').innerHTML;

let width = window.innerWidth * 1;
let height = window.innerHeight * 1;

console.log(importedData)

let chart;

chart = HeatMap(importedData, {
    x: d => d.libraryName,
    y: d => d.taskName,
    value: d => d.results,

    width: width,
    height: height,

    margin: { top: 30, right: 0, bottom: 0, left: 250 },
    yLabel: "Task",
    
});

document.body.appendChild(chart);

// let themeName = document.getElementById('entry-title').innerHTML;
console.log(themeName);
//we want to make the navActive class active on the library page 
let navActive = document.getElementById(themeName + "-nav");

// we want to change the color of the active nav element
navActive.classList.add("active");
// we now go up to the parent over and over again until we reach the nav element
// and we turn all submenu class to expand  
while (navActive.tagName != "NAV") {
    if (navActive.classList.contains("collapse")) {
        navActive.classList.replace("collapse", "expand");
        navActive.parentElement.getElementsByClassName("arrow")[0].style.transform = "rotate(0deg)";
    }
    navActive = navActive.parentElement;
}

// we now make the submenu of the active nav element visible
navActive = document.getElementById(themeName + "-nav");
let subMenu = navActive.parentElement.parentElement.getElementsByClassName("subMenu")[0];
if (subMenu.classList.contains("collapse")) {
    subMenu.classList.replace("collapse", "expand");
    subMenu.parentElement.getElementsByClassName("arrow")[0].style.transform = "rotate(0deg)";
}




