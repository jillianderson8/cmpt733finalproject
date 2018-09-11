function showBelowConfidence(confidence, confidenceContainer, countsContainer) {
	var below = 'confidence0';
	var above = 'confidence110'
	for (var i = 10; i < confidence; i += 10) {
		below += ', .confidence' + i;
	}
	for (var i = 100; i >= confidence; i -= 10) {
		above += ', .confidence' + i;
	}
	$(below).hide();
	var showing = $(above);
	showing.show();
	counts = {}
	$.each(showing, function(index, tree) {
		var key = tree.getAttribute("tree");
		counts[key] = counts.hasOwnProperty(key) ? counts[key] + 1 : 1;
	});
	showCounts(confidence, counts, confidenceContainer, countsContainer);
}
function showCounts(confidence, counts, confidenceContainer, countsContainer) {
	var text = "" + confidence + "% confidence";
	confidenceContainer.html(text);
	text = "";
	for (var i in counts) {
		text += (text ? ", " : "") + counts[i] + " " + i + " trees";
	}
	countsContainer.html(text);
}
function getBox(show, x, y, width, height, tree, confidence, confidenceClass) {
	var color = tree == "banana" ? "yellow" : "white";
	var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
	svg.setAttribute("width", width);
	svg.setAttribute("height", height);
	svg.setAttribute("style", "position:absolute;left:" + x + "px;top:" + y + "px;");
	if (!show) {
		svg.setAttribute("display", "none");
	}
	svg.setAttribute("class", "confidence" + confidenceClass);
	svg.setAttribute("tree", tree);

	var label = document.createElementNS(svg.namespaceURI, "rect");
	label.setAttribute("x", 0);
	label.setAttribute("y", 0);
	label.setAttribute("height", 13);
	label.setAttribute("width", width);
	label.setAttribute("fill", "black");
	label.setAttribute("fill-opacity", 0.4);
	svg.appendChild(label);

	var box = document.createElementNS(svg.namespaceURI, "rect");
	box.setAttribute("x", 0);
	box.setAttribute("y", 0);
	box.setAttribute("height", height);
	box.setAttribute("width", width);
	box.setAttribute("stroke", color);
	box.setAttribute("fill-opacity", 0.0);
	box.setAttribute("stroke-width", 5);
	box.setAttribute("stroke-opacity", 0.6);
	svg.appendChild(box);

	var text = document.createElementNS(svg.namespaceURI, "text");
	text.setAttribute("x", 3);
	text.setAttribute("y", 11);
	text.setAttribute("fill", color);
	text.setAttribute("font-size", 10);
	text.setAttribute("font-weight", "bold");
	text.appendChild(document.createTextNode("" + confidence + "% " + tree));
	svg.appendChild(text);

	return svg;
}
function showPredictions(container, url, confidence) {
	counts = {}
	$.getJSON(url, function(predictions) {
		$.each(predictions, function(index, prediction) {
			if (prediction.confidence > 0.1) {
				var confidenceClass = (10 * Math.floor(prediction.confidence * 10));
				var width = Math.round(prediction.box[3]-prediction.box[1]);
				var height = Math.round(prediction.box[2]-prediction.box[0]);
				var obj = getBox(confidenceClass >= confidence, Math.round(prediction.box[0]), Math.round(prediction.box[1]), width, height, prediction.tree, Math.floor(prediction.confidence * 100), confidenceClass);
				container.appendChild(obj);
				if (confidenceClass >= confidence) {
					var key = prediction.tree;
					counts[key] = counts.hasOwnProperty(key) ? counts[key] + 1 : 1;
				}
			}
		});
	});
	return counts;
}
