console.log("starting stats.js");

load_script("https://d3js.org/d3.v4.min.js").then(function() {

    var jq = $("svg#stats")
    var height = jq.height();
    var width = innerWidth * .9;
    if (width > 1000) width = 1000;

    svg = d3.select("svg#stats"),
        margin = {top: 20, right: 20, bottom: 30, left: 50},
        width = +width - margin.left - margin.right,
        height = +height - margin.top - margin.bottom,
        g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    console.log("svg:", svg);
    console.log("width:", width);

    x = d3.scaleTime().rangeRound([0, width]);

    y = d3.scaleLinear().rangeRound([height, 0]);

    line = d3.line()
        .x(function(d) {
            return x(d.datetime);
        })
        .y(function(d) {
            return y(d.accuracy);
        });

    console.log("line:", line);

    $.getJSON("/api/tests/?format=json", response => {
        console.log("test response:", response);
        data = response.results.map(function(result) {
            return {
                accuracy: new Number(result.accuracy),
                datetime: new Date(result.datetime),
            };
        });
        console.log("data:", data);

        x.domain(d3.extent(data, (d) => d.datetime ));
        y.domain(d3.extent(data, (d) => d.accuracy ));
        console.log("domained");

        g.append("g")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(x))
            .select(".domain")
            .remove();

        console.log("appended first g");

        g.append("g")
            .call(d3.axisLeft(y))
            .append("text")
            .attr("fill", "#000")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", "0.71em")
            .attr("text-anchor", "end")
            .text("Accuracy");


        console.log("appended second g");

        g.append("path")
            .datum(data)
            .attr("fill", "none")
            .attr("stroke", "steelblue")
            .attr("stroke-linejoin", "round")
            .attr("stroke-linecap", "round")
            .attr("stroke-width", 1.5)
            .attr("d", line); 


        console.log("appended third g");

    });

});

