export  function LineChart(data, {
    x = ([x]) => x, // given d in data, returns the (temporal) x-value
    y = ([, y]) => y, // given d in data, returns the (quantitative) y-value
    z = () => 1, // given d in data, returns the (categorical) z-value
    title, // given d in data, returns the title text
    defined, // for gaps in data

    curve = d3.curveBumpX, // method of interpolation between points

    marginTop = 20, // top margin, in pixels
    marginRight = 30, // right margin, in pixels
    marginBottom = 30, // bottom margin, in pixels
    marginLeft = 50, // left margin, in pixels

    width = 640, // outer width, in pixels
    height = 400, // outer height, in pixels

    xType = d3.scaleLinear, // type of x-scale
    yType = d3.scaleLinear, // type of y-scale

    xDomain, // [xmin, xmax]
    yDomain, // [ymin, ymax]

    xRange = [marginLeft, width - marginRight], // [left, right]
    yRange = [height - marginBottom, marginTop], // [bottom, top]

    yFormat, // a format specifier string for the y-axis
    xFormat = d3.format(".0s"), // a format specifier string for the x-axis
    yLabel, // a label for the y-axis
    zDomain, // array of z-values
    labelFontSize = 20, // font size of axis labels

    color = "blue", // stroke color of line, as a constant or a function of *z*

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

    legend = false, // show a legend?
    xLegend = width*0.1, // x-axis legend
    yLegend = height*0.1, // y-axis legend
    legendColorBoxSize = [20, 20], // size of the color box in the legend
    legendColorBoxGap = 5, // margin of the color box in the legend
    legendFontSize = 20, // font size of the legend

    graphicalreduction = 0.05, // graphical reduction of the chart 

    voronoi // show a Voronoi overlay? (for debugging)
    } = {}) {
    // Compute values.
    // We compute the x, y, z, and defined values for each data point.
    const X = d3.map(data, x);
    const Y = d3.map(data, y);
    const Z = d3.map(data, z);
    const O = d3.map(data, d => d);
    if (defined === undefined) defined = (d, i) => !isNaN(X[i]) && !isNaN(Y[i]);
    const D = d3.map(data, defined);

    // Compute default domains, and unique the z-domain.
    // The Domain is the range of values that the data can take on.
    const xMinMaxValue = d3.extent(X);
    const xDynamicRange = xMinMaxValue[1] - xMinMaxValue[0];
    
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
    const yScale = yType(yDomain, yRange);
    const xAxis = d3.axisBottom(xScale).ticks(width / 80, xFormat).tickSizeOuter(0);
    const yAxis = d3.axisLeft(yScale).ticks(height / 60, yFormat);

    // Compute titles.
    const T = title === undefined ? Z : title === null ? null : d3.map(data, title);

    // Construct a line generator.
    // Take the data point by point, and draw a line between them acording to the curve specified.
    const line = d3.line()
        .defined(i => D[i])
        .curve(curve)
        .x(i => xScale(X[i]))
        .y(i => yScale(Y[i]));

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
        .attr("transform", `translate(0,${height - marginBottom})`)
        .call(xAxis)
        .attr("font-size", labelFontSize)
        // change orientation of x-axis labels.
        // .attr("text-anchor", "end")
        // .selectAll("text")
        // .attr("transform", "rotate(-45)")
        .call(g => g.select(".domain").remove())
        .call(voronoi ? () => {} : g => g.selectAll(".tick line").clone()
            .attr("y2", marginTop + marginBottom - height)
            .attr("stroke-opacity", 0.1));

    // add the y-axis to the chart.
    svg.append("g")
        .attr("transform", `translate(${marginLeft},0)`)
        .call(yAxis)
        .attr("font-size", labelFontSize)
        .call(g => g.select(".domain").remove())
        .call(voronoi ? () => {} : g => g.selectAll(".tick line").clone()
            .attr("x2", width - marginLeft - marginRight)
            .attr("stroke-opacity", 0.1))
        .call(g => g.append("text")
            .attr("x", -marginLeft)
            .attr("y", 10 + labelFontSize/2)
            .attr("fill", "currentColor")
            .attr("text-anchor", "start")
            .text(yLabel));
    
    // add circles to the chart where the datapoints are
    const circles = svg.append("g");

    circles
        .attr("fill", typeof color === "string" ? color : null)
        .selectAll("circle")
        .data(I)
        .join("circle")
        .attr("cx", (I) => xScale(X[I]))
        .attr("cy", (I) => yScale(Y[I]))
        .attr("r", circlesRadius)
        .attr("fill", typeof color === "function" ? (i) => color(Z[i]) : null);

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
    
    

    // add the dot when the mouse is over the line.
    const dot = svg.append("g")
        .attr("display", "none");

    dot.append("circle")
        .attr("r", tooltipCircleRadius);

    dot.append("path")
        .attr("fill", "white")
        .attr("stroke", "black")
        .attr("stroke-width", 2)
        .attr("d", `M${-tooltipBoxSize[0] / 2  },5H-5l5,-5l5,5H${tooltipBoxSize[0] / 2 }v${tooltipBoxSize[1]}h-${tooltipBoxSize[0]}z`)
        .attr("transform", `translate(0,${tooltipTopMargin})`);
    
    dot.append("text")
        .attr("font-family", "sans-serif")
        .attr("font-size", tooltipFontSize)
        .attr("fill", "black")
        .attr("text-anchor", "middle")
        .attr("y", tooltipBoxSize[1]/2 + tooltipFontSize/2 + tooltipTopMargin + 5);


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
    if (legend) swatches();

    function pointermoved(event) {
        const [xm, ym] = d3.pointer(event);
        const i = d3.least(I, i => Math.hypot(xScale(X[i]) - xm, yScale(Y[i]) - ym)); // closest point
        // console.log(Z[i]);
        
        path.style("stroke", ([z]) => Z[i] === z ? null : "#ddd").filter(([z]) => Z[i] === z).raise();
        path.style("stroke-width", ([z]) => Z[i] === z ? circlesRadius*2 : null).filter(([z]) => Z[i] === z).raise();
        dot.attr("transform", `translate(${xScale(X[i])},${yScale(Y[i])})`);
        // dot.style("fill", color(Z[i]));
        dot.style("fill", typeof color === "string" ? color : color(Z[i]));
        circles.selectAll('circle').style("fill", "#ddd");
        // TODO fix the Titles
        if (T) dot.select("text").text(Y[i].toFixed(2));
        svg.property("value", O[i]).dispatch("input", {bubbles: true});
    }

    function pointerentered() {
        path.style("mix-blend-mode", null).style("stroke", "#ddd");
        dot.attr("display", null);
    }

    function pointerleft() {
        circles.selectAll('circle').style("fill", null);
        path.style("mix-blend-mode", mixBlendMode).style("stroke", null).style("stroke-width", null);
        dot.attr("display", "none");
        svg.node().value = null;
        svg.dispatch("input", {bubbles: true});
    }

    return Object.assign(svg.node(), {value: null});
}