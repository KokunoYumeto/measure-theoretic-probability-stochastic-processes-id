/*
 * Laboratorium luring jembatan Brown.
 * Karya asli edisi O009/D30; CC BY 4.0.
 */
(function () {
	"use strict";

	const root = document.getElementById("brown-bridge-offline-lab");
	if (!root || root.dataset.initialized === "true") return;
	root.dataset.initialized = "true";

	const svgNS = "http://www.w3.org/2000/svg";
	const fields = {
		observation: root.querySelector("#brown-bridge-observation"),
		steps: root.querySelector("#brown-bridge-steps"),
		repetitions: root.querySelector("#brown-bridge-repetitions"),
		seed: root.querySelector("#brown-bridge-seed")
	};
	const runButton = root.querySelector("#brown-bridge-run");
	const resetButton = root.querySelector("#brown-bridge-reset");
	const status = root.querySelector("#brown-bridge-status");
	const chart = root.querySelector("#brown-bridge-chart");
	const description = root.querySelector("#brown-bridge-chart-description");
	const cells = {
		theoreticalMean: root.querySelector("#brown-bridge-theoretical-mean"),
		empiricalMean: root.querySelector("#brown-bridge-empirical-mean"),
		theoreticalVariance: root.querySelector("#brown-bridge-theoretical-variance"),
		empiricalVariance: root.querySelector("#brown-bridge-empirical-variance")
	};
	const defaults = {
		observation: "0.5",
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
			observation: Number(fields.observation.value),
			steps: Number(fields.steps.value),
			repetitions: Number(fields.repetitions.value),
			seed: Number(fields.seed.value)
		};
		if (!Number.isFinite(values.observation) || values.observation <= 0 || values.observation >= 1) {
			throw new Error("Waktu pengamatan harus berada di antara 0 dan 1 secara ketat.");
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

	function normalDensity(x, standardDeviation) {
		const z = x / standardDeviation;
		return Math.exp(-0.5 * z * z) / (standardDeviation * Math.sqrt(2 * Math.PI));
	}

	function format(value) {
		return Number(value).toLocaleString("id-ID", {
			minimumFractionDigits: 4,
			maximumFractionDigits: 4
		});
	}

	function draw(parameters, path, samples, empiricalMean, empiricalVariance) {
		for (const node of Array.from(chart.children)) {
			if (node !== description && node.tagName.toLowerCase() !== "title") node.remove();
		}
		const pathPanel = {x: 50, y: 35, width: 285, height: 255};
		const densityPanel = {x: 415, y: 35, width: 285, height: 255};
		const theoreticalVariance = parameters.observation * (1 - parameters.observation);
		const theoreticalSD = Math.sqrt(theoreticalVariance);
		const pathValues = path.map((point) => point[1]);
		let pathMin = Math.min(...pathValues, -3 * theoreticalSD, 0);
		let pathMax = Math.max(...pathValues, 3 * theoreticalSD, 0);
		if (pathMax === pathMin) pathMax = pathMin + 1;

		const xPath = (time) => pathPanel.x + time * pathPanel.width;
		const yPath = (value) => pathPanel.y + pathPanel.height -
			((value - pathMin) / (pathMax - pathMin)) * pathPanel.height;
		const pathPoints = path.map((point) => `${xPath(point[0]).toFixed(2)},${yPath(point[1]).toFixed(2)}`).join(" ");

		chart.append(
			element("text", {x: pathPanel.x, y: 18, class: "brown-bridge-title"}, "Satu lintasan jembatan Brown"),
			element("rect", {x: pathPanel.x, y: pathPanel.y, width: pathPanel.width, height: pathPanel.height, class: "brown-bridge-frame"}),
			element("line", {x1: pathPanel.x, y1: yPath(0), x2: pathPanel.x + pathPanel.width, y2: yPath(0), class: "brown-bridge-axis"}),
			element("line", {x1: xPath(parameters.observation), y1: pathPanel.y, x2: xPath(parameters.observation), y2: pathPanel.y + pathPanel.height, class: "brown-bridge-observation"}),
			element("polyline", {points: pathPoints, class: "brown-bridge-path"}),
			element("text", {x: pathPanel.x, y: 315}, "0"),
			element("text", {x: pathPanel.x + pathPanel.width - 5, y: 315}, "1"),
			element("text", {x: pathPanel.x + pathPanel.width / 2 - 5, y: 337}, "t")
		);

		const bins = 20;
		const rangeMin = -4 * theoreticalSD;
		const rangeMax = 4 * theoreticalSD;
		const width = (rangeMax - rangeMin) / bins;
		const counts = Array(bins).fill(0);
		for (const value of samples) {
			const index = Math.floor((value - rangeMin) / width);
			if (index >= 0 && index < bins) counts[index] += 1;
		}
		const empiricalDensities = counts.map((count) => count / (samples.length * width));
		const theoreticalPeak = normalDensity(0, theoreticalSD);
		const densityMax = Math.max(theoreticalPeak, ...empiricalDensities) * 1.12;
		const xDensity = (value) => densityPanel.x + ((value - rangeMin) / (rangeMax - rangeMin)) * densityPanel.width;
		const yDensity = (value) => densityPanel.y + densityPanel.height - (value / densityMax) * densityPanel.height;

		chart.append(
			element("text", {x: densityPanel.x, y: 18, class: "brown-bridge-title"}, "Kepadatan empiris dan normal teoretis"),
			element("rect", {x: densityPanel.x, y: densityPanel.y, width: densityPanel.width, height: densityPanel.height, class: "brown-bridge-frame"})
		);
		for (let index = 0; index < bins; index += 1) {
			const x = densityPanel.x + index * densityPanel.width / bins;
			const y = yDensity(empiricalDensities[index]);
			chart.append(element("rect", {
				x,
				y,
				width: densityPanel.width / bins - 1,
				height: densityPanel.y + densityPanel.height - y,
				class: "brown-bridge-bar"
			}));
		}
		const densityPoints = [];
		for (let index = 0; index <= 160; index += 1) {
			const xValue = rangeMin + (rangeMax - rangeMin) * index / 160;
			densityPoints.push(`${xDensity(xValue).toFixed(2)},${yDensity(normalDensity(xValue, theoreticalSD)).toFixed(2)}`);
		}
		chart.append(
			element("polyline", {points: densityPoints.join(" "), class: "brown-bridge-density"}),
			element("text", {x: densityPanel.x, y: 315}, format(rangeMin)),
			element("text", {x: densityPanel.x + densityPanel.width - 42, y: 315}, format(rangeMax)),
			element("text", {x: densityPanel.x + densityPanel.width / 2 - 18, y: 337}, "X_t")
		);

		description.textContent = `Lintasan jembatan Brown dari 0 kembali ke 0; ` +
			`histogram ${parameters.repetitions} nilai pada t=${parameters.observation} dibandingkan dengan kepadatan normal teoretis. ` +
			`Rataan empiris ${format(empiricalMean)} dan varians sampel ${format(empiricalVariance)}.`;
	}

	function run() {
		try {
			const parameters = readParameters();
			const random = seededRandom(parameters.seed);
			const dt = 1 / parameters.steps;
			const brownian = [0];
			for (let step = 1; step <= parameters.steps; step += 1) {
				brownian.push(brownian[step - 1] + Math.sqrt(dt) * standardNormal(random));
			}
			const terminal = brownian[parameters.steps];
			const firstPath = brownian.map((value, step) => {
				const time = step * dt;
				return [time, value - time * terminal];
			});
			const samples = [];
			const t = parameters.observation;
			for (let repetition = 0; repetition < parameters.repetitions; repetition += 1) {
				const atT = Math.sqrt(t) * standardNormal(random);
				const atOne = atT + Math.sqrt(1 - t) * standardNormal(random);
				samples.push(atT - t * atOne);
			}
			const empiricalMean = samples.reduce((sum, value) => sum + value, 0) / samples.length;
			const empiricalVariance = samples.reduce(
				(sum, value) => sum + (value - empiricalMean) ** 2,
				0
			) / (samples.length - 1);
			const theoreticalVariance = t * (1 - t);
			cells.theoreticalMean.textContent = format(0);
			cells.empiricalMean.textContent = format(empiricalMean);
			cells.theoreticalVariance.textContent = format(theoreticalVariance);
			cells.empiricalVariance.textContent = format(empiricalVariance);
			draw(parameters, firstPath, samples, empiricalMean, empiricalVariance);
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
