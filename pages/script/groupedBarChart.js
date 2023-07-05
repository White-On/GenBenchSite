export function GroupedBarChart(data,{
    values = ([value]) => value, // given d in data, returns the (quantitative) x-value
    categories = ([, categories]) => categories,  // given d in data, returns the (temporal) y-value
    inerClass = ([, , inerClass]) => inerClass, // given d in data, returns the (categorical) z-value

    title = "",
    defined, // for gaps in data

    width,
    height,

    margin = { top: 20, right: 20, bottom: 30, left: 40 },

    color = d3.scaleOrdinal(d3.schemeCategory10),

    labelFontSize = 8, // font size of the labels
    tooltipFontSize = 12, // font size of the title

    yRange = [height - margin.bottom, margin.top], // [bottom, top]
    yFormat, // format of the y-axis

    yLabel, // label of the y-axis
    xLabel, // label of the x-axis

    // xLegend = width*0.1, // x-axis legend
    // yLegend = height*0.1, // y-axis legend

    xLegend = margin.left + 15, // x-axis legend
    yLegend = 0, // y-axis legend
    legendColorBoxSize = [10, 10], // size of the color box in the legend
    legendColorBoxGap = 5, // margin of the color box in the legend
    legendFontSize = 12, // font size of the legend

    activationFunction = null,

    titleFontSize = 16,

    displayLegend = true, // show a legend?

    yType = d3.scaleLinear, // "linear" or "log"

} = {}) {

    const Values = d3.map(data, values);
    const Categories = d3.map(data, categories);
    const InerClass = d3.map(data, inerClass);

//  we want to draw the bars from the highest to the lowest value
//  this wait we wont have issue with the labels
    let indices = [...Values.keys()].sort((a, b) => Values[b] - Values[a]);
    if (defined === undefined) defined = (d, i) => !isNaN(Values[i]);
    const D = d3.map(indices, defined); 
    indices = indices.filter(i => D[i]);

    const I = d3.range(Values.length);

    // console.log(Values);
    // console.log(Categories);
    // console.log(InerClass);

    // // console.log(d3.schemeCategory10);
    // color = d3.scaleOrdinal(color)
    // let colorCategories = [];
    // for (let i = 0; i < new Set(InerClass).length; i++) {
    //     colorCategories.push(d3.interpolateRainbow(i / new Set(InerClass).length));
    // }
    // console.log(colorCategories);
    // color = d3.scaleOrdinal(colorCategories);
    // console.log(colorCategories);

    let xScaleCategory = d3
        .scaleBand()
        .rangeRound([margin.left, width-margin.right])
        .paddingInner(0.3)
        .domain(Categories);

    let xScaleInerCategory = d3
        .scaleBand()
        .padding(0.05)
        .domain(InerClass)
        .rangeRound([0, xScaleCategory.bandwidth()]);
  
    const yMinMaxValue = d3.extent(Values.filter((d) => !isNaN(d)));

    // CAUTION: if the min value is 0, the log scale will not work

    let yDomain;
    let yScale;
    if (yType == d3.scaleLog) {
        yDomain = [yMinMaxValue[0] <= 0 ? 0.0001 : yMinMaxValue[0], yMinMaxValue[1]];
        // yDomain = [0.0001, yMinMaxValue[1]];
        yScale = d3.scaleLog(yDomain, yRange)
    }
    else {
        yDomain = [0, yMinMaxValue[1]];
        yScale = yType(yDomain, yRange);
    }

    let xAxis = d3.axisBottom(xScaleCategory);
    let yAxis = d3.axisLeft(yScale).ticks(height / 60, yFormat);

    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto; height: intrinsic;")
        .style("-webkit-tap-highlight-color", "transparent");


    const rect = svg
        .selectAll("g")
        .data(indices)
        .join("g")
        .attr("transform", function (d) {
            return "translate(" + xScaleCategory(Categories[d]) + ",0)"
        });
    
    // console.log(I);
    // console.log(InerClass);
    // console.log(Values);
    
    rect
        .append("rect")
        .join("rect")
        .attr("x", function (d) {
            return xScaleInerCategory(InerClass[d]);
        })
        .attr("y", function (d) {
            return yScale(Values[d]);
        })
        .attr("width", xScaleInerCategory.bandwidth())
        .attr("height", function (d) {
            return height - yScale(Values[d]) - margin.bottom;
        })
        .attr("fill", function (d) {
            return color(InerClass[d]);
        })
        // Add click event listener
        .on("click", handleClick)
        .style("cursor", "pointer");

    
    rect
        .append("text")
        .join("text")
        .attr("opacity", 0)
        .attr("font-size", tooltipFontSize)
        .attr("text-anchor", "middle")
        .attr("fill", "black")
        .attr("x", function (d) {
            return xScaleInerCategory(InerClass[d]) + xScaleInerCategory.bandwidth()/2;
        })
        .attr("y", function (d) {
            return yScale(Values[d]) - 5;
        })
        .text(function (d) {
            return Values[d].toFixed(countDecimals(Values[d])<=2?countDecimals(Values[d]):2);
        })
        ;
  

    // add the x-axis to the chart.
    let xAxisG = svg.append("g")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(xAxis)
        .attr("font-size", labelFontSize)
        .call(g => g.selectAll("text")
        .attr("text-anchor", "end")
            .attr("transform", "rotate(-45)"))
        .call(g => g.select(".domain").remove())
        .call(g => g.append("text")
            .attr("font-size", labelFontSize)
            .attr("x", width - margin.right)
            .attr("y", + margin.bottom/2)
            .attr("text-anchor", "end")
            .attr("fill", "currentColor")
            .text(xLabel));
  
    // add the y-axis to the chart.
    let yAxisG = svg.append("g")
        .attr("transform", `translate(${margin.left},0)`)
        .call(yAxis)
        .attr("font-size", labelFontSize)
        .call(g => g.select(".domain").remove())
        .call(g => g.selectAll(".tick").call(grid)) // add the gridlines to the chart.
        .call(g => g.append("text")
            .attr("x", -margin.left)
            .attr("y", 10 + labelFontSize/2)
            .attr("text-anchor", "start")
            .attr("fill", "currentColor")
            .text(yLabel));

    
    // add the title to the chart.
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", 10 + titleFontSize/2)
        .attr("text-anchor", "middle")
        .attr("fill", "currentColor")
        .attr("font-size", titleFontSize)
        .text(title);


    const swatches = svg.append("g")
        .attr("font-family", "sans-serif")
        .attr("font-size", legendFontSize)
        .attr("text-anchor", "start")
        .selectAll("g")
        .data(new Set(InerClass))
        .join("g")
        .attr("transform", (z, i) => `translate(0,${i * legendColorBoxSize[1] + i * legendColorBoxGap })`)
        .on("click", handleClick) // Add click event listener
        .style("cursor", "pointer");
        
        swatches.append("rect")
        .attr("x", xLegend)
        .attr("y", yLegend )
        .attr("width", legendColorBoxSize[0])
        .attr("height", legendColorBoxSize[1])
        .attr("fill", color);
        
        swatches.append("text")
        .attr("x", xLegend + legendColorBoxSize[0] + legendColorBoxGap)
        .attr("y", yLegend + legendColorBoxSize[1]/2 - legendFontSize/2)
        .attr("dy", "1em")
        .text(z => z);
    


    let activeElement = [];
    let lastTwoElementSelected = [];

    function handleClick(clickedElement) {
        let innerClassSelected;
        if (clickedElement.srcElement.nodeName == "rect"){
            if (typeof clickedElement.srcElement.__data__ == "number"){
                innerClassSelected = InerClass[clickedElement.srcElement.__data__];
            }
            else{
                innerClassSelected = clickedElement.srcElement.__data__;
            }
        }
        else{
            innerClassSelected = clickedElement.srcElement.__data__;
        }        

        // If the clicked element is already active, remove it from the active list
        if(activeElement.includes(innerClassSelected)){
            activeElement = activeElement.filter(function(value){
                return value != innerClassSelected;
            });
        // If the clicked element is not active, add it to the active list
        }else{
            // for multiple selection
            // activeElement.push(innerClassSelected);

            // for single selection
            activeElement = [innerClassSelected];

            lastTwoElementSelected.push(innerClassSelected);
            lastTwoElementSelected = [...new Set(lastTwoElementSelected)]
            lastTwoElementSelected = lastTwoElementSelected.slice(-2);
        }


        // If there are no active elements, reset the chart
        if(activeElement.length == 0){
            rect
                .data(indices)
                .transition()
                .duration(500)
                .select("text")
                .attr("opacity", 0);

            rect
                .data(indices)
                .transition()
                .duration(500)
                .select("rect")
                .attr("fill", function (d) {
                    return color(InerClass[d]);
                });

            swatches
                .data(new Set(InerClass))
                .transition()
                .duration(500)
                .attr("fill", function (d) {
                    return "black";
            });

            if (activationFunction != null) {
                // console.log("activationFunction");
                activationFunction(lastTwoElementSelected);
            }

        // If there are active elements, update the chart
        }else{
            rect
                .data(indices)
                .transition()
                .duration(500)
                .delay((d) => (d * 20))
                .select("rect")
                .attr("fill", function (d) {
                    return activeElement.includes(InerClass[d]) ? color(InerClass[d]) : "#ddd";
                });
                // a process to make the inactive elements disappear
                // we add the value of the rect height to the y position to get the bottom of the rect
                // .attr("y", function (d) {
                //     return activeElement.includes(InerClass[d]) ? yScale(Values[d]) : yScale(Values[d]) + height - yScale(Values[d]) - margin.bottom;
                // })  
                // // we subtract the value of the rect height from the height of the chart to get the new height of the rect
                // .attr("height", function (d) {
                //     return activeElement.includes(InerClass[d]) ? height - yScale(Values[d]) - margin.bottom : 0;
                // });

                // process to make the value of the rect appear
            rect
                .data(indices)
                .transition()
                .duration(500)
                .delay((d) => (d * 20))
                .select("text")
                .attr("opacity", function (d) {
                    return activeElement.includes(InerClass[d]) ? 1 : 0;
                });

            
            swatches
                .data(new Set(InerClass))
                .transition()
                .duration(500)
                .attr("fill", function (d) {
                    return activeElement.includes(d) ? "black" : "#ddd";
                });

            if (activationFunction != null) {
                // console.log("activationFunction");
                activationFunction(lastTwoElementSelected);
            }
        }

        // console.log(activeElement);
        // console.log(innerClassSelected);
            

    }

    function grid(tick) {
        return tick.append("line")
            .attr("class", "grid")
            .attr("x2", width - margin.left - margin.right)
            .attr("stroke", "currentColor")
            .attr("stroke-opacity", 0.1);
    }

    // Menu for the scale

    // const menu = () => {
    //     let id;
    //     let LabelText;
    //     let options;

    //     const my = (selection) => {
    //         selection
    //             .selectAll("label")
    //             .data([null])
    //             .join("label")
    //             .attr("for", id)
    //             .text(LabelText);
    //         selection
    //             .selectAll("select")
    //             .data([null])
    //             .join("select")
    //             .attr("id", id)
    //             .on("change", (event) => {
    //                 console.log(event.target.value);
    //                 if (event.target.value == "log") {
    //                     yScale = d3.scaleLog()
    //                         .domain([1, d3.max(Values)])
    //                         .range([height - margin.bottom, margin.top]);
    //                 } else if (event.target.value == "auto") {
    //                     yScale = d3.scaleLinear()
    //                         .domain([0, d3.max(Values)])
    //                         .range([height - margin.bottom, margin.top]);
    //                 }
    //                 yAxis = d3.axisLeft(yScale);
    //                 rect
    //                     .data(I)
    //                     .transition()
    //                     .duration(500)
    //                     .delay((d) => (d * 20))
    //                     .select("rect")
    //                     .attr("y", function (d) {
    //                         return yScale(Values[d]);
    //                     }
    //                     )
    //                     .attr("height", function (d) {
    //                         return height - yScale(Values[d]) - margin.bottom;
    //                     }
    //                     );
    //                 rect
    //                     .data(I)
    //                     .transition()
    //                     .duration(500)
    //                     .delay((d) => (d * 20))
    //                     .select("text")
    //                     .attr("y", function (d) {
    //                         return yScale(Values[d]) - 5;
    //                     }
    //                     );
                    
    //                 yAxisG
    //                     .transition()
    //                     .duration(500)
    //                     .call(yAxis);
                    



    //             })
    //             .selectAll("option")
    //             .data(options)
    //             .join("option")
    //             .attr("value", (d) => d)
    //             .text((d) => d);


    //     };
        
    //     my.id = function (value) {
    //         return arguments.length ? (id = value, my) : id;
    //     };

    //     my.LabelText = function (value) {
    //         return arguments.length ? (LabelText = value, my) : LabelText;
    //     };

    //     my.options = function (value) {
    //         return arguments.length ? (options = value, my) : options;
    //     };
    
    //     return my;
    // }
   
    // let menuElement = document.getElementById("menu");
    // if (menuElement != null) {
    //     // get the menu as a d3 selection
    //     let menuD3 = d3.select(menuElement);
    //     // add the menu items
    //     menuD3
    //         .call(menu().id("menu1").LabelText("Select view").options(["auto", "log", "normal"]))

    // }

    
    
    return svg.node();
}


function countDecimals(num) {
    var str = num.toString();
    var decimalIndex = str.indexOf('.');
    if (decimalIndex === -1) {
      return 0;
    } else {
      return str.length - decimalIndex - 1;
    }
  }