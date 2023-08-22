import {LineChart} from './dynamicPlot.js';
import {Histogram} from './histogram.js';

// to get the Task Name that we want to plot we have 2 options:

// 1. get the task name from an element in the html page
// var TaskName = document.querySelector('[id^="Lib"]').id;
// console.log("TaskName = " + TaskName);

// 2. get the task name from the url
// var path = window.location.pathname;
// var page = path.split("/").pop().split(".")[0];
// console.log( page );

//3. get the task name from the title of the page
const libraryName = document.getElementById('entry-title').innerHTML;
// console.log("libraryName = " + libraryName);


// const reductFactor = 0.8;
// let width = window.innerWidth * reductFactor;
// let height = window.innerHeight * reductFactor;

let width = 1000;
let height = 600;
let chart;

const timeBackgroundColor = "#aaffff";

// let treatedData = ResultTreatement(data[libraryName],libraryName);
// console.log(treatedData);

console.log(importedData);

let AllTaskName = Object.keys(importedData);

let orderingFunction = (a, b) => d3.ascending(a.resultElement, b.resultElement);
for (let taskName of AllTaskName) {
    let element = document.getElementById(taskName);

    // console.log("taskName = " + taskName);
    // let intermediateData = FormatedData({[libraryName]:data[libraryName]}, AllTaskName[i]);
    let intermediateData = importedData[taskName];
    // console.log(intermediateData);
    // console.log(intermediateData["status"]);
    if ( intermediateData["status"] != "Run") {
        
        const dictionary = {
            "Error": "A Error occured during the execution of the task" + taskName, 
            "NotRun": "The task " + taskName + " is not available for the library " + libraryName,
            "Timeout": "The task " + taskName + " has been terminated because it took too much time to execute"
        };

        chart = document.createElement("p");
        chart.innerHTML = dictionary[intermediateData["status"]];
    }
    else 
    if (intermediateData["display"] == "histo") {
        let intermediateDataSorted = intermediateData["data"].sort(orderingFunction);
        // generate a color dictionary for the histogram with a gradient of color
        let colorPalette = {};
        for (let i = 0; i < intermediateDataSorted.length; i++) {
            colorPalette[intermediateDataSorted[i].arguments] = d3.interpolateViridis(1-(i / intermediateDataSorted.length));
        }
        chart = Histogram(intermediateDataSorted, {
            x: d => d.arguments,
            y: d => d.resultElement,
            color:  d => colorPalette[d],
            width: width,
            height: height,
            yLabel: "Run Time (s) ↑",
            labelFontSize: 20,
            margin : { top: 40, right: 30, bottom: 100, left: 80 },

            legend: false,

            noXAxisValues: false,    
        });
    }
    else{
        chart =  LineChart(intermediateData["data"], {
            values: d => d.resultElement,
            categories: d => d.arguments,
            inerClass: d => d.libraryName,
            yLabel: "Run Time (s) ↑",
            width: width,
            height: height,
            // color: d => colorPalette[d],
            labelFontSize: 30,
            legendFontSize: 30,
            tooltipFontSize: 30,
            
            margin : { top: 40, right: 30, bottom: 50, left: 80 },
            

            displayLegend: false,
            legendColorBoxGap: 10,
            legendColorBoxSize: [40,40],
        });
    }

    element.appendChild(chart);
    let card = element.parentElement;
    card.style.backgroundColor = timeBackgroundColor;
    
}



//we want to make the navActive class active on the library page 
let navActive = document.getElementById(libraryName + "-nav");

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