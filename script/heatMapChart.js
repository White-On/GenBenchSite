export function HeatMap(data,{
    x = ([x]) => x, 
    y = ([, y]) => y, 
    value = ([, , value]) => value,

    title,

    width = width,
    height = height,

    margin = { top: 20, right: 20, bottom: 30, left: 40 },

    color,

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
    const CX = d3.map(data, x); // column x-axis
    const CY = d3.map(data, y); // column y-axis
    const V = d3.map(data, value); // value of the cell

    const I = d3.range(V.length);

    // console.log(CX);
    // console.log(CY);
    // console.log(V);

    // console.log(I);

     // create scales for x and y axis
    var xScale = d3.scaleBand()
        .range([margin.left, width - margin.right])
        .domain(CX)
        .padding(0);
    var yScale = d3.scaleBand()
        .range([margin.top, height - margin.bottom])
        .domain(CY)
        .padding(0);

    // console.log(xScale.domain());
    // console.log(yScale.domain());
    // console.log(xScale.bandwidth());
    // console.log(xScale(CX[0]));

    const xAxis = d3.axisBottom(xScale);
    const yAxis = d3.axisLeft(yScale);

    // create SVG element and set size
    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto; height: intrinsic;")
        .style("-webkit-tap-highlight-color", "transparent")
  
   
    // create color scale
    var colorScale = d3.scaleSequential(d3.interpolateViridis)
      .domain([0, d3.max(V)]);
  
    // create rectangles for each cell in the heatmap
    let rect = svg.selectAll("rect")
        .data(I)
        .join("rect")
        .attr("x", (i) => xScale(CX[i]))
        .attr("y", (i) => yScale(CY[i]))
        .attr("width", Math.floor(xScale.bandwidth()) +1)
        .attr("height", Math.floor(yScale.bandwidth())+1)
        .attr("fill", (i) => colorScale(V[i]));
    
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
    
    return svg.node(); 
  }
  