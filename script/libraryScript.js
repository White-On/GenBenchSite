import myJson from '../data.json' assert { type: 'json' };

import {LineChart} from './dynamicPlot.js';
import {Histogram} from './histogram.js';

const data = await myJson;

let AllLibraryName = Object.keys(data);
console.log("AllLibraryName = " + AllLibraryName);

let AllTaskName = Object.keys(data[AllLibraryName[0]]);
console.log("AllTaskName = " + AllTaskName);

let ColorList = ["red", "blue", "green", "yellow", "orange", "purple", "pink", "brown", "grey", "black"]
let colorPalette = {};
for (let i = 0; i < AllLibraryName.length; i++) {
    colorPalette[AllLibraryName[i]] = ColorList[i];
}

// to get the Task Name that we want to plot we have 2 options:

// 1. get the task name from an element in the html page
// var TaskName = document.querySelector('[id^="Lib"]').id;
// console.log("TaskName = " + TaskName);

// 2. get the task name from the url
// var path = window.location.pathname;
// var page = path.split("/").pop().split(".")[0];
// console.log( page );

//3. get the task name from the title of the page
let LibraryName = document.getElementById('entry-title').innerHTML;
console.log(LibraryName);

// let width = element.clientWidth;
// let height = element.clientHeight;

let width = window.innerWidth * 0.8;
let height = window.innerHeight * 0.8;

let orderingFunction = (a, b) => d3.ascending(a.runTime, b.runTime);
for (i = 0; i < AllTaskName.length; i++) {
    let intermediateData = FormatedData({LibraryName : data[LibraryName]}, AllTaskName[i]);
    // console.log("intermediateData.length = " + intermediateData.length);
    if (intermediateData.length == 1) {
        let intermediateDataSorted = intermediateData.sort(orderingFunction);
        chart = Histogram(intermediateDataSorted, {
            x: d => d.libraryName,
            y: d => d.runTime,
            color: d => colorPalette[d],
            width: width,
            height: height,
            yLabel: "Run Time (ms)",
            labelFontSize: 30,

            marginLeft: 80,
            marginTop: 40,

            Legend: true,

        });
    }
    else{
        chart =  LineChart(intermediateData, {
            x: d => d.arguments,
            y: d => d.runTime,
            z: d => d.libraryName,
            yLabel: "Run Time (ms)",
            width: width,
            height: height,
            color: d => colorPalette[d],
            labelFontSize: 30,
            legendFontSize: 30,
            tooltipFontSize: 30,
            
            marginLeft: 80,
            marginTop: 40,

            legend: true,
            legendColorBoxGap: 10,
            legendColorBoxSize: [40,40],
        });
    }

    let element = document.getElementById(AllTaskName[i]);
    element.appendChild(chart);
}
