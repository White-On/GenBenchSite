export function arrowRank(cls, element,{

    width = 200,
    height = 50,

    color = d3.scaleSequential(d3.interpolateViridis),

    fontSize = 24,

    contentFolderPath = "",


} = {}) {

    let arrowSize = 30;
    
    // to round the number of pixel to avoid glitches
    let vrb = 0;

    // we make sure the dico is sorted by the value
    let order = {};

    Object.keys(cls).sort(function(a, b) {
    return cls[a] - cls[b];
    }).forEach(function(key) {
    order[key] = cls[key];
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

    // we only keep the batch with the element we want
    chartBatch = chartBatch.filter((d) => d.includes(element));


    const colorScale = color
    .domain([0,d3.max(Object.values(order))*1.4]);


    let xScale = d3.scaleLinear([0,200], [0,width])
    let yScale = d3.scaleLinear([0,50],[0, height])

    let svg = d3.select("body")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto;");

    
    // we create a group for each element of the array
    let val = [element];
    let chart = svg.append("g")
        .attr("transform", "translate(0, 0)");  

    let group = chart.selectAll("g")
        .data(val)
        .enter()
        .append("g")
        .attr("transform","translate(0, 0)");
        // .attr("transform", (d, i) => "translate(" + xScale(chartSizeStep + i * (arrowSize + textBoxSize)).toFixed(vrb) + ", 0)");

    let textBoxSize = width - arrowSize;
    // we check if the element is not the first or the last of the array to change the size of the rectangle
    // if the elemnt is in the midle of the array we make the rectangle bigger
    if (element != chartBatch[chartBatch.length-1][chartBatch[chartBatch.length-1].length-1] && element != chartBatch[0][0]){
        textBoxSize = width - arrowSize*2;
    }

    // we add two rectangles in each group 
    group.append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", xScale(textBoxSize + 1).toFixed(vrb))
        .attr("height", yScale(50))
        .attr("fill", (d,i) => colorScale(order[val[i]]));

    // let lastrect = group.append("rect")
    //     .attr("x", xScale(textBoxSize + 1).toFixed(vrb))
    //     .attr("y", 0)
    //     .attr("width", xScale(arrowSize).toFixed(vrb))
    //     .attr("height", yScale(50))
    //     .attr("fill", (d,i) => colorScale(order[val[i+1]]));

    // we add a triangle in one of the rectangle if it's not the last element of a batch
    if(element != chartBatch[chartBatch.length-1][chartBatch[chartBatch.length-1].length-1]){
    group.append("path")
        .attr("d", "M " + xScale(textBoxSize).toFixed(vrb) + " 0 L " + xScale(textBoxSize + arrowSize).toFixed(vrb) + " "+ yScale(25) +" L " + xScale(textBoxSize).toFixed(vrb) + " "+ yScale(50) +" Z")
        .attr("fill", (d,i) => colorScale(order[val[i]]));
    }

    // we add a triangle in one of the rectangle if it's not the first element of a batch
    if(element != chartBatch[0][0]){
    // we first move the group to the left
    group.attr("transform", (d, i) => "translate(" + xScale(arrowSize).toFixed(vrb) + ", 0)");
    // then add the leftover of a arrow comming from the previous batch
    group.append("path")
        .attr("d", "M 0 0 L " + xScale(-arrowSize).toFixed(vrb) + " 0 L 0 "+ yScale(25) +" L"+ xScale(-arrowSize).toFixed(vrb) +" "+ yScale(50) + " L 0 "+ yScale(50) + "Z ")
        // .attr("d", "M " + xScale(arrowSize).toFixed(vrb) + " 0 L " + "0 0 L " + xScale(arrowSize).toFixed(vrb) + " "+ yScale(25) +" L " + xScale(textBoxSize + arrowSize).toFixed(vrb) + " "+ yScale(50) +"Z")
        .attr("fill", (d,i) => colorScale(order[val[i]]));
    }
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

    // // we remove the last rect of the last group
    // lastrect
    //     .filter((d, i) => i === val.length - 1)
    //     .remove();

    // // we remove the last triangle of the last group
    // group
    //     .filter((d, i) => i === val.length - 1)
    //     .selectAll("path")
    //     .remove();
    

    return svg.node();

}