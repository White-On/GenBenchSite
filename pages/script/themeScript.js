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

    margin: { top: 50, right: 50, bottom: 50, left: 120 },
    
});

document.body.appendChild(chart);

let themeName = document.getElementById('entry-title').innerHTML;
//we want to make the navActive class active on the library page 
let navActive = document.getElementById(themeName + "-nav");
navActive.classList.add("active");




