// import myJson from '../data.json' assert { type: 'json' };
// import myJson from '../results.json' assert { type: 'json' };

import {LineChart} from './dynamicPlot.js';
import {Histogram} from './histogram.js';
import {GroupedBarChart} from './groupedBarChart.js';

// const data = await myJson;

// let AllLibraryName = Object.keys(data);
// console.log("AllLibraryName = " + AllLibraryName);

// let AllTaskName = Object.keys(data[AllLibraryName[0]]);
// console.log("AllTaskName = " + AllTaskName);

// let ColorList = ["red", "blue", "green", "yellow", "orange", "purple", "pink", "brown", "grey", "black"]
// let colorPalette = {};
// for (let i = 0; i < AllLibraryName.length; i++) {
//     colorPalette[AllLibraryName[i]] = ColorList[i];
// }

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

// let width = element.clientWidth;
// let height = element.clientHeight;

let width = window.innerWidth * 0.8;
let height = window.innerHeight * 0.8;

console.log(importedData)

let chart;
let orderingFunction = (a, b) => d3.ascending(a.runTime, b.runTime);
importedData.sort(orderingFunction);
chart = GroupedBarChart(importedData, {
    values: d => d.runTime,
    categories: d => d.arguments,
    inerClass: d => d.libraryName,

    width: width,
    height: height,

    margin: { top: 50, right: 50, bottom: 50, left: 50 },
    
});

// let intermediateData = FormatedData(data, TaskName);
// console.log(intermediateData);
// if (intermediateData.length == AllLibraryName.length) {
//     let intermediateDataSorted = intermediateData.sort(orderingFunction);
//     chart = Histogram(intermediateDataSorted, {
//         x: d => d.libraryName,
//         y: d => d.runTime,
//         color: d => colorPalette[d],
//         width: width,
//         height: height,
//         yLabel: "Run Time (ms) ↑",
//         labelFontSize: 30,

//         marginLeft: 80,
//         marginTop: 40,

//         legend: true,

//     });
// }
// else{
//     chart =  LineChart(intermediateData, {
//         x: d => d.arguments,
//         y: d => d.runTime,
//         z: d => d.libraryName,
//         yLabel: "Run Time (ms) ↑",
//         width: width,
//         height: height,
//         color: d => colorPalette[d],
//         labelFontSize: 30,
//         legendFontSize: 30,
//         tooltipFontSize: 30,
        
//         marginLeft: 80,
//         marginTop: 40,

//         legend: true,
//         legendColorBoxGap: 10,
//         legendColorBoxSize: [40,40],
//     });
// }

element.appendChild(chart);


function FormatedData(data, TaskName) {
    let LibraryName = Object.keys(data);
    let task;
    
    let formattedData = [];
    for (let j = 0; j < LibraryName.length; j++) {
        task = data[LibraryName[j]][TaskName]['results'];
        let argument = Object.keys(task).map(x=>+x);
        let results = Object.values(task);
        for (let i = 0; i < argument.length; i++) {
            formattedData.push({
                arguments: argument[i],
                runTime: results[i],
                libraryName : LibraryName[j],
            });
        }
    }
    return formattedData;
}