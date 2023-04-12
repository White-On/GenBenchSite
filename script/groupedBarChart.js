export function GroupedBarChart(data,{
    values = ([value]) => value, 
    categories = ([, categories]) => categories, 
    inerClass = ([, , inerClass]) => inerClass,

    title,

    width = width,
    height = height,

    margin = { top: 20, right: 20, bottom: 30, left: 40 },

    color = d3.scaleOrdinal(d3.schemeCategory10),

    labelFontSize = 20, // font size of the labels

    yRange = [height - margin.bottom, margin.top], // [bottom, top]
    yFormat, // format of the y-axis
    yLabel, // label of the y-axis

    xLegend = width*0.1, // x-axis legend
    yLegend = height*0.1, // y-axis legend
    legendColorBoxSize = [20, 20], // size of the color box in the legend
    legendColorBoxGap = 5, // margin of the color box in the legend
    legendFontSize = 20, // font size of the legend

} = {}) {

    const Values = d3.map(data, values);
    const Categories = d3.map(data, categories);
    const InerClass = d3.map(data, inerClass);

    const I = d3.range(Values.length);

    console.log(Values);
    console.log(Categories);
    console.log(InerClass);

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
        .paddingInner(0.1)
        .domain(Categories);

    let xScaleInerCategory = d3
        .scaleBand()
        .padding(0.05)
        .domain(InerClass)
        .rangeRound([0, xScaleCategory.bandwidth()]);
  
    const yMinMaxValue = d3.extent(Values);
    const yDomain = [0, yMinMaxValue[1]];
    const yScale = d3.scaleLinear(yDomain, yRange);

    const xAxis = d3.axisBottom(xScaleCategory);
    const yAxis = d3.axisLeft(yScale).ticks(height / 60, yFormat);

    let svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto; height: intrinsic;")
        .style("-webkit-tap-highlight-color", "transparent")

    let rect = svg
      .selectAll("rect")
      .data(I)
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
      .attr("transform", function (d) {
            return "translate(" + xScaleCategory(Categories[d]) + ",0)"
        })
      .attr("fill", function (d) {
        return color(InerClass[d]);
      })
      .on("click", handleBarClick); // Add click event listener
  

    // add the x-axis to the chart.
    svg.append("g")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(xAxis)
        .attr("font-size", labelFontSize)
        .call(g => g.select(".domain").remove());
  
    // add the y-axis to the chart.
    svg.append("g")
        .attr("transform", `translate(${margin.left},0)`)
        .call(yAxis)
        .attr("font-size", labelFontSize)
        .call(g => g.select(".domain").remove())
        .call(g => g.append("text")
            .attr("x", -margin.left)
            .attr("y", 10 + labelFontSize/2)
            .attr("text-anchor", "start")
            .text(yLabel));
  
    var legend = svg
      .append("g")
      .attr("font-family", "sans-serif")
      .attr("font-size", 10)
      .attr("text-anchor", "end")
      .selectAll("g")
      .data(Categories.slice().reverse())
      .enter()
      .append("g")
      .attr("transform", function (d, i) {
        return "translate(0," + i * 20 + ")";
      });
  
    legend
      .append("rect")
      .attr("x", width - 19)
      .attr("width", 19);

    
    const swatches = svg.append("g")
        .attr("font-family", "sans-serif")
        .attr("font-size", legendFontSize)
        .attr("text-anchor", "start")
        .selectAll("g")
        .data(new Set(InerClass))
        .join("g")
        .attr("transform", (z, i) => `translate(0,${i * legendColorBoxSize[1] + i * legendColorBoxGap })`)
        .on("click", handleSwatchClick); // Add click event listener
      
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
      

    let previousElement = null;

    function handleSwatchClick(swatchElement) {
        // console.log(swatchElement.srcElement.__data__);

        if(previousElement == swatchElement.srcElement.__data__){
            rect
            .data(I)
            .transition()
            .duration(500)
            .attr("fill", function (d) {
                return color(InerClass[d]);
            });
            previousElement = null;

            swatches
            .data(new Set(InerClass))
            .transition()
            .duration(500)
            .attr("fill", function (d) {
                return "black";
            });
        }else{
            rect
            .data(I)
            .transition()
            .duration(500)
            .attr("fill", function (d) {
                return InerClass[d] == swatchElement.srcElement.__data__ ? color(InerClass[d]) : "#ddd";
            });
            previousElement = swatchElement.srcElement.__data__;

            swatches
            .data(new Set(InerClass))
            .transition()
            .duration(500)
            .attr("fill", function (d) {
                return d == swatchElement.srcElement.__data__ ? "black" : "#ddd";
            });
        }

    }

    function handleBarClick(barElement) {
        // console.log(InerClass[barElement.srcElement.__data__]);

        if(previousElement == barElement.srcElement.__data__){
            rect
            .data(I)
            .transition()
            .duration(500)
            .attr("fill", function (d) {
                return color(InerClass[d]);
            });
            previousElement = null;

            swatches
            .data(new Set(InerClass))
            .transition()
            .duration(500)
            .attr("fill", function (d) {
                return "black";
            });
        }else{
            rect
            .data(I)
            .transition()
            .duration(500)
            .attr("fill", function (d) {
                return InerClass[d] == InerClass[barElement.srcElement.__data__] ? color(InerClass[d]) : "#ddd";
            });
            previousElement = barElement.srcElement.__data__;

            swatches
            .data(new Set(InerClass))
            .transition()
            .duration(500)
            .attr("fill", function (d) {
                return d == InerClass[barElement.srcElement.__data__] ? "black" : "#ddd";
            });
        }
    }
      
    
    return svg.node();
}


