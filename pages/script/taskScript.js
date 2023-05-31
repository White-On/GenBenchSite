import {LineChart} from './dynamicPlot.js';
import {Histogram} from './histogram.js';
import {GroupedBarChart} from './groupedBarChart.js';
import {ViolonsChart} from './violonsChart.js';

function dataSpread(data){
    let min = Math.min.apply(Math, data)
    let max = Math.max.apply(Math, data)
    return max - min;
}
// to get the Task Name that we want to plot we have 3 options:

// 1. get the task name from an element in the html page
// let TaskName = document.querySelector('[id^="Task"]').id;
// console.log("TaskName = " + TaskName);

// 2. get the task name from the url
// var path = window.location.pathname;
// var page = path.split("/").pop().split(".")[0];
// console.log( page );

//3. get the task name from the title of the page
// let TaskName = document.getElementById('entry-title').innerHTML;

let htmlComponent = document.getElementById("graphics");

// we're adding a dropdown to choose the chart we want to display
let dropdown = document.createElement("select");
dropdown.id = "chartSelector";
dropdown.title = "chartSelector";


let width = htmlComponent.getBoundingClientRect().width;
// let height = window.innerHeight * 0.5;
let height = 500;

let possibleplot = {"line": LineChart, "histo": Histogram, "groupedBar": GroupedBarChart, "violons": ViolonsChart};

const timeBackgroundColor = "#ffffaa";
const evaluationBackgroundcolor = "#aaffff";
// const defaultBackgroundcolor = "#aaffff";

let chartList = [];
let titleList = [];
let allLibraries;

for(let element in importedData){
    let chart;
    let chartdata = importedData[element].data;
    titleList.push(importedData[element].title);
    
    console.log(chartdata);
    // console.log(importedData[element]);
    if (chartdata.length == 0){
        chart = document.createElement("p");
        chart.innerHTML = "No data to display 😯";
        chartList.push(chart);
        continue;
    }

    // need a better way to get all the libraries
    allLibraries = chartdata.map(d => d.libraryName);
    allLibraries = [...new Set(allLibraries)];

    // check if the arguments are numbers or not to sort the data if needed
    // if(typeof chartdata[0].arguments === "number"){
    //     // if the arguments are numbers we sort the data by the arguments
    //     let orderingFunction = (a, b) => d3.ascending(a.arguments, b.arguments);
    //     chartdata.sort(orderingFunction);
    //     console.log("arguments are numbers");
    // }
    // else{
    //     // if the arguments are not numbers we sort the data by the arguments
    //     let orderingFunction = (a, b) => d3.ascending(a.runTime, b.runTime);
    //     chartdata.sort(orderingFunction);
    //     console.log("arguments are not numbers");
    // }

    let orderingFunction = (a, b) => d3.ascending(a.arguments, b.arguments);
    chartdata.sort(orderingFunction);

    if (importedData[element].scale == "auto"){
        // we're getting the local min and max from each library
        let local_spread = [];
        for(let library of allLibraries){
            let data = chartdata.filter(d => d.libraryName == library);
            local_spread.push(dataSpread(data.map(d => d.runTime)));
        }
        // we remove the eventual 0 from the local spread -> error in the data
        local_spread = local_spread.filter(d => d != 0);
        let global_spread = dataSpread(chartdata.map(d => d.runTime));
        // default scale is linear
        importedData[element].scale = 'linear'
        // factor of comparison between the local spread and the global spread
        let factor = 0.2;
        for(let spread of local_spread){
            if (spread < global_spread * factor){
                importedData[element].scale = 'log'
                break;
            }
        }

    }

    try{
        chart = possibleplot[importedData[element].display](chartdata, {
            values: d => d.runTime,
            categories: d => d.arguments,
            inerClass: d => d.libraryName,

            width: width,
            height: height,

            // xLabel: argDescription + " →",
            // yLabel: "Run Time (ms) ↑",
            xLabel: importedData[element].XLabel + " →",
            yLabel: importedData[element].YLabel + " ↑",

            labelFontSize: 12,
            titleFontSize: 16,

            margin: { top: 40, right: 10, bottom: 100, left: 50 },

            // yType: (importedData[element].scale == 'log')?d3.scaleLog:d3.scaleLinear ,
            yType: d3.scaleLinear,

            tooltipFontSize: 12,

        });

        chartList.push(chart);
    } catch(e){
        console.log(e);
        chart = document.createElement("p");
        chart.innerHTML = "Error Occured in the display of the chart 😥";
        chartList.push(chart);
    }
}


for(let title of titleList){
    let option = document.createElement("option");
    option.value = title;
    option.text = title;
    dropdown.appendChild(option);
}

htmlComponent.appendChild(dropdown);

for(let chart of chartList){
    htmlComponent.appendChild(chart);
    // we set the display to none to hide the chart
    chart.style.display = "none";
}

// we display the first chart
chartList[0].style.display = "block";

if (dropdown.value == "Runtime"){
    htmlComponent.style.backgroundColor = timeBackgroundColor;
}else {
    htmlComponent.style.backgroundColor = evaluationBackgroundcolor;
}

dropdown.onchange = function(){
    for(let chart of chartList){
        chart.style.display = "none";
    }
    chartList[titleList.indexOf(dropdown.value)].style.display = "block";
    if (dropdown.value == "Runtime"){
        htmlComponent.style.backgroundColor = timeBackgroundColor;
    }else {
        htmlComponent.style.backgroundColor = evaluationBackgroundcolor;
    }
}

// we're adding buttons to choose the library's code we want to display
let codeSelector = document.getElementById("codeSelector");
codeSelector.id = "codeSelector";


// by default we display two libraries's code
let elementsToDisplay = [];
elementsToDisplay.push(allLibraries[0]);
elementsToDisplay.push(allLibraries[1]);
handleClickToPrintCode(elementsToDisplay);

for(let library of allLibraries){
    let button = document.createElement("button");
    button.type = "button";
    button.id = library + "-button";
    button.innerHTML = library;
    
    // we manage the click on the button
    // if the element is already in the list we remove it
    // if the element is not in the list we add it
    // we can only have two elements in the list
    button.onclick = function(){
        if(elementsToDisplay.includes(library)){
            elementsToDisplay.splice(elementsToDisplay.indexOf(library), 1);
        }else{
            elementsToDisplay.push(library);
        }
        if(elementsToDisplay.length > 2){
            elementsToDisplay.shift();
        }
        handleClickToPrintCode(elementsToDisplay);
    }
        
    codeSelector.appendChild(button);
}



function handleClickToPrintCode(elementsToDisplay) {
    // console.log(elementsToDisplay);
    for(let library of allLibraries){
        if(elementsToDisplay.includes(library)){
            document.getElementById(library).style.display = "block";
        }else{
            document.getElementById(library).style.display = "none";
        }
    }
}

// document.body.innerHTML += code["pgmpy"]

//we want to make the navActive class active on the library page
let navActive = document.getElementById(TaskName + "-nav");

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
