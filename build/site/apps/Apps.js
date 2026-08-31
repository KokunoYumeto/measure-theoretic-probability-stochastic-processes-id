//App scripts for Random: Probability, Mathematical Statistics, and Stochastic Processes
"use strict";

//Constants
const HOR = 0, VERT = 1, LEFT = 0, RIGHT = 1, ABOVE = 2, BELOW = 3, AT = 4;
const PDF = 0, CDF = 1;

//Buttons
class Button {
	constructor(ct, title) {
        this.button = document.createElement("button");
		ct.appendChild(this.button);
		this.button.type = "button";
		this.button.title = title;
	}
	setMethod(app, method) {
		this.button.setAttribute("onclick", app + "." + method);
	}
	setIcon(src) {
		const img = document.createElement("img");
		img.setAttribute("src", src);
		this.button.appendChild(img);
	}
	setText(text) {
		this.button.innerHTML = text;
	}
	setDisabled(b) {
		this.button.disabled = b;
	}
	setStyle(style) {
		this.button.style = style;
	}
}
//Simulation app buttons
class StepButton extends Button {
	constructor(ct, app) {
		super(ct, "Step");
		const icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
		this.button.appendChild(icon);
		icon.setAttribute("width", 12);
		icon.setAttribute("height", 12);
		const poly = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
		icon.appendChild(poly);
		poly.setAttribute("fill", "darkred");
		poly.setAttribute("points", "2,2 10,6 2,10");
		this.setMethod(app, "step()");
	}
}
class RunButton extends Button {
	constructor(ct, app) {
		super(ct, "Run");
		const icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
		this.button.appendChild(icon);
		icon.setAttribute("width", 12);
		icon.setAttribute("height", 12);
		const poly1 = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
		icon.appendChild(poly1);
		poly1.setAttribute("fill", "darkred");
		poly1.setAttribute("points", "1,1 6,6 1,11");
		const poly2 = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
		icon.appendChild(poly2);
		poly2.setAttribute("fill", "darkred");
		poly2.setAttribute("points", "6,1 11,6 6,11");
		this.setMethod(app, "run()");
	}
}
class StopButton extends Button {
	constructor(ct, app) {
		super(ct, "Stop");
		const icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
		this.button.appendChild(icon);
		icon.setAttribute("width", 12);
		icon.setAttribute("height", 12);
		const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
		icon.appendChild(rect);
		rect.setAttribute("fill", "darkred");
		rect.setAttribute("x", 2);
		rect.setAttribute("y", 2);
		rect.setAttribute("width", 8);
		rect.setAttribute("height", 8);
		this.setMethod(app, "stop()");
	}
}
class ResetButton extends Button {
	constructor(ct, app) {
		super(ct, "Reset");
		const icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
		this.button.appendChild(icon);
		icon.setAttribute("width", 12);
		icon.setAttribute("height", 12);
		const poly = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
		icon.appendChild(poly);
		poly.setAttribute("fill", "darkred");
		poly.setAttribute("points", "1,6 6,1 6,11");
		const line1 = document.createElementNS("http://www.w3.org/2000/svg", "line");
		icon.appendChild(line1);
		line1.setAttribute("stroke", "darkred");
		line1.setAttribute("x1", 11);
		line1.setAttribute("y1", 1);
		line1.setAttribute("x2", 11);
		line1.setAttribute("y2", 11);
		const line2= document.createElementNS("http://www.w3.org/2000/svg", "line");
		icon.appendChild(line2);
		line2.setAttribute("stroke", "darkred");
		line2.setAttribute("x1", 1);
		line2.setAttribute("y1", 6);
		line2.setAttribute("x2", 11);
		line2.setAttribute("y2", 6);
		this.setMethod(app, "reset()");
	}
}
//SVG Markers
//Arrow marker
const arrowMarker = document.createElementNS("http://www.w3.org/2000/svg", "marker");
const arrowPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
arrowMarker.appendChild(arrowPath);
arrowMarker.setAttribute("id", "arrow");
arrowMarker.setAttribute("viewBox", "0 0 10 10");
arrowMarker.setAttribute("refX", "5");
arrowMarker.setAttribute("refY", "5");
arrowMarker.setAttribute("markerWidth", "10");
arrowMarker.setAttribute("markerHeight", "10");
arrowMarker.setAttribute("orient", "auto-start-reverse");
arrowPath.setAttribute("d", "M 0 0 L 10 5 L 0 10 z");
arrowPath.setAttribute("fill", "black");
//Tick marker
const tickMarker = document.createElementNS("http://www.w3.org/2000/svg", "marker");
const tickPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
tickMarker.appendChild(tickPath);
tickMarker.setAttribute("id", "tick");
tickMarker.setAttribute("viewBox", "0 0 10 10");
tickMarker.setAttribute("refX", "0");
tickMarker.setAttribute("refY", "5");
tickMarker.setAttribute("markerWidth", "10");
tickMarker.setAttribute("markerHeight", "10");
tickMarker.setAttribute("orient", "auto-start-reverse");
tickPath.setAttribute("d", "M 0 0 L 0 10");
tickPath.setAttribute("stroke", "black");
//Dot marker
const dotMarker = document.createElementNS("http://www.w3.org/2000/svg", "marker");
const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
dotMarker.appendChild(dot);
dot.setAttribute("cx", 5);
dot.setAttribute("cy", 5);
dot.setAttribute("r", 5);
dot.setAttribute("fill", "black");
dotMarker.setAttribute("id", "dot");
dotMarker.setAttribute("viewBox", "0 0 10 10");
dotMarker.setAttribute("refX", "5");
dotMarker.setAttribute("refY", "5");
dotMarker.setAttribute("markerWidth", "10");
dotMarker.setAttribute("markerHeight", "10");
//Parameter control in container ct, defined by an input and a label
class Parameter {
	constructor(ct, name, title) {
		this.label = document.createElement("label");
		this.label.title = title;
		this.input = document.createElement("input");
		this.input.type = "range";
		this.input.title = title;
		this.input.style = "width: 100px;";
		this.name = name;
		this.title = title;
		ct.appendChild(this.label);
		ct.appendChild(this.input);
	}
	setProperties(min, max, step, value) {
		this.input.min = min;
		this.input.max = max;
		this.input.step = step;
		this.format = Math.round(Math.log(1 / this.input.step) / Math.log(10));
		this.setValue(value);
	}
	setValue(x) {
		this.input.value = x;
		if (this.input.type == "range") this.label.innerHTML = this.name + " = " + x.toFixed(this.format);
		else if (this.input.type == "hidden") this.label.innerHTML = "";
		else this.label.innerHTML = this.name + " = ";
	}
	getValue() {
        const x = Number(this.input.value);
        this.setValue(x);
		return x;
	}	
	setDisabled(b) {
		this.input.disabled = b;
	}
	setMethod(app, method) {
		this.input.setAttribute("onchange", app + "." + method);
	}
	setType(type) {
		this.input.type = type;
		if (type == "hidden") this.label.innerHTML = "";
	}
	setTitle(name, title) {
		this.name = name;
		this.input.title = title;
		this.label.title = title;
	}
}
//Drop-down box
class Select {
	constructor(ct, title) {
		this.select = document.createElement("select");
		ct.appendChild(this.select);
		this.select.title = title;
	}
	setOptions(values, labels, selected) {
		for (let i = 0; i < values.length; i++) {
			this.addOption(values[i], labels[i]);
		}
		this.select.selectedIndex = selected;
	}
	addOption(value, label) {
		let option  = document.createElement("option");
		option.value = value;
		option.text = label;
		this.select.add(option);
	}
	setMethod(app, method) {
		this.select.setAttribute("onchange", app + "." + method);
	}
	getValue() {
		return this.select.value;
	}
	setValue(v) {
		this.select.value = v;
		this.select.dispatchEvent(new Event("change"));
	}
	setDisabled(b) {
		this.select.disabled = b;
	}
}
//Checkbox
class Check {
	constructor(ct, text, title) {
		this.check = document.createElement("input");
		ct.appendChild(this.check);
		this.check.type = "checkbox";
		this.check.title = title;
		this.label = document.createElement("label");
		ct.appendChild(this.label);
		this.label.for = this.check;
		this.label.innerHTML = text;
		this.label.title = title;
	}
	checked() {
		return this.check.checked;
	}
	setMethod(app, method) {
		this.check.setAttribute("onchange", app + "." + method);
	}
}
//Radio buttons
class Radio {
	constructor(ct, name, title) {
		this.ct = ct;
		this.name = name;
		this.title = title;
	}
	setButtons(values, labels, selected) {
		this.button = []; this.label = [];
		for (let i = 0; i < values.length; i++) {
			this.button[i] = document.createElement("input");
			this.ct.appendChild(this.button[i]);
			this.button[i].type = "radio";
			this.button[i].name = this.name;
			this.button[i].value = values[i];
			this.button[i].id = values[i];
			this.button[i].title = this.title;
			this.label[i] = document.createElement("label");
			this.ct.appendChild(this.label[i]);
			this.label[i].for = values[i];
			this.label[i].innerHTML = labels[i];
			this.label[i].title = this.title;
			if (i == selected) this.button[i].checked = true;
		}
	}
	setMethod(i, app, method) {
		this.button[i].setAttribute("onclick", app + "." + method);
	}
}
class Message {
	constructor(ct) {
		this.message = document.createElement("p");
		ct.appendChild(this.message);
	}
	setText(text) {
		this.message.innerHTML = text;
	}
}
class Label {
	constructor(ct, title) {
		this.label = document.createElement("label");
		ct.appendChild(this.label);
		this.label.title = title;
	}
	setText(text) {
		this.label.innerHTML = text;
	}
}
class Dialog {
	constructor(ct) {
		this.dialog = document.createElement("dialog");
		ct.appendChild(this.dialog);
	}
	open(text) {
		this.dialog.innerHTML = text;
		this.dialog.open = true;
	}
	close() {
		this.dialog.open = false;
	}
}
//Table in the form of a text area in a given container and with specified width, height, and title
class Table {
	constructor(ct, w, h, title) {
		this.textArea = document.createElement("textarea");
		ct.appendChild(this.textArea);
		this.textArea.style = "margin-left: 5px; width: " + w + "px; height: " + h + "px;";
		this.textArea.title = title;
		this.textArea.readOnly = true;
	}
	setHeader(heads) {
		this.header = "";
		for (let i = 0; i < heads.length; i++) this.header += heads[i] + "\t";
		this.textArea.value = this.header;
		return this.header;
	}
	addData(data) {
		let txt = "\n";
		for (let i = 0; i < data.length; i++) txt += data[i] + "\t";
		this.textArea.value += txt;
	}
	setValue(text) {
		this.textArea.value = this.header + "\n" + text;
	}
	setSize(w, h) {
		this.textArea.style = "width: " + w + "px; height: " + h + "px;";
	}
	getValue() {
		return this.textArea.value;
	}
	reset() {
		this.textArea.value = this.header;
	}
}
//Basic data table for a simulation app
class DataTable extends Table {
	constructor(ct, w, h) {
		super(ct, w, h);
		this.currentData = "";
		this.completeData = "";
		this.textArea.title = "Data table";
	}
	setCurrentData(data) {
		this.currentData = "";
		for (let i = 0; i < data.length; i++) this.currentData += data[i] + "\t";
		if (this.completeData === "") this.completeData = this.currentData;
		else this.completeData += "\n" + this.currentData;
	}
	showCurrent() {
		this.setValue(this.currentData) ;
	}
	showComplete() {
		this.setValue(this.completeData);
	}
	reset() {
		this.currentData = "";
		this.completeData = "";
		this.showComplete();
	}
}
//A basic app with a toolbar, graphs, and tables, that can be subclassed
class App {
	constructor(name) {
		this.name = name;
	}
	initialize() {
		this.div = document.getElementById(this.name);
		this.div.class = "app";
		//Toolbars
		this.toolbars = document.createElement("div");
		this.div.appendChild(this.toolbars);
		//Main toolbar
		this.toolbar = this.addToolbar();
		//Graphs (middle panel)
		this.graphs = document.createElement("div");
		this.div.appendChild(this.graphs);
		this.graphs.style = "margin-top: 10px;";
		//Tables (lower panel)
		this.tables = document.createElement("div");
		this.div.appendChild(this.tables);
		this.tables.style = "margin-top: 10px";
	}
	addToolbar() {
		const toolbar = document.createElement("div");
		toolbar.style = "margin: 5px";
		this.toolbars.appendChild(toolbar);
		return toolbar;
	}
}
//A basic simulation app that can be subclassed
class SimApp extends App {
	constructor(name) {
		super(name);
		this.runCount = 0;
		this.stopCount = 0;
		this.stopFreq = 100;
		this.header = "Run";
	}
	initialize() {
		super.initialize();
		//Simulation buttons
		this.stepButton = new StepButton(this.toolbar, this.name);
		this.runButton = new RunButton(this.toolbar, this.name);
		this.stopButton = new StopButton(this.toolbar, this.name);
		this.resetButton = new ResetButton(this.toolbar, this.name);
		//Stop select
		this.stopSelect = new Select(this.toolbar, "Stop frequency");
		this.stopSelect.setOptions([10, 100, 1000, 10000], ["Stop: 10", "Stop: 100", "Stop: 1000", "Stop: 10000"], 1);
		this.stopSelect.select.setAttribute("onchange", this.name + ".stopFreq = " + this.name + ".stopSelect.select.value");
	}
	step() {
		this.simulate();
		this.dataTable.showComplete();
	}
	run() {
		this.stepButton.setDisabled(true);
		this.stopButton.setDisabled(false);
		this.runButton.setDisabled(true);
		this.stopSelect.setDisabled(true);
		this.ID = setInterval(this.simulate.bind(this), 20);
	}
	stop() {
		this.stopCount = 0;
		clearInterval(this.ID);
		this.stepButton.setDisabled(false);
		this.runButton.setDisabled(false);
		this.resetButton.setDisabled(false);
		this.stopSelect.setDisabled(false);
		if (this.runCount > 0) this.dataTable.showComplete();
	}
	reset() {
		this.stop();
		this.runCount = 1;
		this.stopCount = 0;
		this.dataTable.reset();
	}
	simulate() {
		this.runCount++;
		this.stopCount++;
		this.dataTable.showCurrent();
		if (this.stopCount == this.stopFreq) this.stop();
	}
}
//Abstract rectangle
class Rectangle {
	constructor(x, y, w, h) {
		this.x = x;
		this.y = y;
		this.w = w;
		this.h = h;
		this.x2 = this.x + this.w;
		this.y2 = this.y + this.w;
	}
	contains(a, b) {
		if (this.x <= a && a <= this.x + this.w && this.y <= b && b <= this.y + this.h) return true;
		else return false;
	}
	nonEmpty() {
		if (this.w >= 0 && this.h >= 0) return true;
		else return false;
	}
	area() {
		if (this.nonEmpty()) return this.w * this.h;
		else return 0;
	}
	circumference() {
		return 2 * this.w + 2 * this.h;
	}
	//Determines if a point (a, b) is within 5 pixels of the lower right corner
	seCorner(a, b) {
		let x1 = this.x + this.w, y1 = this.y + this.h;
		if (x1 - 5 <= a && a <= x1 + 5 && y1 - 5 <= b && b <= y1 + 5) return true;
		else return false;
	}
}
function intersect(R, S) {
	let x1, y1, x2, y2;
	if (!(R.x > S.x + S.w || S.x > R.x + R.w || R.y > S.y + S.h || S.y > R.y + R.h)) {
		x1 = Math.max(R.x, S.x); 
		y1 = Math.max(R.y, S.y);
		x2 = Math.min(R.x + R.w, S.x + S.w);
		y2 = Math.min(R.y + R.h, S.y + S.h);
		return new Rectangle(x1, y1, x2 - x1, y2 - y1);
	}
	else return new Rectangle(0, 0, 0, 0);
}
//A basic graphical object that can be subclassed
class Canvas {
	constructor(ct, w, h, name) {
		this.svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
		ct.appendChild(this.svg);
		this.width = w;
		this.height = h;
		this.svg.setAttribute("width", this.width);
		this.svg.setAttribute("height", this.height);
		//Title
		this.title = document.createElementNS("http://www.w3.org/2000/svg", "title");
		this.svg.appendChild(this.title);
		this.title.innerHTML = name;
		//Background rectangle
		this.background = document.createElementNS("http://www.w3.org/2000/svg", "rect");
		this.svg.appendChild(this.background);
		this.background.setAttribute("x", 0);
		this.background.setAttribute("y", 0);
		this.background.setAttribute("width", this.width);
		this.background.setAttribute("height", this.height);
		this.background.setAttribute("stroke", "none");
		this.background.setAttribute("fill", "none");
		//Bounds on x and y coordinates
		this.xMin = 0;
		this.xMax = 1;
		this.yMin = 0;
		this.yMax = 1;
		//Margins
		this.lm = 20;
		this.rm = 20;
		this.bm = 20;
		this.tm = 20;
	}
	setTitle(txt) {
		this.title.innerHTML = txt;
	}
	setBounds(x0, x1, y0, y1) {
		this.xMin = x0;
		this.xMax = x1;
		this.yMin = y0;
		this.yMax = y1;
	}
	setMargins(lm, rm, bm, tm) {
		this.lm = lm;
		this.rm = rm;
		this.bm = bm;
		this.tm = tm;
	}
	//Functions to covert to and from (x, y) coordinate units to svg units.
	xCanvas(x) {
		return this.lm + Math.round(((x - this.xMin) / (this.xMax - this.xMin)) * (this.width - this.lm - this.rm));
	}	
	yCanvas(y) {
		return this.height - this.bm - Math.round(((y - this.yMin) / (this.yMax - this.yMin)) * (this.height - this.bm - this.tm));
	}	
	xScale(x) {
		return this.xMin + ((x - this.lm) / (this.width - this.lm - this.rm)) * (this.xMax - this.xMin);
	}	
	yScale(y) {
		return this.yMin + ((this.height - y - this.bm) / (this.height  - this.bm - this.tm)) * (this.yMax - this.yMin);
	}
	//Reset the graph by removing all but the first n children
	reset(n) {
		while(this.svg.children.length > n) this.svg.removeChild(this.svg.lastChild);
	}
	//Get mouse coordinates corresponding to an event
	getMouseCoordinates(evt) {
		const CTM = this.svg.getScreenCTM();
		return {
		  x: (evt.clientX - CTM.e) / CTM.a,
		  y: (evt.clientY - CTM.f) / CTM.d
		}
	}
	//Background color
	setBackground(color) {
		this.background.setAttribute("fill", color);
	}
	//Rectangle
	makeRect(x0, y0, x1, y1, stroke, fill) {
		let rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
		this.svg.appendChild(rect);
		if (typeof x0 == "number" && typeof x1 == "number" && typeof y0 == "number" && typeof y1 == "number") {
			this.setRect(rect, x0, y0, x1, y1, stroke, fill);
		}
		return rect;
	}
	setRect(rect, x0, y0, x1, y1, stroke, fill) {
		let a = this.xCanvas(x0), b = this.xCanvas(x1);
		let u = Math.min(this.yCanvas(y0), this.yCanvas(y1)), v = Math.max(this.yCanvas(y0), this.yCanvas(y1));
        rect.setAttribute("x", a);
        rect.setAttribute("y", u);
        rect.setAttribute("width", b - a);
        rect.setAttribute("height", v - u);
        rect.setAttribute("stroke", stroke);
        rect.setAttribute("fill", fill);
        return rect;
	}
	clearRect(rect) {
		rect.setAttribute("stroke", "none")
		rect.setAttribute("fill", "none");
	}
	setColors(obj, stroke, fill) {
		obj.setAttribute("stroke", stroke);
		obj.setAttribute("fill", fill);
	}
	//Circle
	makeCircle(x, y, r, stroke, fill) {
		let circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
		this.svg.appendChild(circle);
		if (typeof x == "number" && typeof y == "number" && typeof r == "number") {
			this.setCircle(circle, x, y, r, stroke, fill);
		}
		return circle;
	}
	setCircle(circle, x, y, r, stroke, fill) {
		let cx = this.xCanvas(x), cy = this.yCanvas(y), cr = this.xCanvas(x + r) - cx;
		circle.setAttribute("cx", cx);
		circle.setAttribute("cy", cy);
		circle.setAttribute("r", cr);
		circle.setAttribute("stroke", stroke);
		circle.setAttribute("fill", fill);
	}
	clearCircle(circle) {
		circle.setAttribute("stroke", "none");
		circle.setAttribute("fill", "none");
	}
	//Dot
	makeDot(x, y, r, fill) {
		let dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
		this.svg.appendChild(dot);
		if (typeof x == "number" && typeof y == "number" && typeof r == "number") {
			this.setDot(dot, x, y, r, fill);
		}
		return dot;
	}
	setDot(dot, x, y, r, fill) {
		let cx = this.xCanvas(x), cy = this.yCanvas(y);
		dot.setAttribute("cx", cx);
		dot.setAttribute("cy", cy);
		dot.setAttribute("r", r);
		dot.setAttribute("stroke", "none");
		dot.setAttribute("fill", fill);
	}
	clearDot(dot) {
		dot.setAttribute("fill", "none");
	}
	//Line
	makeLine(x1, y1, x2, y2, stroke) {
		let line = document.createElementNS("http://www.w3.org/2000/svg", "line");
		this.svg.appendChild(line);
		if (typeof x1 == "number" && typeof y1 == "number" && typeof x2 == "number" && typeof y2 == "number") {
			this.setLine(line, x1, y1, x2, y2, stroke);
		}
		return line;
	}
	setLine(line, x1, y1, x2, y2, stroke) {
		let a1 = this.xCanvas(x1), b1 = this.yCanvas(y1), a2 = this.xCanvas(x2), b2 = this.yCanvas(y2);
		line.setAttribute("x1", a1);
		line.setAttribute("y1", b1);
		line.setAttribute("x2", a2);
		line.setAttribute("y2", b2);
		line.setAttribute("stroke", stroke);
	}
	clearLine(line) {
		line.setAttribute("stroke", "none");
	}
	//Paths
	makePath() {
		let path = document.createElementNS("http://www.w3.org/2000/svg", "path")
		this.svg.appendChild(path);
		path.setAttribute("d", "");
		return path;
	}
	addDotMarker(path, fill) {
		this.svg.appendChild(dotMarker);
		path.setAttribute("marker-start", "url(#dot)");
		path.setAttribute("marker-mid", "url(#dot)");
		path.setAttribute("marker-end", "url(#dot)");
		dot.setAttribute("cx", 5);
		dot.setAttribute("cy", 5);
		dot.setAttribute("r", 3);
		dot.setAttribute("fill", fill);
	}
	moveTo(d, x, y) {
		d += "M " + this.xCanvas(x) + " " + this.yCanvas(y);
		return d;
	}
	lineTo(d, x, y) {
		d += "L" + this.xCanvas(x) + " " + this.yCanvas(y);
		return d;
	}
	draw(path, d, stroke, fill) {
		path.setAttribute("d", d);
		path.setAttribute("stroke", stroke);
		path.setAttribute("fill", fill);
	}
	//Axis starting at (x0, y0) with step size s of a given type (horizontal or vertical) 
	makeAxis(x0, y0, s, type) {
		let baseline = this.makePath();
		this.svg.appendChild(tickMarker);
		this.svg.appendChild(arrowMarker);
		baseline.setAttribute("marker-mid", "url(#tick)");
		baseline.setAttribute("marker-end", "url(#arrow)");
		this.setAxis(baseline, x0, y0, s, type);
		return baseline;
	}
	setAxis(baseline, x0, y0, s, type) {
		let d = "";
		d = this.moveTo(d, x0, y0);
		if (type == HOR) {
			for (let x = x0; x <= this.xScale(this.width); x = x + s) d = this.lineTo(d, x, y0);
			this.draw(baseline, d, "black", "none");
		}
		else if (type == VERT) {
			for (let y = y0; y <= this.yScale(0); y = y + s) d = this.lineTo(d, x0, y);
			this.draw(baseline, d, "black", "none");
		}
	}
	//Text label with content txt at position (x, y), of a given type (horzontal, vertical, or neither)
	makeText(txt, x, y, type, size, style) {
		let text = document.createElementNS("http://www.w3.org/2000/svg", "text");
		this.svg.appendChild(text);
		if (typeof size == "undefined") size = 10;
		if (typeof style == "undefined") style = "normal";
		text.setAttribute("font-family", "times");
		text.setAttribute("text-anchor", "middle");
		text.setAttribute("fill", "black");
		text.setAttribute("font-size", size);
		text.setAttribute("font-style", style);
		switch(type) {
			case BELOW:
				text.setAttribute("x", this.xCanvas(x));
				text.setAttribute("y", this.yCanvas(y) + 10);
				break;
			case ABOVE:
				text.setAttribute("x", this.xCanvas(x));
				text.setAttribute("y", this.yCanvas(y) - 10);
				break;
			case LEFT:
				text.setAttribute("x", this.xCanvas(x) - txt.length - 10);
				text.setAttribute("y", this.yCanvas(y));
				break;
			default:
				text.setAttribute("x", this.xCanvas(x));
				text.setAttribute("y", this.yCanvas(y));
		}
		text.textContent = txt;
		return text;
	}
	//Horizontal rectangle at the bottom of the graph
	makeBar(x1, x2, stroke, fill) {
		let bar = document.createElementNS("http://www.w3.org/2000/svg", "rect");
		this.svg.appendChild(bar);
		if (typeof x1 == "number" && typeof x2 == "number") this.setBar(bar, x1, x2, stroke, fill)
		return bar;
	}
	setBar(bar, x1, x2, stroke, fill) {
		let y = this.height;
		bar.setAttribute("x", this.xCanvas(x1));
		bar.setAttribute("y", y - 17);
		bar.setAttribute("width", this.xCanvas(x2) - this.xCanvas(x1));
		bar.setAttribute("height", 10);
		bar.setAttribute("stroke", stroke);
		bar.setAttribute("fill", fill);
	}
	clearBar(bar){
		bar.setAttribute("stroke", "none");
		bar.setAttribute("fill", "none");
	}
	//Vertical tick mark at the bottom of the graph
	makeMark(x, stroke) {
		let mark = document.createElementNS("http://www.w3.org/2000/svg", "line");
		this.svg.appendChild(mark);
		if (typeof x == "number") this.setMark(mark, x, stroke);
		return mark;
	}
	setMark(mark, x, stroke) {
		let y = this.height;
		mark.setAttribute("x1", this.xCanvas(x));
		mark.setAttribute("y1", y);
		mark.setAttribute("x2", this.xCanvas(x));
		mark.setAttribute("y2", y - 25);
		mark.setAttribute("stroke", stroke);
	}
	clearTick(tick) {
		tick.setAttribute("stroke", "none");
	}
}
//Distribution graph with specified container, width, height, distribution, label
class DistGraph extends Canvas {
	constructor(ct, w, h) {
		super(ct, w, h, "");
		this.setMargins(30, 20, 30, 20);
		this.distC = "blue";
		this.dataC = "rgba(255, 0, 0, 0.7)";
		this.showMoments = true;
		this.yf = 3;
		this.mf = 3;
	}
	//Setup the distribution
	setDist(dist, rv) { 
		//Initialize
		this.reset(1);
		this.dist = dist;
		this.setTitle(rv + " distribution graph");
		this.data = dist.data;
		let a = dist.min, b = dist.max, s = dist.step, m = dist.maxDensity();
		this.setBounds(a - s / 2, b + s / 2, 0, m);
		this.xf = Math.max(Math.ceil(Math.log(1 / s) / Math.log(10)), 0);
		//x-axis
		this.makeAxis(a - s / 2, 0, s, HOR);
		this.makeText(a.toFixed(this.xf), a, 0, BELOW);
		this.makeText(b.toFixed(this.xf), b, 0, BELOW);
		//y-axis
		this.makeAxis(a - s / 2, 0, m / 10, VERT);
		this.makeText("0", a - s / 2, 0, LEFT);
		this.makeText(m.toFixed(this.yf), a - s / 2, m, LEFT);
		//Distribution PDF and optionally the mean-sd bar
		if (dist.type == DISC) {
			for (let x = a; x <= b; x += s) {
				this.makeRect(x - s / 2, 0, x + s / 2, dist.density(x), this.distC, "none");
			}
		}
		else {
			let curve = this.makePath(), d = "";
			d = this.moveTo(d, a, dist.density(a));
			for (let x = a; x <= b; x += s) d = this.lineTo(d, x + s, dist.density(x + s));
			this.draw(curve, d, this.distC, "none");
		}
		if (this.showMoments) {
			let mu = dist.mean(), sd = dist.stdDev();
			let distMark = this.makeMark();
			let distBar = this.makeBar();
			if (-Infinity < mu && mu < Infinity) {
				this.setMark(distMark, mu, this.distC);
				if (sd < Infinity) this.setBar(distBar, mu - sd, mu + sd, this.distC, "none");
			}
		}
		//Data objects
		let k = dist.intervals();
		this.dataPDF = [];
		for (let i = 0; i < k; i++) this.dataPDF[i] = this.makeRect();
		this.dataBar = this.makeBar();
		this.dataMark = this.makeMark();
		this.curve1 = this.makePath();
		this.curve2 = this.makePath();
	}
	//Draw data PDF and optionally mean-standard deviation bar
 	update() {
		let dist = this.dist, type = dist.type;
		let data = this.data, n = data.points, k = data.intervals, s = data.step, x = 0, y = 0;
		for (let i = 0; i < k; i++) {
			x = dist.min + i * s;
			if (type == DISC) y = data.relFreq(x); else y = data.density(x);
			if (isNaN(y)) y = 0;
			if (n > 0) this.setRect(this.dataPDF[i], x - s / 2, 0, x + s / 2, y, "none", this.dataC);
			else this.clearRect(this.dataPDF[i]);
		}
		if (this.showMoments) {
			let m = data.mean(), sd = data.stdDev(), h = this.height;
			if (n > 0) this.setMark(this.dataMark, m, this.dataC);
			if (n > 1) this.setBar(this.dataBar, m - sd, m + sd, "none", this.dataC);
			if (n == 0) {
				this.clearLine(this.dataMark);
				this.clearRect(this.dataBar);
			}
		}
	}
	//Cumulative probabilities
	showLeft(y) {
		this.showInterval(this.dist.min, y);
	}
	showRight(y) {
		this.showInterval(y, this.dist.max);
	}
	showTails(y, z) {
		let dist = this.dist, a = dist.min, b = dist.max, s = dist.step, x = a;
		if (dist.type == DISC) {
			let n = dist.intervals(), j = dist.index(y), k = dist.index(z);
			for (let i = 0; i < n; i++) {
				x = a + i * s;
				if (i <= j || i >= k) this.setRect(this.dataPDF[i], x - s / 2, 0, x + s / 2, dist.density(x), this.dataC, this.dataC);
				else this.clearRect(this.dataPDF[i]);
			}
		}
		else {
			let d1 = "", d2 = "";
			d1 = this.moveTo(d1, a, dist.density(a));
			for (x = a; x < y + s / 2; x += s) d1 = this.lineTo(d1, x + s, dist.density(x + s));
			d1 = this.lineTo(d1, x, 0);
			d1 = this.lineTo(d1, a, 0);
			this.draw(this.curve1, d1, this.dataC, this.dataC);
			d2 = this.moveTo(d2, z, dist.density(z));
			for (x = z; x < b + s / 2; x += s) d2 = this.lineTo(d2, x + s, dist.density(x + s));
			d2 = this.lineTo(d2, x, 0);
			d2 = this.lineTo(d2, z, 0);
			this.draw(this.curve2, d2, this.dataC, this.dataC);
		}
	}
	showInterval(y, z) {
		let dist = this.dist, a = dist.min, b = dist.max, s = dist.step, x = a;
		if (dist.type == DISC) {
			let n = dist.intervals(), j = dist.index(y), k = dist.index(z);
			for (let i = 0; i < n; i++) {
				x = a + i * s;
				if (i >= j && i <= k) this.setRect(this.dataPDF[i], x - s / 2, 0, x + s / 2, dist.density(x), this.dataC, this.dataC);
				else this.clearRect(this.dataPDF[i]);
			}
		}
		else {
			let d = "";
			d = this.moveTo(d, y, dist.density(y));
			for (x = y; x < z + s / 2; x += s) d = this.lineTo(d, x + s, dist.density(x + s));
			d = this.lineTo(d, x, 0);
			d = this.lineTo(d, y, 0);
			this.draw(this.curve1, d, this.dataC, this.dataC);
		}
	}
	showQuantile(q) {
		let dist = this.dist;
		this.showLeft(dist.quantile(q));
	}
}
//Data graph with specified container, width, height, data, label
class RVDataGraph extends Canvas {
	constructor(ct, w, h) {
		super(ct, w, h, "Distribution graph");
		this.setMargins(30, 20, 30, 20);
		this.color = "red";
		this.showMoments = true;
		this.yf = 3;
		this.mf = 3;
	}
	//Initialize 
	setData(data, rv, type) { 
		//Initialize
		this.data = data;
		this.type = type;
		this.setTitle(rv + " distribution graph");
		this.update();
	}
	//Draw data PDF and optionally mean-sd bar
 	update() {
		let data = this.data, type = this.type, a = data.lower, b = data.upper, s = data.step, n = data.points, m = 1;
		if (n == 0) m = 1;
		else if (type == DISC) m = data.maxRelFreq(); 
		else m = data.maxDensity();
		this.setBounds(a - s / 2, b + s / 2, 0, m);
		this.xf = Math.max(Math.ceil(Math.log(1 / s) / Math.log(10)), 0);
		this.reset(1);
		//Draw axes
		this.makeAxis(a - s / 2, 0, s, HOR);
		this.makeText(a.toFixed(this.xf), a, 0, BELOW);    
		this.makeText(b.toFixed(this.xf), b, 0, BELOW);
		this.makeAxis(a - s / 2, 0, m / 10, VERT);
		this.makeText("0", a - s / 2, 0, LEFT);
		this.makeText(m.toFixed(this.yf), a - s / 2, m, LEFT);
		let y = 0;
		for (let x = a; x <= b; x += s) {
			if (n == 0) y = 0;
			else if (type == DISC) y = data.relFreq(x); 
			else y = data.density(x);
			if (isNaN(y)) y = 0;
			this.makeRect(x - s / 2, 0, x + s / 2, y, "gray", this.color);
		}
		if (this.showMoments) {
			let mu = data.mean(), sd = data.stdDev(), bar = this.makeBar(), mark = this.makeMark();
			if (-Infinity < mu && mu < Infinity) {
				this.setMark(mark, mu, this.color);
				if (sd < Infinity) this.setBar(bar, mu - sd, mu + sd, "gray", this.color);
			}
		}
	}
}
class CDFGraph extends Canvas {
	constructor (ct, w, h) {
		super(ct, w, h);
		this.distC = "blue";
		this.dataC = "rgba(255, 0, 0, 0.7)";
		this.setMargins(30, 20, 20, 20);
	}
	setDist(dist, rv) {
		super.reset(1);
		this.dist = dist;
		let a = dist.min, b = dist.max, s = dist.step;
		this.setTitle("CDF of " + rv);
		this.setBounds(a - s / 2, b + s / 2, 0, 1);
		this.xf = Math.max(Math.round(Math.log(1 / s) / Math.log(10)), 0);
		this.yf = 3;
		//Draw axes
		this.makeAxis(a - s / 2, 0, s, HOR);
		this.makeText(a.toFixed(this.xf), a, 0, BELOW, 10, "normal");
		this.makeText(b.toFixed(this.xf), b, 0, BELOW, 10, "normal");
		this.makeAxis(a - s / 2, 0, 1 / 10, VERT);
		this.makeText("0", a - s / 2, 0, LEFT, 10, "normal");
		this.makeText("1", a - s / 2, 1, LEFT, 10, "normal");
		this.vLine = this.makeLine();
		this.hLine = this.makeLine();
		//Draw CDF graph
		let y = 0;
		if (dist.type == DISC) {
			for (let x = a; x < b + s / 2; x += s) {
				y = dist.cdf(x);
				this.makeRect(x - s / 2, 0, x + s / 2, y, this.distC, "none");
			}
		}
		else {
			y = dist.cdf(a); 
			let cdfGraph = this.makePath(), d = "";
			d = this.moveTo(d, a, y);
			for (let x = a; x < b; x += s) {
				y = dist.cdf(x + s);
				d = this.lineTo(d, x + s, y);
			}
			this.draw(cdfGraph, d, this.distC, "none");
		}
	}
	showLeft(x) {
		let dist = this.dist, q = dist.cdf(x), a = dist.min, b = dist.max, s = dist.step;
		this.setLine(this.vLine, x, 0, x, q, this.dataC);
		this.setLine(this.hLine, a - s / 2, q, x, q, this.dataC);
	}
	showQuantile(q) {
		let x = this.dist.quantile(q);
		this.showLeft(x);
	}
	reset() {
		this.clearLine(this.vLine);
		this.clearLine(this.hLine);
	}
}
//Timeline 
class Timeline extends Canvas {
	constructor(ct, w, name) {
		super(ct, w, 50, name);
		this.time;
		this.r = 4;
		super.setMargins(10, 10,  10, 10);
	}
	setParameters(t0, t1, s) {
		this.setBounds(t0 - s / 2, t1 + s / 2, -1, 1);
		let tf = Math.max(Math.round(Math.log(1 / s) / Math.log(10)), 0);
		super.reset(1);
		this.makeAxis(t0 - s / 2, 0, s, HOR);
		this.makeText(t0.toFixed(tf), t0, 0, BELOW);
		this.makeText(t1.toFixed(tf), t1, 0, BELOW,);
	}
	addPoint(t, c) {
		return this.makeDot(t, 0, this.r, c);
	}
	changePoint = function(p, t, c) {
		return this.setDot(p, t, 0, this.r, c);
	}
	reset() {
		super.reset(6);
	}
}
//Table for recording a distribution in a simulation app
class DistTable extends Table {
	constructor(ct, w, h) {
		super(ct, w, h);
		this.yf = 3;
		this.mf = 4;
		this.showMoments = true;
	}
	setDist(dist, rv) {
		this.dist = dist;
		this.rv = rv;
		this.header = rv + "\tDist" + "\tData";
		this.textArea.title = rv + " distribution table";
		this.xf = Math.max(Math.ceil(Math.log(1 / dist.step) / Math.log(10)), 0);
		this.update();
	}
	update() {
		let n = this.dist.data.points, y;
		let txt = "";
		for (let x = this.dist.min; x <= this.dist.max; x = x + this.dist.step) {
			txt += x.toFixed(this.xf) + "\t" + this.dist.density(x).toFixed(this.yf);
			if (n > 0) {
				if (this.dist.type == DISC) y = this.dist.data.relFreq(x); else y = this.dist.data.density(x);
				if (isNaN(y)) y = 0;
				txt += "\t" + y.toFixed(this.yf);
			}
			txt += "\n";
		}
		if (this.showMoments) {
			txt += "\nMean" + "\t" + this.dist.mean().toFixed(this.mf);
			if (n > 0) txt += "\t" + this.dist.data.mean().toFixed(this.mf);
			txt += "\nSD" + "\t" + this.dist.stdDev().toFixed(this.mf);
			if (n > 1) txt += "\t" + this.dist.data.stdDev().toFixed(this.mf);
		}
		this.setValue(txt);
	}
}
//Table for recording data in a simulation app
class RVDataTable extends Table {
	constructor(ct, w, h) {
		super(ct, w, h);
		this.yf = 3;
		this.mf = 4;
		this.showMoments = true;
	}
	setData(data, rv, type) {
		this.data = data;
		this.rv = rv;
		this.type = type;
		this.header = this.rv + "\tData";
		this.textArea.title = this.rv + " distribution table";
		this.xf = Math.max(Math.ceil(Math.log(1 / this.data.step) / Math.log(10)), 0);
		this.update();
	}
	update() {
		let n = this.data.points, y;
		let txt = "";
		for (let x = this.data.lower; x <= this.data.upper; x += this.data.step) {
			txt += x.toFixed(this.xf);
			if (n > 0) {
				if (this.type == DISC) y = this.data.relFreq(x); else y = this.data.density(x);
				txt += "\t" + y.toFixed(this.yf);
			}
			txt += "\n";
		}
		if (this.showMoments) {
			if (n > 0) txt += "\nMean\t" + this.data.mean().toFixed(this.mf);
			if (n > 1) txt += "\nSD\t" + this.data.stdDev().toFixed(this.mf);
		}
		this.setValue(txt);
	}
}
//Randomizing gadgets
//A six-sided die with container element ct
class Die {
    constructor(ct) {
        //Properties
        this.svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        ct.appendChild(this.svg);
        this.svg.setAttribute("width","36");
        this.svg.setAttribute("height","36");
        this.svg.style.margin = "2px";
        this.value = -1;
        this.backColor = "red";
        this.spotColor = "white";
        this.die = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        this.svg.appendChild(this.die);
        this.die.setAttribute("x", "0");
        this.die.setAttribute("y", "0");
        this.die.setAttribute("width", "100%");
        this.die.setAttribute("height", "100%");
        this.die.setAttribute("rx", "5");
        this.die.setAttribute("ry", "5");
		this.die.setAttribute("fill", "gray");
        this.spot = [];
        for (let i = 0; i < 3; i++) {
            this.spot[i] = [];
            for (let j = 0; j < 3; j++) {
                let x = 8 + 10 * i;
                let y = 8 + 10 * j;
                this.spot[i][j] = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                this.svg.appendChild(this.spot[i][j]);
                this.spot[i][j].setAttribute("cx", x);
                this.spot[i][j].setAttribute("cy", y);
                this.spot[i][j].setAttribute("r", "4");
                this.spot[i][j].setAttribute("fill", "none");
                this.spot[i][j].setAttribute("stroke", "none");
            }
        }
    }
	setValue(v) {
		this.value = v;
		this.svg.style.display = "inline";
		if (v == 0) this.die.setAttribute("fill", "gray");
		else if (v > 0) this.die.setAttribute("fill", this.backColor);
		else this.svg.style.display = "none";
		switch(v) {
		case 0:
			this.spot[1][1].setAttribute("fill", "none");
			this.spot[0][0].setAttribute("fill", "none");
			this.spot[0][1].setAttribute("fill", "none");
			this.spot[0][2].setAttribute("fill", "none");
			this.spot[2][0].setAttribute("fill", "none");
			this.spot[2][1].setAttribute("fill", "none");
			this.spot[2][2].setAttribute("fill", "none");
			break;
		case 1:
			this.spot[1][1].setAttribute("fill", this.spotColor);
			this.spot[0][0].setAttribute("fill", "none");
			this.spot[0][1].setAttribute("fill", "none");
			this.spot[0][2].setAttribute("fill", "none");
			this.spot[2][0].setAttribute("fill", "none");
			this.spot[2][1].setAttribute("fill", "none");
			this.spot[2][2].setAttribute("fill", "none");
			break;
		case 2:
			this.spot[0][0].setAttribute("fill", this.spotColor);
			this.spot[2][2].setAttribute('fill', this.spotColor);
			this.spot[0][1].setAttribute("fill", "none");
			this.spot[0][2].setAttribute("fill", "none");
			this.spot[2][0].setAttribute("fill", "none");
			this.spot[2][1].setAttribute("fill", "none");
			this.spot[1][1].setAttribute("fill", "none");
			break;
		case 3:
			this.spot[0][0].setAttribute("fill", this.spotColor);
			this.spot[1][1].setAttribute("fill", this.spotColor);
			this.spot[2][2].setAttribute('fill', this.spotColor);
			this.spot[0][1].setAttribute("fill", "none");
			this.spot[0][2].setAttribute("fill", "none");
			this.spot[2][0].setAttribute("fill", "none");
			this.spot[2][1].setAttribute("fill", "none");
			break;
		case 4:
			this.spot[0][0].setAttribute("fill", this.spotColor);
			this.spot[0][2].setAttribute("fill", this.spotColor);
			this.spot[2][0].setAttribute("fill", this.spotColor);
			this.spot[2][2].setAttribute('fill', this.spotColor);
			this.spot[0][1].setAttribute("fill", "none");
			this.spot[1][1].setAttribute("fill", "none");
			this.spot[2][1].setAttribute("fill", "none");
			break;
		case 5:
			this.spot[0][0].setAttribute("fill", this.spotColor);
			this.spot[0][2].setAttribute("fill", this.spotColor);
			this.spot[2][0].setAttribute("fill", this.spotColor);
			this.spot[2][2].setAttribute("fill", this.spotColor);
			this.spot[1][1].setAttribute("fill", this.spotColor);
			this.spot[0][1].setAttribute("fill", "none");
			this.spot[2][1].setAttribute("fill", "none");
			break;
		case 6:
			this.spot[0][0].setAttribute("fill", this.spotColor);
			this.spot[0][1].setAttribute("fill", this.spotColor);
			this.spot[0][2].setAttribute("fill", this.spotColor);
			this.spot[2][0].setAttribute("fill", this.spotColor);
			this.spot[2][1].setAttribute("fill", this.spotColor);
			this.spot[2][2].setAttribute("fill", this.spotColor);
			this.spot[1][1].setAttribute("fill", "none");
			break;
		}
	}
	roll(prob) {
		let p = Math.random(), sum = 0, x = 0;
		for (let i = 0; i < 6; i++) {
			if ((sum < p) && (p <= sum + prob[i])) x = i + 1;
			sum += prob[i];
		}
		this.setValue(x);
		return x;
	}
}
//A container for dice
class DiceBoard {
	constructor(ct) {
		this.panel = document.createElement("div");
		ct.appendChild(this.panel);
	}
	setDice(n) {
		this.n = n;
		this.svg = []; this.dice = [];
		while(this.panel.children.length > 0) this.panel.removeChild(this.panel.lastChild);
		for (let i = 0; i < this.n; i++) {
			this.dice[i] = new Die(this.panel);
		}
	}
	setValue(i, v) {
		this.dice[i].setValue(v);

	}
	reset() {
		for (let i = 0; i < this.n; i++) this.setValue(i, 0);
	}
	rollDice(p) {
		let y = 0, n = this.n;
		for (let i = 0; i < n; i++) y += this.dice[i].roll(p);
		return y;
	}
	rollDie(i, p) {
		return this.dice[i].roll(p);
	}
	getValue(i) {
		return this.dice[i].value;
	}
	getValues() {
		let v = [], n = this.n;
		for (let i = 0; i < n; i++) v[i] = this.dice[i].value;
		return v;
	}
	getHeader(x) {
		let h = [], n = this.n;
		for (let i = 0; i < n; i++) h[i] = x + (i + 1);
		return h;
	}
}
//A ball with a color and a label
class Ball {
    constructor(ct) { 
        //Container
        this.svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        ct.appendChild(this.svg); 
        this.svg.setAttribute("width","30");
        this.svg.setAttribute("height","30");
        this.svg.style.margin = "2px";
		this.title = document.createElementNS("http://www.w3.org/2000/svg", "title");
		this.svg.appendChild(this.title);
        //Ball
        this.ball = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        this.svg.appendChild(this.ball);
        this.ball.setAttribute("cx", "15");
        this.ball.setAttribute("cy", "15");
        this.ball.setAttribute("r", "14.5");
		this.ball.setAttribute("fill", "gray");
        this.ball.setAttribute("stroke", "black");
        //Label
        this.label = document.createElementNS("http://www.w3.org/2000/svg", "text");
        this.svg.appendChild(this.label);
        this.label.setAttribute("font-size", "16");
        this.label.setAttribute("font-family", "times");
        this.label.setAttribute("text-anchor", "middle");
        this.label.setAttribute("x", "15");
        this.label.setAttribute("y", "20");
        this.label.setAttribute("fill", "white");
    }
	setTitle(text) {
		this.title.innerHTML = text;
	}
	setBall(label, fill) {
		this.ball.setAttribute("fill", fill);
		this.label.textContent = label;
	}
	setSize(s) {
        this.svg.setAttribute("width", s);
        this.svg.setAttribute("height", s);
        this.ball.setAttribute("cx", s / 2);
        this.ball.setAttribute("cy", s / 2);
        this.ball.setAttribute("r", s / 2 - 1);
        this.label.setAttribute("font-size", s / 2);
        this.label.setAttribute("x", s / 2);
        this.label.setAttribute("y", 5 * s / 8);
	}
	getValue() {
		return this.label.textContent;
	}
}
//A container for balls with colors and labels
class Urn {
	constructor(ct) {
		this.panel = document.createElement("div");
		ct.appendChild(this.panel);
	}
	setBalls(n) {
		this.n = n;
		this.svg = []; this.balls = []; this.labels = [];
		while(this.panel.children.length > 0) this.panel.removeChild(this.panel.lastChild);
		for (let i = 0; i < n; i++) {
			this.balls[i] = new Ball(this.panel);
		}
	}
	reset(k) {
		let n = this.n;
		for (let i = 0; i < n; i++) {
			if (i < k) this.setBall(i, "", "gray");
			else this.setBall(i, "", "none");
		}
	}
	setBall(i, label, fill) {
		this.balls[i].setBall(label, fill);
	}
	getValue(i) {
		return this.balls[i].getValue();
	}
	getValues() {
		let v = [], n = this.n;
		for (let i = 0; i < n; i++) v[i] = this.getValue(i);
		return v;
	}
	getHeader(x) {
		let h = [], n = this.n;
		for (let i = 0; i < this.n; i++) h[i] = x + (i + 1);
		return h;
	}
	setTitle(i, text) {
		this.balls[i].setTitle(text);
	}
}
//A coin with labels H and T that can be tossed.
class Coin extends Ball {
	constructor(ct) {
		super(ct);
	}
	setValue(v) {
		if (v == 0) super.setBall("T", "green");
		else if (v == 1) super.setBall("H", "red");
		else super.setBall("", "gray");
		this.value = v;
	}
	toss(p) {
		let v = 0;
		if (Math.random() <= p) v = 1;
		this.setValue(v);
		return v;
	}
}
//A container for coins
class CoinBox {
	constructor(ct) {
		this.panel = document.createElement("div");
		ct.appendChild(this.panel);
	}
	setCoins(n) {
		this.n = n;
		this.svg = []; this.coins = [], this.labels = [];
		while(this.panel.children.length > 0) this.panel.removeChild(this.panel.lastChild);
		for (let i = 0; i < n; i++) {
			this.coins[i] = new Coin(this.panel);
		}
	}
	reset() {
		let n = this.n;
		for (let i = 0; i < n; i++) this.setValue(i, -1);
	}
	setValue(i, v) {
		this.coins[i].setValue(v);
	}
	tossCoin(i, p) {
		return this.coins[i].toss(p);
	}
	tossCoins(p) {
		let y = 0, n = this.n;
		for (let i = 0; i < n; i++) y += this.coins[i].toss(p);
		return y;
	}
	getValues() {
		let v = [], n = this.n;
		for (let i = 0; i < n; i++) v[i] = this.coins[i].value;
		return v;
	}
	getValue(i) {
		return this.coins[i].value;
	}	
	getHeader(x) {
		let h = [], n = this.n;
		for (let i = 0; i < n; i++) h[i] = x + (i + 1);
		return h;
	}
}
//Card Hand
class CardHand {
	constructor(ct) {
		this.panel = document.createElement("div");
		ct.appendChild(this.panel);
		this.suitSymbols = ["\u2663", "\u2666", "\u2665", "\u2660"];
        this.suitNames = ["C", "D", "H", "S"];
        this.denomNames = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"];
		this.deck = [];
		for (let i = 0; i < 52; i++) this.deck[i] = i + 1;
	}
	setCards(n, symbol) {
		this.n = n;
		this.headings = [];
		while(this.panel.children.length > 0) this.panel.removeChild(this.panel.lastChild);
		this.hand = []; 
		this.suit = [];
		this.suitSymbol = [];
		this.suitName = [];
		this.denomination = [];
		this.denomName = [];
		for (let i = 0; i < n; i++) {
			this.hand[i] = document.createElement("img");
			this.panel.appendChild(this.hand[i]);
			this.hand[i].setAttribute("width", 80);
			this.hand[i].setAttribute("height", 112);
			this.hand[i].style.display = "inline";
			this.hand[i].title = "Card" + (i + 1);
			this.headings[i] = symbol + (i + 1);
		}
		this.reset();
	}
	reset() {
		let n = this.n;
		for (let i = 0; i < n; i++) this.hand[i].src = "Cards/Back.svg";
	}
	setCardImage(i, src) {
		this.hand[i].src = src;
	}
	deal() {
		let n = this.n, d = sample(this.deck, n, 0), data = [];
		for (let i = 0; i < n; i++) {
			this.suit[i] = Math.ceil(d[i] / 13);
			this.suitSymbol[i] = this.suitSymbols[this.suit[i] - 1];
			this.suitName[i] = this.suitNames[this.suit[i] - 1];
			this.denomination[i] = d[i] - 13 * (this.suit[i] - 1);
            this.denomName[i] = this.denomNames[this.denomination[i] - 1];
			this.hand[i].src="Cards/" + this.denomName[i] + this.suitName[i] + ".svg";
			data[i] = this.denomName[i] + this.suitSymbol[i];
		}
		return data;
	}
}
//Galton Board
class GaltonBoard extends Canvas {
	constructor(ct, w, h) {
		super(ct, w, h, "Galton board");
		this.r = 4;
		this.pegColor = "blue";
		this.ballColor = "rgba(255, 0, 0, 0.7)";
		this.setMargins(20, 20, 20, 20);
	}
	setRows(n) {
		this.rows = n;
		super.reset(1);
		this.setBounds(-n, n, n, 0);
		this.pegs = [];
		for (let i = 0; i <= n; i++) {
			this.pegs[i] = [];
			for (let j = 0; j <= i; j++) {
				let x = -i + 2 * j, y = i;
				this.pegs[i][j] = this.makeDot(x, y, this.r, this.pegColor);
			}
		}
		this.s = this.yScale(this.yCanvas(0) - 2 * this.r);  //vertical offset for ball
	}
	reset() {
		let n = this.rows;
		for (let i = 0; i <= n; i++) {
			for (let j = 0; j <= i; j++) this.setColors(this.pegs[i][j], this.pegColor, this.pegColor);
		}
	}
	setPath(p) {
		this.reset();
		this.setColors(this.pegs[0][0], this.ballColor, this.ballColor);
		let j = 0;
		for (let i = 0; i < p.length; i++) {
			j += p[i];
			this.setColors(this.pegs[i + 1][j], this.ballColor, this.ballColor);
		}
	}
	getPeg(x, y) {
		let n = this.rows;
		let i = Math.round(this.yScale(y)), j = Math.round((this.xScale(x) + i) / 2);
		if (0 <= i && i <= n && 0 <= j && j <= i) return [i, j];
		else return null;
	}
}
//An image with a caption
class Figure {
	constructor(ct) {
		this.figure = document.createElement("figure");
		ct.appendChild(this.figure);
		this.image = document.createElement("img");
		this.caption = document.createElement("figcaption");
		this.figure.appendChild(this.caption);
		this.figure.appendChild(this.image);
	}
	setImage(src, w, h) {
		this.image.src = src;
		this.image.style = "width:" + w + "px; height: " + h + "px; border: black 1px solid;";
	}
	setCaption(txt) {
		this.caption.innerHTML = txt;
	}
}