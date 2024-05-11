// import { HeatMap } from "./heatMapChart.js";
import { rankBar } from "./rankBar.js";


let width = window.innerWidth * 1;
let height = window.innerHeight * 1;

const main_container = document.getElementById("main_container");

// console.log(importedData)
let setTaskName = new Set();
let setLibraryName = new Set();
for (let i = 0; i < importedData.length; i++) {
    setTaskName.add(importedData[i].taskName);
    setLibraryName.add(importedData[i].libraryName);
}
// transform the set into an array
setTaskName = Array.from(setTaskName);
setLibraryName = Array.from(setLibraryName);

// we adjust the position of the theme name present in the task set 
// so that it is always at the top of the list
// let index = setTaskName.indexOf(themeName);
// setTaskName.splice(index, 1);
// setTaskName.unshift(themeName);

// console.log(setTaskName);
// console.log(setLibraryName);

for (let task of setTaskName){    
    // console.log(task);
    let cls = importedData.filter(d => d.taskName == task);
    // we want a element like this
    // {library:result,library:result}
    cls = cls.map(d => {
        let obj = {};
        obj[d.libraryName] = d.results;
        return obj;
    });
    //  we want to merge all the objects in the array into one object
    cls = Object.assign({}, ...cls);
    // console.log(cls);

    let chart = rankBar(cls, {
        width : 400,
        height : 25,
        fontSize : 10,
        gap : 5,
    });

    let div = document.createElement("div");
    const title = document.createElement("h2");
    if (task == themeName) {
        title.innerHTML = task;
    } else {
        title.innerHTML = "•\t" + task;
    }
    div.appendChild(title);
    div.appendChild(chart);
    div.classList.add("chart");

    main_container.appendChild(div);
};


// let chart;

// chart = HeatMap(importedData, {
//     x: d => d.libraryName,
//     y: d => d.taskName,
//     value: d => d.results,

//     width: width,
//     height: height,

//     margin: { top: 30, right: 0, bottom: 0, left: 250 },
//     yLabel: "Task",
    
// });

// document.body.appendChild(chart);

// NAVIGATION BAR

// let themeName = document.getElementById('entry-title').innerHTML;
// console.log(themeName);
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

// we now make the submenu of the active nav element visible
navActive = document.getElementById(themeName + "-nav");
let subMenu = navActive.parentElement.parentElement.getElementsByClassName("subMenu")[0];
if (subMenu.classList.contains("collapse")) {
    subMenu.classList.replace("collapse", "expand");
    subMenu.parentElement.getElementsByClassName("arrow")[0].style.transform = "rotate(0deg)";
}




