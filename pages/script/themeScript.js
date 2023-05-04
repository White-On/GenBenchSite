import { HeatMap } from "./heatMapChart.js";

// let themeName = document.getElementById('entry-title').innerHTML;

let width = window.innerWidth * 0.5;
let height = window.innerHeight * 0.5;

console.log(importedData)

let chart;

chart = HeatMap(importedData, {
    x: d => d.libraryName,
    y: d => d.taskName,
    value: d => d.results,

    width: width,
    height: height,

    margin: { top: 30, right: 0, bottom: 0, left: 120 },
    
});

document.body.appendChild(chart);

let themeName = document.getElementById('entry-title').innerHTML;
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




