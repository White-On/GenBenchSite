import {LineChart} from './dynamicPlot.js';
import {Histogram} from './histogram.js';
import {GroupedBarChart} from './groupedBarChart.js';

// to get the Task Name that we want to plot we have 2 options:

// 1. get the task name from an element in the html page
// let TaskName = document.querySelector('[id^="Task"]').id;
// console.log("TaskName = " + TaskName);

// 2. get the task name from the url
// var path = window.location.pathname;
// var page = path.split("/").pop().split(".")[0];
// console.log( page );

//3. get the task name from the title of the page
let TaskName = document.getElementById('entry-title').innerHTML;

let element = document.getElementById(TaskName);

let width = window.innerWidth * 0.4;
let height = window.innerHeight * 0.75;


let chart;
// check if the arguments are numbers or not to sort the data if needed 
if (isNaN(importedData[0].arguments)){
    let orderingFunction = (a, b) => d3.ascending(a.runTime, b.runTime);
    importedData.sort(orderingFunction);
}

chart = GroupedBarChart(importedData, {
    values: d => d.runTime,
    categories: d => d.arguments,
    inerClass: d => d.libraryName,

    width: width,
    height: height,

    xLabel: "Arguments →",
    yLabel: "Run Time (ms) ↑",

    activationFunction: handleClickToPrintCode,

    margin: { top: 40, right: 50, bottom: 100, left: 50 },
    
});

function handleClickToPrintCode(elements) {
    console.log(elements);
    if (elements.length == 0) {
        document.getElementById("codeLib1").innerHTML = "";
        document.getElementById("codeLib2").innerHTML = "";
        return;
    }
    else if (elements.length == 1) {
        document.getElementById("codeLib1").innerHTML = code[elements[0]];
        document.getElementById("codeLib2").innerHTML = "";
        return;
    }
    else if (elements.length == 2) {
        document.getElementById("codeLib1").innerHTML = code[elements[0]];
        document.getElementById("codeLib2").innerHTML = code[elements[1]];
        return;
    }
}

element.appendChild(chart);


// document.body.innerHTML += code["pgmpy"]