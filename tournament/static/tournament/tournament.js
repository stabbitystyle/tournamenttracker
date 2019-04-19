// function addEntrant() {

//     var newEntrantDiv = document.createElement("div");
//     newEntrantDiv.className = "fieldWrapper";
//     newEntrantInterior = `
//         <div class="fieldWrapper">
//             <label for="id_password">Number of Entrants</label>
//             {{ form.numberOfEntrants }}
//             <sub>{{ form.numberOfEntrants.errors.as_text }}</sub>
//         </div>
//     `
//     newEntrantDiv.innerHTML = newEntrantInterior;
  
//     var skill_list = document.getElementById("skill-list");
//     skill_list.insertBefore(newSkillField, document.getElementById("add-skill-li"));
//   }

function csvToTree(text) {
    var table = d3.csvParse(text);
    var root = d3.stratify()
        .id(function(d) { return d.id; })
        .parentId(function(d) { return d.parent; })
        (table);

    var treeLayout = d3.tree()
        .size([400, 200])

    treeLayout(root)

    // Nodes
    d3.select('svg g.nodes')
        .selectAll('circle.node')
        .data(root.descendants())
        .enter()
        .append('circle')
        .classed('node', true)
        .attr('cx', function(d) {return d.x;})
        .attr('cy', function(d) {return d.y;})
        .attr('r', 4);

    // Links
    d3.select('svg g.links')
        .selectAll('line.link')
        .data(root.links())
        .enter()
        .append('line')
        .classed('link', true)
        .attr('x1', function(d) {return d.source.x;})
        .attr('y1', function(d) {return d.source.y;})
        .attr('x2', function(d) {return d.target.x;})
        .attr('y2', function(d) {return d.target.y;});
    
    // node.append('text')
	// 	.attr('class', 'name')
	// 	.attr('x', 8)
	// 	.attr('y', -6)
	// 	.text(d => `${d.data.name}`)

	// node.append('text')
	// 	.attr('x', 8)
	// 	.attr('y', 8)
	// 	.attr('dy', '.71em')
	// 	.attr('class', 'about lifespan')
	// 	.text(d => `${d.data.born} - ${d.data.died}`)
}

// courtesy of https://bl.ocks.org/mbostock/2429963
function elbow(d, i) {
    return "M" + d.source.y + "," + d.source.x
        + "V" + d.target.x + "H" + d.target.y;
  }
