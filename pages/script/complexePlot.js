export function ComplexeLineChart(data, {
    values = ([value]) => value, // given d in data, returns the (quantitative) x-value
    categories = ([, categories]) => categories,  // given d in data, returns the (temporal) y-value
    inerClass = ([, , inerClass]) => inerClass, // given d in data, returns the (categorical) z-value
    std = ([, , , std]) => std, // given d in data, returns the (categorical) z-value

    title = "", // title of the chart
    titleFontSize = 20, // font size of the title

    defined, // for gaps in data

    curve = d3.curveMonotoneX, // method of interpolation between points

    width = 640, // outer width, in pixels
    height = 400, // outer height, in pixels

    margin = { top: 20, right: 30, bottom: 30, left: 50 },

    xType = d3.scaleLinear, // type of x-scale
    yType = d3.scaleLinear, // type of y-scale

    xDomain, // [xmin, xmax]
    yDomain, // [ymin, ymax]

    xRange = [margin.left, width - margin.right], // [left, right]
    yRange = [height - margin.bottom, margin.top], // [bottom, top]

    yFormat, // a format specifier string for the y-axis
    xFormat = d3.format(".0s"), // a format specifier string for the x-axis
    xLabel, // a label for the x-axis
    yLabel, // a label for the y-axis
    zDomain, // array of z-values
    labelFontSize = 20, // font size of axis labels

    color = d3.scaleOrdinal(d3.schemeCategory10), // stroke color of line, as a constant or a function of *z*

    strokeLinecap, // stroke line cap of line
    strokeLinejoin, // stroke line join of line
    strokeWidth = 2, // stroke width of line
    strokeOpacity = 1, // stroke opacity of line

    circlesRadius = 5, // radius of circles

    tooltipFontSize = 15, // font size of tooltip text
    tooltipBoxSize = [100, tooltipFontSize*2],
    tooltipCircleRadius = circlesRadius*2,
    tooltipTopMargin = tooltipCircleRadius + 10,

    mixBlendMode = "multiply", // blend mode of lines

    displayLegend = true, // show a legend?
    xLegend = margin.left + 15, // x-axis legend
    yLegend = 0, // y-axis legend
    legendColorBoxSize = [10, 10], // size of the color box in the legend
    legendColorBoxGap = 5, // margin of the color box in the legend
    legendFontSize = 12, // font size of the legend

    graphicalreduction = 0.1, // graphical reduction of the chart 
    timeout, // timeout for the tooltip

    voronoi // show a Voronoi overlay? (for debugging)
    } = {}) {
    // Compute values.
    // We compute the x, y, z, and defined values for each data point.
    const X = d3.map(data, categories);
    const Y = d3.map(data, values);
    const Z = d3.map(data, inerClass);
    const W = d3.map(data, std);
    const O = d3.map(data, d => d);
    if (defined === undefined) defined = (d, i) => !isNaN(X[i]) && !isNaN(Y[i]);
    const D = d3.map(data, defined);

    // Compute default domains, and unique the z-domain.
    // The Domain is the range of values that the data can take on.
    let xMinMaxValue;
    let xDynamicRange;
    if(typeof X[0] !== "string"){
        xMinMaxValue = d3.extent(X);
        xDynamicRange = xMinMaxValue[1] - xMinMaxValue[0];

        if (xDomain === undefined) xDomain = [xMinMaxValue[0] - xDynamicRange*graphicalreduction, xMinMaxValue[1] + xDynamicRange*graphicalreduction];

    }
    else{
        xType = d3.scaleBand;
        xDomain = X;
    }
    
    const yMinMaxValue = [d3.min(Y, d => typeof d === "string" ? +d : d), d3.max(Y, d => typeof d === "string" ? +d : d)];
    const yDynamicRange = yMinMaxValue[1] - yMinMaxValue[0];

    if (xDomain === undefined) xDomain = [xMinMaxValue[0] - xDynamicRange*graphicalreduction, xMinMaxValue[1] + xDynamicRange*graphicalreduction];
    // if Y is a string, then we need to coerce it to a number.
    if (yDomain === undefined) yDomain = [yMinMaxValue[0] - yDynamicRange*graphicalreduction, yMinMaxValue[1] + yDynamicRange*graphicalreduction];
    // zDomain is the set of all possible values that the z variable can take on.
    if (zDomain === undefined) zDomain = Z;
    zDomain = new d3.InternSet(zDomain);

    // Omit any data not present in the z-domain.
    const I = d3.range(X.length).filter(i => zDomain.has(Z[i]));

    // Construct scales and axes.
    const xScale = xType(xDomain, xRange);
    // const yScale = yType(yDomain, yRange);

    let yScale;
    if (yType == d3.scaleLog) {
        yDomain = [yMinMaxValue[0] <= 0 ? 0.0001 : yMinMaxValue[0], yMinMaxValue[1]];
        yScale = d3.scaleLog(yDomain, yRange)
    }
    else {
        yScale = yType(yDomain, yRange);
    }

    const xAxis = d3.axisBottom(xScale).ticks(width / 80, xFormat).tickSizeOuter(0);
    const yAxis = d3.axisLeft(yScale).ticks(height / 60, yFormat);

    // Construct a line generator.
    // Take the data point by point, and draw a line between them acording to the curve specified.
    const line = d3.line()
        .defined(i => D[i])
        .curve(curve)
        .x(i => xScale(X[i]))
        .y(i => yScale(Y[i]));
    
    const stdAreaLine = d3.area()
        .defined(i => D[i])
        .curve(curve)
        .x(i => xScale(X[i]))
        .y0(i => yScale(Y[i] - W[i]))
        .y1(i => yScale(Y[i] + W[i]));


    // Construct a new SVG. this is the main container for the chart.
    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto; height: intrinsic;")
        .style("-webkit-tap-highlight-color", "transparent")
        // all of the following are for accessibility ans interaction.
        .on("pointerenter", pointerentered)
        .on("pointermove", pointermoved)
        .on("pointerleave", pointerleft)
        .on("touchstart", event => event.preventDefault());

    // optional Voronoi display (for fun).
    // this is a way to see the points that are being used to draw the line.
    if (voronoi) svg.append("path")
        .attr("fill", "none")
        .attr("stroke", "#ccc")
        .attr("d", d3.Delaunay
            .from(I, i => xScale(X[i]), i => yScale(Y[i]))
            .voronoi([0, 0, width, height])
            .render());
    
    // add the x-axis to the chart.
    svg.append("g")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(xAxis)
        .attr("font-size", labelFontSize)
        // change orientation of x-axis labels.
        .call(g => g.selectAll("text")
        .attr("text-anchor", "end")
        .attr("transform", "rotate(-45)"))
        .call(g => g.select(".domain").remove())
        .call(voronoi ? () => {} : g => g.selectAll(".tick line").clone()
            .attr("y2", margin.top + margin.bottom - height)
            .attr("stroke-opacity", 0.1))
        .call(g => g.append("text")
            .attr("font-size", labelFontSize)
            .attr("x", width - margin.right)
            .attr("y", + margin.bottom/2)
            .attr("text-anchor", "end")
            .attr("fill", "currentColor")

            .text(xLabel));

    // add the y-axis to the chart.
    svg.append("g")
        .attr("transform", `translate(${margin.left},0)`)
        .call(yAxis)
        .attr("font-size", labelFontSize)
        .call(g => g.select(".domain").remove())
        .call(voronoi ? () => {} : g => g.selectAll(".tick line").clone()
            .attr("x2", width - margin.left - margin.right)
            .attr("stroke-opacity", 0.1))
        .call(g => g.append("text")
            .attr("x", -margin.left)
            .attr("y", 10 + labelFontSize/2)
            .attr("fill", "currentColor")
            .attr("text-anchor", "start")
            .text(yLabel));
        
    // add the title to the chart.
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", 10 + titleFontSize)
        .attr("text-anchor", "middle")
        .attr("fill", "currentColor")
        .attr("font-size", titleFontSize)
        .text(title);
    
    // add circles to the chart where the datapoints are
    const circles = svg.append("g");

    // console.log(yScale.range());
    // for(let i of I ) {
    //     console.log(Y[i]);
    // }

    circles
        .attr("fill", typeof color === "string" ? color : null)
        .selectAll("circle")
        .data(I)
        .join("circle")
        .filter(i => D[i])
        .attr("cx", (I) => xScale(X[I]))
        .attr("cy", (I) => yScale(Y[I]))
        .attr("r", circlesRadius)
        .attr("fill", typeof color === "function" ? (i) => color(Z[i]) : null);

    // add the area of the standard deviation to the chart.
    const stdArea = svg.append("g")
        .attr("fill", "none")
        .attr("stroke", typeof color === "string" ? color : null)
        .attr("stroke-linecap", strokeLinecap)
        .attr("stroke-linejoin", strokeLinejoin)
        .attr("stroke-width", strokeWidth)
        .attr("stroke-opacity", strokeOpacity)
        .selectAll("path")
        .data(d3.group(I, i => Z[i]))
        .join("path")
        .style("mix-blend-mode", mixBlendMode)
        // strocked area
        // .attr("stroke", typeof color === "function" ? ([z]) => color(z) : null)
        // .attr('stroke-dasharray', '5,5')
        // .attr('stroke-opacity', .3)
        .attr('fill', typeof color === "function" ? ([z]) => color(z) : null)
        .attr("fill-opacity", .3)
        .attr("d", ([, I]) => stdAreaLine(I));
    
    // add the line to the chart.
    const path = svg.append("g")
        .attr("fill", "none")
        .attr("stroke", typeof color === "string" ? color : null)
        .attr("stroke-linecap", strokeLinecap)
        .attr("stroke-linejoin", strokeLinejoin)
        .attr("stroke-width", strokeWidth)
        .attr("stroke-opacity", strokeOpacity)
        .selectAll("path")
        .data(d3.group(I, i => Z[i]))
        .join("path")
        .style("mix-blend-mode", mixBlendMode)
        .attr("stroke", typeof color === "function" ? ([z]) => color(z) : null)
        .attr("d", ([, I]) => line(I));
    
    // console.log(path);
    // console.log(d3.group(I, i => Z[i]));
    // for(let i of I) {
    //     console.log(D[i]);
    // }

    // add the dot when the mouse is over the line.
    const dot = svg.append("g")
        .attr("display", "none");

    dot.append("circle")
        .attr("r", tooltipCircleRadius)
        .call(dot => dot.append("title"));
            // .text(i => [X[i], `${Y[i]} sec`].join("\n")));
    

    // dot.append("path")
    //     .attr("fill", "white")
    //     .attr("stroke", "black")
    //     .attr("stroke-width", 2)
    //     .attr("d", `M${-tooltipBoxSize[0] / 2  },5H-5l5,-5l5,5H${tooltipBoxSize[0] / 2 }v${tooltipBoxSize[1]}h-${tooltipBoxSize[0]}z`)
    //     .attr("transform", `translate(0,${tooltipTopMargin})`);
    
    // dot.append("text")
    //     .attr("font-family", "sans-serif")
    //     .attr("font-size", tooltipFontSize)
    //     .attr("fill", "black")
    //     .attr("text-anchor", "middle")
    //     .attr("y", tooltipBoxSize[1]/2 + tooltipFontSize/2 + tooltipTopMargin + 5);


    function swatches() {
        // adding the swatches to the chart.
        const swatches = svg.append("g")
            .attr("font-family", "sans-serif")
            .attr("font-size", legendFontSize)
            .attr("text-anchor", "start")
            .selectAll("g")
            .data(zDomain)
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
            // .text(z => z)
            .html(function(z){ return "<a href=\"" + z + ".html\">"+ z +"</a>"; });

        return swatches;
    }

    // add the swatches to the chart.
    if (displayLegend) swatches();

    // if the timeout is defined, do something
    if (timeout != null) {
        // adding the display of the timeout value in the top right corner
        svg.append("text")
            .attr("x", width - margin.right)
            .attr("y", 10 + labelFontSize/2)
            .attr("text-anchor", "end")
            .attr("fill", "currentColor")
            .attr("font-size", labelFontSize)
            .text("Timeout: " + timeout + " s");
            
    }
    
    function pointermoved(event) {
        const [xm, ym] = d3.pointer(event);
        const i = d3.least(I, i => Math.hypot(xScale(X[i]) - xm, yScale(Y[i]) - ym)); // closest point
        // console.log(Z[i]);
        
        path.style("stroke", ([z]) => Z[i] === z ? null : "#ddd").filter(([z]) => Z[i] === z).raise();
        path.style("stroke-width", ([z]) => Z[i] === z ? circlesRadius : null).filter(([z]) => Z[i] === z).raise();
        stdArea.style("fill", ([z]) => Z[i] === z ? null : "#ddd").filter(([z]) => Z[i] === z).raise();
        dot.attr("transform", `translate(${xScale(X[i])},${yScale(Y[i])})`);
        // dot.style("fill", color(Z[i]));
        dot.style("fill", typeof color === "string" ? color : color(Z[i]));
        circles.selectAll('circle').style("fill", "#ddd");
        // if (Z) dot.select("text").text(Y[i].toFixed(2));
        if (Z) dot.select("title").text(
            [`${xLabel} : ${xFormat(X[i])}`, 
            `${yLabel} : ${Y[i].toFixed(4)}`,
            `σ : ${W[i].toFixed(4)}`].join("\n")
        );

        svg.property("value", O[i]).dispatch("input", {bubbles: true});
    }

    function pointerentered() {
        path.style("mix-blend-mode", null).style("stroke", "#ddd");
        dot.attr("display", null);
    }

    function pointerleft() {
        // reset the chart.
        circles.selectAll('circle').style("fill", null);
        path.style("mix-blend-mode", mixBlendMode).style("stroke", null).style("stroke-width", null);
        stdArea.style("fill", null);
        dot.attr("display", "none");
        svg.node().value = null;
        svg.dispatch("input", {bubbles: true});
    }

    return Object.assign(svg.node(), {value: null});
}