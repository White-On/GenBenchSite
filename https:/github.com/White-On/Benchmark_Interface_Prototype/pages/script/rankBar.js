export function rankBar(data, {

    width = 600,
    height = 50,

    color = d3.scaleSequential(d3.interpolateViridis),

    fontSize = 24,
    gap = 10,

    contentFolderPath = "",


} = {}) {

    let textBoxSize = 120;
    let chartSizeStep = 0;
    let arrowSize = 30;
    // to round the number of pixel to avoid glitches
    let vrb = 0;

    // we make sure the dico is sorted by the value
    let order = {};

    Object.keys(data).sort(function(a, b) {
    return data[a] - data[b];
    }).forEach(function(key) {
    order[key] = data[key];
    });

    // we create an array of array to separate the elements with a value that follow each other and make transition between them
    // we then get a list of array with ordered elements separated by the same value

    let chartBatch = [];
    let tmpCache = [];
    for (let j = 0; j < Object.keys(order).length; j++) {
        tmpCache.push(Object.keys(order)[j]);
        if (order[Object.keys(order)[j]] == order[Object.keys(order)[j+1]]) {
            chartBatch.push(tmpCache);
            tmpCache = [];
        }
    }
    chartBatch.push(tmpCache);


    const colorScale = color
    .domain([0,d3.max(Object.values(order))*1.4]);

    let totalSize = 0;
    for(let element of chartBatch){
        totalSize += element.length * (arrowSize + textBoxSize) - (arrowSize-gap);
    }



    let xScale = d3.scaleLinear([0,totalSize], [0,width])
    let yScale = d3.scaleLinear([0,50],[0, height])

    let svg = d3.select("body")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto;");

    for (let m = 0; m < chartBatch.length; m++) {
        // we create a group for each element of the array
        let val = chartBatch[m];
        let chart = svg.append("g")
            .attr("transform", "translate(0, 0)");  

        let group = chart.selectAll("g")
            .data(val)
            .enter()
            .append("g")
            .attr("transform", (d, i) => "translate(" + xScale(chartSizeStep + i * (arrowSize + textBoxSize)).toFixed(vrb) + ", 0)");

        chartSizeStep = chartSizeStep + val.length * (arrowSize + textBoxSize) - (arrowSize-gap);

        // we add two rectangles in each group 
        group.append("rect")
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", xScale(textBoxSize + 1).toFixed(vrb))
            .attr("height", yScale(50))
            .attr("fill", (d,i) => colorScale(order[val[i]]));

        let lastrect = group.append("rect")
            .attr("x", xScale(textBoxSize + 1).toFixed(vrb))
            .attr("y", 0)
            .attr("width", xScale(arrowSize).toFixed(vrb))
            .attr("height", yScale(50))
            .attr("fill", (d,i) => colorScale(order[val[i+1]]));

        // we add a triangle in one of the rectangle
        group.append("path")
            .attr("d", "M " + xScale(textBoxSize).toFixed(vrb) + " 0 L " + xScale(textBoxSize + arrowSize).toFixed(vrb) + " "+ yScale(25) +" L " + xScale(textBoxSize).toFixed(vrb) + " "+ yScale(50) +"Z")
            .attr("fill", (d,i) => colorScale(order[val[i]]));

        // we add a text in each group
        group.append("text")
            .attr("x", xScale(textBoxSize/2))
            .attr("y", yScale(25))
            .attr("text-anchor", "middle")
            .attr("dominant-baseline", "central")
            .attr("font-size", fontSize)
            .attr("font-weight", 400)
            .text((d) => d)
            .attr("fill", "white")
            .on('click', function(d) {
                // we redirect to the page of the element
                window.location.href = contentFolderPath + d.srcElement.innerHTML + ".html";
                
            })
            .style("cursor", "pointer");

        // we remove the last rect of the last group
        lastrect
            .filter((d, i) => i === val.length - 1)
            .remove();

        // we remove the last triangle of the last group
        group
            .filter((d, i) => i === val.length - 1)
            .selectAll("path")
            .remove();
        }
    
        return svg.node();

    }