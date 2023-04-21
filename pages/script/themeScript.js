import { HeatMap } from "./heatMapChart.js";

let width = window.innerWidth * 0.8;
let height = window.innerHeight * 0.8;

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