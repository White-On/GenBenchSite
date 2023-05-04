export function HeatMap(data,{
    x = ([x]) => x, 
    y = ([, y]) => y, 
    value = ([, , value]) => value,

    width = width,
    height = height,

    margin = { top: 20, right: 20, bottom: 30, left: 40 },

    color,

    labelFontSize = 20, // font size of the labels

    xLabel, // label of the x-axis
    yLabel, // label of the y-axis

    cubeSize = 100, // size of the cube


} = {}) {
    const CX = d3.map(data, x); // column x-axis
    const CY = d3.map(data, y); // column y-axis
    const V = d3.map(data, value); // value of the cell

    const I = d3.range(V.length);

    // we calculate the number of tasks in the theme
    let numberOfXElement = [...new Set(CX)].length;
    let numberOfYElement = [...new Set(CY)].length;

     // create scales for x and y axis
    var xScale = d3.scaleBand()
        .range([margin.left, margin.left+numberOfXElement*cubeSize - margin.right])
        .domain(CX)
        .padding(0);
    var yScale = d3.scaleBand()
        .range([margin.top, margin.top +numberOfYElement*cubeSize - margin.bottom])
        .domain(CY)
        .padding(0);

    console.log(xScale.domain());
    console.log(yScale.domain());
    console.log(xScale.bandwidth());
    // console.log(xScale(CX[0]));

    const xAxis = d3.axisTop(xScale);
    const yAxis = d3.axisLeft(yScale);

    // create SVG element and set size
    const svg = d3.create("svg")
        .attr("width", margin.left + numberOfXElement*cubeSize - margin.right)
        .attr("height", margin.top + numberOfYElement*cubeSize - margin.bottom)
        .attr("viewBox", [0, 0, margin.left + numberOfXElement*cubeSize - margin.right, margin.top + numberOfYElement*cubeSize - margin.bottom])
        .attr("style", "max-width: 100%; height: auto; height: intrinsic;")
        .style("-webkit-tap-highlight-color", "transparent")
  
   
    // create color scale
    var colorScale = d3.scaleSequential(d3.interpolateViridis)
      .domain([0, d3.max(V)*1.4]);
  
    // create rectangles for each cell in the heatmap
    let rect = svg.selectAll("rect")
        .data(I)
        .join("rect")
        .attr("x", (i) => xScale(CX[i]))
        .attr("y", (i) => yScale(CY[i]))
        .attr("width", xScale.bandwidth().toFixed(0))
        .attr("height",yScale.bandwidth().toFixed(0))
        .attr("fill", (i) => colorScale(V[i]));
    
    // add the x-axis to the chart.
    svg.append("g")
        .attr("transform", `translate(0,${margin.top})`)
        .call(xAxis)
        .attr("font-size", labelFontSize)
        .call(g => g.select(".domain").remove())
        .call(g => g.append("text")
            .text(xLabel))
            .on('click', function(d) {
                // we redirect to the page of the element
                window.location.href = d.srcElement.innerHTML + ".html";
                
            })
            .style("cursor", "pointer");
  
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
            .text(yLabel))
            .on('click', function(d) {
                // we redirect to the page of the element
                window.location.href = d.srcElement.innerHTML + ".html";
                
            })
            .style("cursor", "pointer");
    
    return svg.node(); 
  }
  