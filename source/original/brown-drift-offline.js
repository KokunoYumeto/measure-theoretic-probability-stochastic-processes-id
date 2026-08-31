/*
 * Laboratorium luring gerak Brown dengan hanyutan.
 * Karya asli edisi O009/D30; CC BY 4.0.
 */
(function () {
	"use strict";

	const root = document.getElementById("brown-drift-offline-lab");
	if (!root || root.dataset.initialized === "true") return;
	root.dataset.initialized = "true";

	const svgNS = "http://www.w3.org/2000/svg";
	const fields = {
		mu: root.querySelector("#brown-drift-mu"),
		sigma: root.querySelector("#brown-drift-sigma"),
		horizon: root.querySelector("#brown-drift-horizon"),
		steps: root.querySelector("#brown-drift-steps"),
		repetitions: root.querySelector("#brown-drift-repetitions"),
		seed: root.querySelector("#brown-drift-seed")
	};
	const runButton = root.querySelector("#brown-drift-run");
	const resetButton = root.querySelector("#brown-drift-reset");
	const status = root.querySelector("#brown-drift-status");
	const chart = root.querySelector("#brown-drift-chart");
	const description = root.querySelector("#brown-drift-chart-description");
	const cells = {
		theoreticalMean: root.querySelector("#brown-drift-theoretical-mean"),
		empiricalMean: root.querySelector("#brown-drift-empirical-mean"),
		theoreticalVariance: root.querySelector("#brown-drift-theoretical-variance"),
		empiricalVariance: root.querySelector("#brown-drift-empirical-variance")
	};
	const defaults = {
		mu: "0.4",
		sigma: "1.2",
		horizon: "1",
		steps: "200",
		repetitions: "1000",
		seed: "20260825"
	};

	function seededRandom(seed) {
		let state = seed >>> 0;
		return function () {
			state += 0x6D2B79F5;
			let value = state;
			value = Math.imul(value ^ (value >>> 15), value | 1);
			value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
			return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
		};
	}

	function standardNormal(random) {
		let u = 0;
		let v = 0;
		while (u === 0) u = random();
		while (v === 0) v = random();
		return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
	}

	function readParameters() {
		const values = {
			mu: Number(fields.mu.value),
			sigma: Number(fields.sigma.value),
			horizon: Number(fields.horizon.value),
			steps: Number(fields.steps.value),
			repetitions: Number(fields.repetitions.value),
			seed: Number(fields.seed.value)
		};
		if (!Number.isFinite(values.mu) || Math.abs(values.mu) > 20) {
			throw new Error("Hanyutan harus berupa bilangan hingga antara -20 dan 20.");
		}
		if (!Number.isFinite(values.sigma) || values.sigma <= 0 || values.sigma > 20) {
			throw new Error("Skala harus lebih besar dari 0 dan paling besar 20.");
		}
		if (!Number.isFinite(values.horizon) || values.horizon <= 0 || values.horizon > 20) {
			throw new Error("Horizon waktu harus lebih besar dari 0 dan paling besar 20.");
		}
		if (!Number.isInteger(values.steps) || values.steps < 20 || values.steps > 2000) {
			throw new Error("Banyak langkah harus berupa bilangan bulat antara 20 dan 2.000.");
		}
		if (!Number.isInteger(values.repetitions) || values.repetitions < 10 || values.repetitions > 5000) {
			throw new Error("Banyak replikasi harus berupa bilangan bulat antara 10 dan 5.000.");
		}
		if (!Number.isInteger(values.seed) || values.seed < 1 || values.seed > 4294967295) {
			throw new Error("Benih harus berupa bilangan bulat antara 1 dan 4.294.967.295.");
		}
		return values;
	}

	function element(name, attributes, text) {
		const node = document.createElementNS(svgNS, name);
		for (const [key, value] of Object.entries(attributes || {})) {
			node.setAttribute(key, String(value));
		}
		if (text !== undefined) node.textContent = text;
		return node;
	}

	function normalDensity(x, mean, standardDeviation) {
		const z = (x - mean) / standardDeviation;
		return Math.exp(-0.5 * z * z) / (standardDeviation * Math.sqrt(2 * Math.PI));
	}

	function format(value) {
		return Number(value).toLocaleString("id-ID", {
			minimumFractionDigits: 4,
			maximumFractionDigits: 4
		});
	}

	function draw(parameters, path, endpoints, empiricalMean, empiricalVariance) {
		for (const node of Array.from(chart.children)) {
			if (node !== description && node.tagName.toLowerCase() !== "title") node.remove();
		}
		const pathPanel = {x: 50, y: 35, width: 285, height: 255};
		const densityPanel = {x: 415, y: 35, width: 285, height: 255};
		const theoreticalMean = parameters.mu * parameters.horizon;
		const theoreticalSD = parameters.sigma * Math.sqrt(parameters.horizon);
		const pathValues = path.map((point) => point[1]);
		let pathMin = Math.min(...pathValues, theoreticalMean - 3 * theoreticalSD, 0);
		let pathMax = Math.max(...pathValues, theoreticalMean + 3 * theoreticalSD, 0);
		if (pathMax === pathMin) pathMax = pathMin + 1;

		const xPath = (time) => pathPanel.x + (time / parameters.horizon) * pathPanel.width;
		const yPath = (value) => pathPanel.y + pathPanel.height -
			((value - pathMin) / (pathMax - pathMin)) * pathPanel.height;
		const pathPoints = path.map((point) => `${xPath(point[0]).toFixed(2)},${yPath(point[1]).toFixed(2)}`).join(" ");

		chart.append(
			element("text", {x: pathPanel.x, y: 18, class: "brown-drift-title"}, "Satu lintasan sampel"),
			element("rect", {x: pathPanel.x, y: pathPanel.y, width: pathPanel.width, height: pathPanel.height, class: "brown-drift-frame"}),
			element("line", {x1: pathPanel.x, y1: yPath(0), x2: pathPanel.x + pathPanel.width, y2: yPath(0), class: "brown-drift-axis"}),
			element("polyline", {points: pathPoints, class: "brown-drift-path"}),
			element("text", {x: pathPanel.x, y: 315}, "0"),
			element("text", {x: pathPanel.x + pathPanel.width - 8, y: 315}, String(parameters.horizon)),
			element("text", {x: pathPanel.x + pathPanel.width / 2 - 5, y: 337}, "t")
		);

		const bins = 20;
		const rangeMin = theoreticalMean - 4 * theoreticalSD;
		const rangeMax = theoreticalMean + 4 * theoreticalSD;
		const width = (rangeMax - rangeMin) / bins;
		const counts = Array(bins).fill(0);
		for (const value of endpoints) {
			const index = Math.floor((value - rangeMin) / width);
			if (index >= 0 && index < bins) counts[index] += 1;
		}
		const empiricalDensities = counts.map((count) => count / (endpoints.length * width));
		const theoreticalPeak = normalDensity(theoreticalMean, theoreticalMean, theoreticalSD);
		const densityMax = Math.max(theoreticalPeak, ...empiricalDensities) * 1.12;
		const xDensity = (value) => densityPanel.x + ((value - rangeMin) / (rangeMax - rangeMin)) * densityPanel.width;
		const yDensity = (value) => densityPanel.y + densityPanel.height - (value / densityMax) * densityPanel.height;

		chart.append(
			element("text", {x: densityPanel.x, y: 18, class: "brown-drift-title"}, "Kepadatan empiris X_T dan kurva normal"),
			element("rect", {x: densityPanel.x, y: densityPanel.y, width: densityPanel.width, height: densityPanel.height, class: "brown-drift-frame"})
		);
		for (let index = 0; index < bins; index += 1) {
			const x = densityPanel.x + index * densityPanel.width / bins;
			const y = yDensity(empiricalDensities[index]);
			chart.append(element("rect", {
				x,
				y,
				width: densityPanel.width / bins - 1,
				height: densityPanel.y + densityPanel.height - y,
				class: "brown-drift-bar"
			}));
		}
		const densityPoints = [];
		for (let index = 0; index <= 160; index += 1) {
			const xValue = rangeMin + (rangeMax - rangeMin) * index / 160;
			densityPoints.push(`${xDensity(xValue).toFixed(2)},${yDensity(normalDensity(xValue, theoreticalMean, theoreticalSD)).toFixed(2)}`);
		}
		chart.append(
			element("polyline", {points: densityPoints.join(" "), class: "brown-drift-density"}),
			element("text", {x: densityPanel.x, y: 315}, format(rangeMin)),
			element("text", {x: densityPanel.x + densityPanel.width - 42, y: 315}, format(rangeMax)),
			element("text", {x: densityPanel.x + densityPanel.width / 2 - 12, y: 337}, "X_T")
		);

		description.textContent = `Lintasan gerak Brown dari 0 sampai waktu ${parameters.horizon}; ` +
			`histogram ${parameters.repetitions} nilai akhir dibandingkan dengan kepadatan normal teoretis. ` +
			`Rataan empiris ${format(empiricalMean)} dan varians sampel ${format(empiricalVariance)}.`;
	}

	function run() {
		try {
			const parameters = readParameters();
			const random = seededRandom(parameters.seed);
			const dt = parameters.horizon / parameters.steps;
			const incrementDrift = parameters.mu * dt;
			const incrementScale = parameters.sigma * Math.sqrt(dt);
			const endpoints = [];
			let firstPath = [[0, 0]];
			for (let repetition = 0; repetition < parameters.repetitions; repetition += 1) {
				let value = 0;
				const currentPath = repetition === 0 ? [[0, 0]] : null;
				for (let step = 1; step <= parameters.steps; step += 1) {
					value += incrementDrift + incrementScale * standardNormal(random);
					if (currentPath) currentPath.push([step * dt, value]);
				}
				if (currentPath) firstPath = currentPath;
				endpoints.push(value);
			}
			const empiricalMean = endpoints.reduce((sum, value) => sum + value, 0) / endpoints.length;
			const empiricalVariance = endpoints.reduce(
				(sum, value) => sum + (value - empiricalMean) ** 2,
				0
			) / (endpoints.length - 1);
			const theoreticalMean = parameters.mu * parameters.horizon;
			const theoreticalVariance = parameters.sigma ** 2 * parameters.horizon;
			cells.theoreticalMean.textContent = format(theoreticalMean);
			cells.empiricalMean.textContent = format(empiricalMean);
			cells.theoreticalVariance.textContent = format(theoreticalVariance);
			cells.empiricalVariance.textContent = format(empiricalVariance);
			draw(parameters, firstPath, endpoints, empiricalMean, empiricalVariance);
			status.textContent = `Selesai: ${parameters.repetitions.toLocaleString("id-ID")} replikasi deterministik dengan benih ${parameters.seed}.`;
		} catch (error) {
			status.textContent = error instanceof Error ? error.message : "Parameter tidak valid.";
		}
	}

	function reset() {
		for (const [key, value] of Object.entries(defaults)) fields[key].value = value;
		run();
	}

	runButton.addEventListener("click", run);
	resetButton.addEventListener("click", reset);
	run();
}());
