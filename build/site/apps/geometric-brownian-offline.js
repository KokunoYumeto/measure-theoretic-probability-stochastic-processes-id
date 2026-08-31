/*
 * Laboratorium luring gerak Brown geometrik.
 * Karya asli edisi O009/D30; CC BY 4.0.
 */
(function () {
	"use strict";

	const root = document.getElementById("geometric-brownian-offline-lab");
	if (!root || root.dataset.initialized === "true") return;
	root.dataset.initialized = "true";

	const svgNS = "http://www.w3.org/2000/svg";
	const fields = {
		x0: root.querySelector("#geometric-brownian-x0"),
		mu: root.querySelector("#geometric-brownian-mu"),
		sigma: root.querySelector("#geometric-brownian-sigma"),
		horizon: root.querySelector("#geometric-brownian-horizon"),
		steps: root.querySelector("#geometric-brownian-steps"),
		repetitions: root.querySelector("#geometric-brownian-repetitions"),
		seed: root.querySelector("#geometric-brownian-seed")
	};
	const runButton = root.querySelector("#geometric-brownian-run");
	const resetButton = root.querySelector("#geometric-brownian-reset");
	const status = root.querySelector("#geometric-brownian-status");
	const chart = root.querySelector("#geometric-brownian-chart");
	const description = root.querySelector("#geometric-brownian-chart-description");
	const cells = {
		theoreticalMean: root.querySelector("#geometric-brownian-theoretical-mean"),
		empiricalMean: root.querySelector("#geometric-brownian-empirical-mean"),
		theoreticalMedian: root.querySelector("#geometric-brownian-theoretical-median"),
		empiricalMedian: root.querySelector("#geometric-brownian-empirical-median"),
		theoreticalVariance: root.querySelector("#geometric-brownian-theoretical-variance"),
		empiricalVariance: root.querySelector("#geometric-brownian-empirical-variance"),
		theoreticalProbability: root.querySelector("#geometric-brownian-theoretical-probability"),
		empiricalProbability: root.querySelector("#geometric-brownian-empirical-probability")
	};
	const defaults = {
		x0: "1",
		mu: "0.1",
		sigma: "0.4",
		horizon: "1",
		steps: "200",
		repetitions: "1000",
		seed: "20260826"
	};

	function seededRandom(seed) {
		let state = seed >>> 0;
		return function () {
			state = (state + 0x6D2B79F5) >>> 0;
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
			x0: Number(fields.x0.value),
			mu: Number(fields.mu.value),
			sigma: Number(fields.sigma.value),
			horizon: Number(fields.horizon.value),
			steps: Number(fields.steps.value),
			repetitions: Number(fields.repetitions.value),
			seed: Number(fields.seed.value)
		};
		if (!Number.isFinite(values.x0) || values.x0 < 0.0001 || values.x0 > 1000000) {
			throw new Error("Nilai awal harus berada antara 0,0001 dan 1.000.000.");
		}
		if (!Number.isFinite(values.mu) || Math.abs(values.mu) > 2) {
			throw new Error("Hanyutan harus berupa bilangan hingga antara -2 dan 2.");
		}
		if (!Number.isFinite(values.sigma) || values.sigma < 0.01 || values.sigma > 2) {
			throw new Error("Volatilitas harus berada antara 0,01 dan 2.");
		}
		if (!Number.isFinite(values.horizon) || values.horizon < 0.01 || values.horizon > 4) {
			throw new Error("Horizon waktu harus berada antara 0,01 dan 4.");
		}
		if (!Number.isInteger(values.steps) || values.steps < 20 || values.steps > 1000) {
			throw new Error("Banyak langkah harus berupa bilangan bulat antara 20 dan 1.000.");
		}
		if (!Number.isInteger(values.repetitions) || values.repetitions < 10 || values.repetitions > 2000) {
			throw new Error("Banyak replikasi harus berupa bilangan bulat antara 10 dan 2.000.");
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

	function lognormalDensity(x, location, scale) {
		if (!(x > 0)) return 0;
		const z = (Math.log(x) - location) / scale;
		return Math.exp(-0.5 * z * z) / (x * scale * Math.sqrt(2 * Math.PI));
	}

	function normalCdf(x) {
		const sign = x < 0 ? -1 : 1;
		const value = Math.abs(x) / Math.sqrt(2);
		const t = 1 / (1 + 0.3275911 * value);
		const polynomial = (((((1.061405429 * t - 1.453152027) * t) +
			1.421413741) * t - 0.284496736) * t + 0.254829592) * t;
		const erf = sign * (1 - polynomial * Math.exp(-value * value));
		return 0.5 * (1 + erf);
	}

	function format(value) {
		return Number(value).toLocaleString("id-ID", {
			minimumFractionDigits: 4,
			maximumFractionDigits: 4
		});
	}

	function shortFormat(value) {
		return Number(value).toLocaleString("id-ID", {
			maximumFractionDigits: 3
		});
	}

	function draw(parameters, path, endpoints, empiricalMean, empiricalVariance) {
		for (const node of Array.from(chart.children)) {
			if (node !== description && node.tagName.toLowerCase() !== "title") node.remove();
		}
		const pathPanel = {x: 50, y: 35, width: 285, height: 255};
		const densityPanel = {x: 415, y: 35, width: 285, height: 255};
		const location = Math.log(parameters.x0) +
			(parameters.mu - parameters.sigma ** 2 / 2) * parameters.horizon;
		const scale = parameters.sigma * Math.sqrt(parameters.horizon);
		const pathValues = path.map((point) => point[1]);
		const terminalMean = parameters.x0 * Math.exp(
			parameters.mu * parameters.horizon
		);
		const terminalMedian = parameters.x0 * Math.exp(
			(parameters.mu - parameters.sigma ** 2 / 2) * parameters.horizon
		);
		let pathMin = Math.min(
			...pathValues, parameters.x0, terminalMean, terminalMedian
		);
		let pathMax = Math.max(
			...pathValues, parameters.x0, terminalMean, terminalMedian
		);
		const padding = Math.max((pathMax - pathMin) * 0.08, parameters.x0 * 0.04);
		pathMin = Math.max(0, pathMin - padding);
		pathMax += padding;
		if (pathMax === pathMin) pathMax = pathMin + 1;

		const xPath = (time) => pathPanel.x + (time / parameters.horizon) * pathPanel.width;
		const yPath = (value) => pathPanel.y + pathPanel.height -
			((value - pathMin) / (pathMax - pathMin)) * pathPanel.height;
		const meanPoints = [];
		const medianPoints = [];
		for (let index = 0; index <= 100; index += 1) {
			const time = parameters.horizon * index / 100;
			meanPoints.push(
				xPath(time).toFixed(2) + "," +
				yPath(parameters.x0 * Math.exp(parameters.mu * time)).toFixed(2)
			);
			medianPoints.push(
				xPath(time).toFixed(2) + "," +
				yPath(parameters.x0 * Math.exp(
					(parameters.mu - parameters.sigma ** 2 / 2) * time
				)).toFixed(2)
			);
		}
		const pathPoints = path.map((point) => `${xPath(point[0]).toFixed(2)},${yPath(point[1]).toFixed(2)}`).join(" ");

		chart.append(
			element("text", {x: pathPanel.x, y: 18, class: "geometric-brownian-title"}, "Satu lintasan gerak Brown geometrik"),
			element("rect", {x: pathPanel.x, y: pathPanel.y, width: pathPanel.width, height: pathPanel.height, class: "geometric-brownian-frame"}),
			element("line", {x1: pathPanel.x, y1: yPath(parameters.x0), x2: pathPanel.x + pathPanel.width, y2: yPath(parameters.x0), class: "geometric-brownian-initial"}),
			element("polyline", {points: meanPoints.join(" "), class: "geometric-brownian-mean"}),
			element("polyline", {points: medianPoints.join(" "), class: "geometric-brownian-median"}),
			element("polyline", {points: pathPoints, class: "geometric-brownian-path"}),
			element("line", {x1: pathPanel.x + 6, y1: pathPanel.y + 18, x2: pathPanel.x + 26, y2: pathPanel.y + 18, class: "geometric-brownian-path"}),
			element("text", {x: pathPanel.x + 30, y: pathPanel.y + 22, class: "geometric-brownian-legend"}, "lintasan"),
			element("line", {x1: pathPanel.x + 82, y1: pathPanel.y + 18, x2: pathPanel.x + 102, y2: pathPanel.y + 18, class: "geometric-brownian-mean"}),
			element("text", {x: pathPanel.x + 106, y: pathPanel.y + 22, class: "geometric-brownian-legend"}, "rataan"),
			element("line", {x1: pathPanel.x + 155, y1: pathPanel.y + 18, x2: pathPanel.x + 175, y2: pathPanel.y + 18, class: "geometric-brownian-median"}),
			element("text", {x: pathPanel.x + 179, y: pathPanel.y + 22, class: "geometric-brownian-legend"}, "median"),
			element("line", {x1: pathPanel.x + 6, y1: pathPanel.y + 31, x2: pathPanel.x + 26, y2: pathPanel.y + 31, class: "geometric-brownian-initial"}),
			element("text", {x: pathPanel.x + 30, y: pathPanel.y + 35, class: "geometric-brownian-legend"}, "nilai awal"),
			element("text", {x: pathPanel.x, y: 315}, "0"),
			element("text", {x: pathPanel.x + pathPanel.width - 12, y: 315}, shortFormat(parameters.horizon)),
			element("text", {x: pathPanel.x + pathPanel.width / 2 - 5, y: 337}, "t")
		);

		const bins = 20;
		const rangeMin = Math.exp(location - 4 * scale);
		const rangeMax = Math.exp(location + 4 * scale);
		const width = (rangeMax - rangeMin) / bins;
		const counts = Array(bins).fill(0);
		for (const value of endpoints) {
			const index = Math.floor((value - rangeMin) / width);
			if (index >= 0 && index < bins) counts[index] += 1;
		}
		const empiricalDensities = counts.map((count) => count / (endpoints.length * width));
		const mode = Math.exp(location - scale ** 2);
		const theoreticalPeak = lognormalDensity(mode, location, scale);
		const densityMax = Math.max(theoreticalPeak, ...empiricalDensities) * 1.12;
		const xDensity = (value) => densityPanel.x + ((value - rangeMin) / (rangeMax - rangeMin)) * densityPanel.width;
		const yDensity = (value) => densityPanel.y + densityPanel.height - (value / densityMax) * densityPanel.height;

		chart.append(
			element("text", {x: densityPanel.x, y: 18, class: "geometric-brownian-title"}, "Kepadatan empiris dan lognormal teoretis"),
			element("rect", {x: densityPanel.x, y: densityPanel.y, width: densityPanel.width, height: densityPanel.height, class: "geometric-brownian-frame"})
		);
		for (let index = 0; index < bins; index += 1) {
			const x = densityPanel.x + index * densityPanel.width / bins;
			const y = yDensity(empiricalDensities[index]);
			chart.append(element("rect", {
				x,
				y,
				width: densityPanel.width / bins - 1,
				height: densityPanel.y + densityPanel.height - y,
				class: "geometric-brownian-bar"
			}));
		}
		const densityPoints = [];
		for (let index = 0; index <= 180; index += 1) {
			const xValue = rangeMin + (rangeMax - rangeMin) * index / 180;
			densityPoints.push(`${xDensity(xValue).toFixed(2)},${yDensity(lognormalDensity(xValue, location, scale)).toFixed(2)}`);
		}
		chart.append(
			element("polyline", {points: densityPoints.join(" "), class: "geometric-brownian-density"}),
			element("text", {x: densityPanel.x, y: 315}, shortFormat(rangeMin)),
			element("text", {x: densityPanel.x + densityPanel.width - 50, y: 315}, shortFormat(rangeMax)),
			element("text", {x: densityPanel.x + densityPanel.width / 2 - 12, y: 337}, "X_T")
		);

		description.textContent = `Lintasan gerak Brown geometrik yang bermula di ${shortFormat(parameters.x0)}; ` +
			`histogram ${parameters.repetitions} nilai pada T=${shortFormat(parameters.horizon)} dibandingkan dengan kepadatan lognormal teoretis. ` +
			`Rataan empiris ${format(empiricalMean)} dan varians sampel ${format(empiricalVariance)}.`;
		description.textContent +=
			" Panel lintasan juga menampilkan kurva rataan teoretis bergaris putus panjang dan median teoretis bergaris putus pendek.";
	}

	function run() {
		try {
			const parameters = readParameters();
			const random = seededRandom(parameters.seed);
			const dt = parameters.horizon / parameters.steps;
			const logDrift = (parameters.mu - parameters.sigma ** 2 / 2) * dt;
			const logScale = parameters.sigma * Math.sqrt(dt);
			const endpoints = [];
			let firstPath = [[0, parameters.x0]];
			for (let repetition = 0; repetition < parameters.repetitions; repetition += 1) {
				let value = parameters.x0;
				const currentPath = repetition === 0 ? [[0, parameters.x0]] : null;
				for (let step = 1; step <= parameters.steps; step += 1) {
					value *= Math.exp(logDrift + logScale * standardNormal(random));
					if (currentPath) currentPath.push([step * dt, value]);
				}
				if (currentPath) firstPath = currentPath;
				endpoints.push(value);
			}
			const empiricalMean = endpoints.reduce((sum, value) => sum + value, 0) / endpoints.length;
			const orderedEndpoints = [...endpoints].sort((left, right) => left - right);
			const middle = Math.floor(orderedEndpoints.length / 2);
			const empiricalMedian = orderedEndpoints.length % 2 === 0
				? (orderedEndpoints[middle - 1] + orderedEndpoints[middle]) / 2
				: orderedEndpoints[middle];
			const empiricalVariance = endpoints.reduce(
				(sum, value) => sum + (value - empiricalMean) ** 2,
				0
			) / (endpoints.length - 1);
			const theoreticalMean = parameters.x0 * Math.exp(parameters.mu * parameters.horizon);
			const theoreticalMedian = parameters.x0 * Math.exp(
				(parameters.mu - parameters.sigma ** 2 / 2) * parameters.horizon
			);
			const theoreticalVariance = parameters.x0 ** 2 *
				Math.exp(2 * parameters.mu * parameters.horizon) *
				(Math.exp(parameters.sigma ** 2 * parameters.horizon) - 1);
			const theoreticalProbability = normalCdf(
				(parameters.mu - parameters.sigma ** 2 / 2) *
				Math.sqrt(parameters.horizon) / parameters.sigma
			);
			const empiricalProbability = endpoints.filter(
				(value) => value > parameters.x0
			).length / endpoints.length;
			cells.theoreticalMean.textContent = format(theoreticalMean);
			cells.empiricalMean.textContent = format(empiricalMean);
			cells.theoreticalMedian.textContent = format(theoreticalMedian);
			cells.empiricalMedian.textContent = format(empiricalMedian);
			cells.theoreticalVariance.textContent = format(theoreticalVariance);
			cells.empiricalVariance.textContent = format(empiricalVariance);
			cells.theoreticalProbability.textContent = format(theoreticalProbability);
			cells.empiricalProbability.textContent = format(empiricalProbability);
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
