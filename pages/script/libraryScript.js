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
console.log("libraryName = " + libraryName);


const reductFactor = 0.8;
let width = window.innerWidth * reductFactor;
let height = window.innerHeight * reductFactor;

let chart;


// let treatedData = ResultTreatement(data[libraryName],libraryName);
// console.log(treatedData);

// console.log(importedData);

let AllTaskName = Object.keys(importedData);

let orderingFunction = (a, b) => d3.ascending(a.resultElement, b.resultElement);
for (let taskName of AllTaskName) {
    let element = document.getElementById(taskName);

    console.log("taskName = " + taskName);
    // let intermediateData = FormatedData({[libraryName]:data[libraryName]}, AllTaskName[i]);
    let intermediateData = importedData[taskName];
    console.log(intermediateData);
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
            yLabel: "Run Time (ms) ↑",
            labelFontSize: 20,
            marginLeft: 80,
            marginTop: 40,
            marginBottom: 80,

            legend: false,

            noXAxisValues: false,    
        });
    }
    else{
        chart =  LineChart(intermediateData["data"], {
            x: d => d.arguments,
            y: d => d.resultElement,
            z: d => d.libraryName,
            yLabel: "Run Time (ms) ↑",
            width: width,
            height: height,
            // color: d => colorPalette[d],
            labelFontSize: 30,
            legendFontSize: 30,
            tooltipFontSize: 30,
            
            marginLeft: 80,
            marginTop: 40,
            

            legend: false,
            legendColorBoxGap: 10,
            legendColorBoxSize: [40,40],
        });
    }

    
    element.appendChild(chart);
}

function FormatedData(data, TaskName) {
    let LibraryName = Object.keys(data);
    let task;
    // console.log(data)

    // if (data[LibraryName[0]][TaskName]['statusCode'] != 0) {
    //     return null;
    // }
    
    let formattedData = [];
    for (let j = 0; j < LibraryName.length; j++) {
        task = data[LibraryName[j]][TaskName]['results'];
        let argument = Object.keys(task).map(x=>+x).map(x=>x<0?0:x);
        // let argumentDomain = Object.keys(task);
        let diplayModele = "line";
        if (IsNanList(argument)) {
            // argumentDomain = Object.keys(task);
            // argument = Array.from(Array(argumentDomain.length).keys());
            argument = Object.keys(task);
            diplayModele = "histogram";

        }
        let results = Object.values(task).map(x=>+x).map(x=>x<0?0:x);

        let resultsAndArgument = argument.map((x, i) => [x, results[i]]).filter(x => x[1] != Infinity);
        // console.log(resultsAndArgument);

        for (let i = 0; i < resultsAndArgument.length; i++) {
            formattedData.push({
                arguments: resultsAndArgument[i][0],
                resultElement: resultsAndArgument[i][1],
                libraryName : LibraryName[j],
                diplayModele: diplayModele,
            });
        }
    }
    return formattedData;
}

function IsNanList(list) {
    let cpt = 0;
    for (let i = 0; i < list.length; i++) {
        if (isNaN(list[i])) {
            cpt++;
        }
    }
    return cpt == list.length;
}

function ResultTreatement(tasksData,libraryName,type = "time") {
    let task;
    let formattedData = {};
    for (let taskName in tasksData) {
        // console.log(taskName);
        formattedData[taskName] = [];

        let results = Object.values(tasksData[taskName]["results"]).map(x=>x[type=="time"?0:1]).map((x,i)=>+x).map(x=>x<0?0:x);
        // console.log(results);

        if(IsNanList(results)){
            formattedData[taskName] = Object.values(tasksData[taskName]["results"]).map(x=>x[type=="time"?0:1])[0];
            continue;
        }

        let argument = Object.keys(tasksData[taskName]["results"]).map(x=>+x).map(x=>x<0?0:x);
        let diplayModele = "line";
        
        if (IsNanList(argument)) {
            argument = Object.keys(tasksData[taskName]["results"])
            diplayModele = "histogram";

        }
        // console.log(argument);

        let resultsAndArgument = argument.map((x, i) => [x, results[i]]).filter(x => x[1] == x[1]);
        // console.log(resultsAndArgument);

        for (let i = 0; i < resultsAndArgument.length; i++) {
            formattedData[taskName].push({
                arguments: resultsAndArgument[i][0],
                resultElement: resultsAndArgument[i][1],
                libraryName : libraryName,
                diplayModele: diplayModele,
            });
        }
    }
    return formattedData;
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