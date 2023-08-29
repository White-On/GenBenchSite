import {Histogram} from './histogram.js';
import {GroupedBarChart} from './groupedBarChart.js';
import {ViolonsChart} from './violonsChart.js';
import {ComplexeLineChart} from './complexePlot.js';

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

let possibleplot = {"line": ComplexeLineChart, "histo": Histogram, "groupedBar": GroupedBarChart, "violons": ViolonsChart};

const timeBackgroundColor = "#aaffff";
const evaluationBackgroundcolor = "#ffffaa";
// const defaultBackgroundcolor = "#aaffff";

let chartList = [];
let labelList = [];
let allLibraries;

for(let element in importedData){
    let chart;
    let chartdata = importedData[element].data;
    labelList.push(importedData[element].label);
    
    // console.log(chartdata);
    // console.log(importedData[element]);
    if (chartdata.length == 0){
        chart = document.createElement("p");
        chart.innerHTML = "No data to display 😯";
        chartList.push(chart);
        continue;
    }

    // need a better way to get all the libraries
    if (allLibraries == undefined){
        allLibraries = chartdata.map(d => d.libraryName);
        allLibraries = [...new Set(allLibraries)];
    }

    // we attribute a color to each library as a function of the number of libraries
    let colorScale = d3.scaleOrdinal(d3.schemeCategory10);
    colorScale.domain(allLibraries);

    // check if the arguments are numbers or not to sort the data if needed
    if(typeof chartdata[0].arguments === "number"){
        // if the arguments are numbers we sort the data by the arguments
        let orderingFunction = (a, b) => d3.ascending(a.arguments, b.arguments);
        chartdata.sort(orderingFunction);
        // console.log("arguments are numbers");
    }
    else{
        // if the arguments are not numbers we sort the data by the arguments
        // before sorting we need to create a dict with the error values removed
        // and then we sort the data and then fuse the data with the error values
        // let data = chartdata.filter(d => typeof d.runTime === "number");
        // let dataError = chartdata.filter(d => typeof d.runTime !== "number");
        // let orderingFunction = (a, b) => d3.ascending(a.runTime, b.runTime);
        // data.sort(orderingFunction);
        // chartdata = data.concat(dataError);
        // console.log("arguments are not numbers");
    }

    // let orderingFunction = (a, b) => d3.ascending(a.arguments, b.arguments);
    // chartdata.sort(orderingFunction);

    if (importedData[element].scale == "auto"){
        // we're getting the local min and max from each library
        let local_spread = [];
        for(let library of allLibraries){
            
            let data = chartdata.filter(d => d.libraryName == library);
            // we remove the eventual strings from the data -> error in the data
            data = data.filter(d => typeof d.runTime === "number");
            local_spread.push(dataSpread(data.map(d => d.runTime)));
        }
        
        // we remove the eventual 0 from the local spread -> error in the data
        local_spread = local_spread.filter(d => d > 0);
        let data = chartdata.filter(d => typeof d.runTime === "number");
        let global_spread = dataSpread(data.map(d => d.runTime));
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
        console.log(chartdata)
        chart = possibleplot[importedData[element].display](chartdata, {
            values: d => d.runTime,
            categories: d => d.arguments,
            inerClass: d => d.libraryName,
            std: d => d.std,

            width: width,
            height: height,

            // xLabel: argDescription + " →",
            // yLabel: "Run Time (ms) ↑",
            xLabel: importedData[element].XLabel + " →",
            yLabel: importedData[element].YLabel + " ↑",

            labelFontSize: 12,
            titleFontSize: 16,
            title: importedData[element].title,

            margin: { top: 40, right: 10, bottom: 100, left: 50 },

            yType: (importedData[element].scale == 'log')?d3.scaleLog:d3.scaleLinear ,
            // yType: d3.scaleLinear,

            tooltipFontSize: 12,
            timeout : importedData[element].timeout,

            color : d => colorScale(d),

        });

        chartList.push(chart);
    } catch(e){
        // console.log(e);
        chart = document.createElement("p");
        chart.innerHTML = "Error Occured in the display of the chart 😥";
        chartList.push(chart);
    }
}


if (labelList.length == 1){
    dropdown = document.createElement("div");
    dropdown.id = "chartSelector";
    dropdown.innerHTML = labelList[0];
}
else{
    for(let title of labelList){
        let option = document.createElement("option");
        option.value = title;
        option.text = title;
        dropdown.appendChild(option);
    }
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
    chartList[labelList.indexOf(dropdown.value)].style.display = "block";
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
try{
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
}catch(e){
    console.log("No data imported")
    console.log(e);
    
    let code_menu = document.getElementById("code-menu");
    code_menu.style.display = "none";
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

// NAVIGATION BAR
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
