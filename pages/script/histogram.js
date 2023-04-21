export function Histogram(data, {
    x = ([x]) => x, // given d in data, returns the (temporal) x-value
    y = ([, y]) => y, // given d in data, returns the (quantitative) y-value

    width = 640,
    height = 400,

    marginTop = 20, // top margin, in pixels
    marginRight = 30, // right margin, in pixels
    marginBottom = 30, // bottom margin, in pixels
    marginLeft = 50, // left margin, in pixels

    xDomain = undefined, // [x0, x1], or undefined to auto-detect
    yDomain = undefined, // [y0, y1], or undefined to auto-detect
    xRange = [marginLeft , width - marginRight], // [x0, x1]
    yRange = [height - marginBottom, marginTop], // [y0, y1]

    noXAxisValues = false, // array of x-values to show ticks for

    yType = d3.scaleLinear, // y-axis scale type
    yFormat = d3.format(".0s"), // y-axis tick format
    // yFormat,

    yLabel = "", // y-axis label
    labelFontSize = 8, // font size of the label

    xPadding = 0.2, // padding between bars on the x-axis

    color = "steelblue", // bar color

    legend = true, // show legend
    xLegend = width*0.1, // x-axis legend
    yLegend = height*0.1, // y-axis legend
    legendColorBoxSize = [20, 20], // size of the color box in the legend
    legendColorBoxGap = 5, // margin of the color box in the legend
    legendFontSize = 20, // font size of the legend

    } = {}) {
    const X = d3.map(data, x); // x-values
    const Y = d3.map(data, y); // y-values
    
    if (xDomain === undefined) xDomain = X;
    if (yDomain === undefined) yDomain = [0, d3.max(Y)];
    xDomain = new d3.InternSet(xDomain);

    // Omit any data not present in the x-domain.
    const I = d3.range(X.length).filter(i => xDomain.has(X[i]));

    // The scale for the x-axis. Note that the x-axis is a band scale.
    const xScale = d3.scaleBand(xDomain, xRange).padding(xPadding);
    // The scale for the y-axis.
    const yScale = yType(yDomain, yRange);

    const xAxis = d3.axisBottom(xScale).tickSizeOuter(0);
    const yAxis = d3.axisLeft(yScale).ticks(height / 40, yFormat);

    if (noXAxisValues) xAxis.tickValues(noXAxisValues);

    const format = yScale.tickFormat(100, yFormat);
    
    // the main svg element
    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto; height: intrinsic;")
        .style("-webkit-tap-highlight-color", "transparent")
    
    // X-axis 
    const xGroup = svg.append("g")
        .attr("transform", `translate(0,${height - marginBottom})`)
        .call(xAxis)
        .style("font-size", labelFontSize)
        .attr("text-anchor", "end")
        .selectAll("text")
        .attr("transform", "rotate(-45)");
    
    // Y-axis 
    const yGroup = svg.append("g")
      .attr("transform", `translate(${marginLeft},0)`)
      .call(yAxis)
      .call(g => g.select(".domain").remove())
      .call(g => g.selectAll(".tick").call(grid))
      .call(g => g.append("text")
            .attr("x", -marginLeft)
            .attr("y", 10 + labelFontSize / 2)
            .attr("fill", "currentColor")
            .attr("text-anchor", "start")
            .text(yLabel))
            .style("font-size", labelFontSize);
    
    // create the bars
    let rect = svg.append("g")
      .attr("fill", typeof color === "string" ? color : null)
        .selectAll("rect")
        .data(I)
        .join("rect")
        .call(position, i => xScale(X[i]), i => yScale(Y[i]))
        .style("mix-blend-mode", "multiply")
        .attr("fill", typeof color === "function" ? (i) => color(X[i]) : null)
        .call(rect => rect.append("title")
            .text(i => [X[i], `${format(Y[i])} sec`].join("\n")));
    
    // create the legend
    function grid(tick) {
        return tick.append("line")
            .attr("class", "grid")
            .attr("x2", width - marginLeft - marginRight)
            .attr("stroke", "currentColor")
            .attr("stroke-opacity", 0.1);
    }

    // position the bars
    function position(rect, x, y) {
        rect
            .attr("x", x)
            .attr("y", y)
            .attr("width", xScale.bandwidth())
            .attr("height", i => yScale(0) - yScale(Y[i]));
    }


    // adding the swatches to the chart.
    function swatches() {
        const swatches = svg.append("g")
            .attr("font-family", "sans-serif")
            .attr("font-size", legendFontSize)
            .attr("text-anchor", "start")
            .selectAll("g")
            .data(xDomain)
            .join("g")
            .attr("transform", (z, i) => `translate(0,${i * legendColorBoxSize[1] + i * legendColorBoxGap })`);
        
        // adding the swatch color to the chart.

        swatches.append("rect")
            .attr("x", xLegend)
            .attr("y", yLegend )
            .attr("width", legendColorBoxSize[0])
            .attr("height", legendColorBoxSize[1])
            .attr("fill", color);

        // adding the swatch text to the chart.
        swatches.append("text")
            .attr("x", xLegend + legendColorBoxSize[0] + legendColorBoxGap)
            .attr("y", yLegend + legendColorBoxSize[1]/2 - legendFontSize/2)
            .attr("dy", "1em")
            .text(z => z);
        
        return swatches;
    }
    if (legend) swatches();

    return Object.assign(svg.node(), {value: null});
}