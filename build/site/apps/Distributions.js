//JavaScript file for Random, http://www.randomservices.org/random/
"use strict";

//Constants
const DISC = 0, CONT = 1, EULER = 0.5772156649;

//Special Functions
//Error function
function erf(x) {
	let p = 0.3275911, a1 = 0.254829592, a2 = -0.284496736, a3 = 1.421413741, a4 = -1.453152027, a5 = 1.061405429;
	let x0 = Math.abs(x);
	let t = 1 / (1 + p * x0)
	let y = 1 - (a1 * t + a2 * t ** 2 + a3 * t ** 3 + a4 * t ** 4 + a5 * t ** 5) * Math.exp(-(x ** 2));
	if (x >= 0) return y; 
	else return -y;}
//Standard normal cdf
function stdNormalCDF(x) {
	return 0.5 + 0.5 * erf(x / Math.sqrt(2));
}
//Tests for parity
function isEven(n) {
    if (n % 2 === 0) return true;
	else return false;
}
function isOdd(n) {
	if ((n - 1) % 2 === 0) return true;
	else return false;
}
//Sign functon
function sgn(x) {
	if (x > 0) return 1;
	else if (x < 0) return -1;
	else return 0;
}
//Sorting functions
function ascend(a, b) {
	return a - b;
}
function descend(a, b) {
	return b - a;
}
//Generalzied power function
function genPow(a, n, b) {
	let p = 1;
	for (let i = 0; i < n; i++)	p *= (a + i * b);
	return p;
}
//Rising power funtion
function risePow(a, n) {
	return genPow(a, n, 1);
}
//Falling power function
function perm(n, k) {
	let p = 1;
	for (let i = 0; i < k; i++)	p *= (n - i);
	return p;
}
//Factorial function
function factorial(n) {
	return perm(n, n);
}
//Binomial coefficient
function binomial(n, k) {
	if (k < 0 || k > n) return 0;
	else {
		let p = 1;
		for (let i = 0; i < k; i++)	p *= ((n - i) / (k - i));
		return Math.round(p);
	}
}
//Polylogarithm function
function polyLog(a, x) {
	let sum = 0, k = 1, e = 0.0001;
	while (x ** k / k ** a > e) {
		sum += x ** k / k ** a;
		k++;
	}
	return sum;
}
//Random sample of size n from a population array p
function sample(p, n, type) {
	const m = p.length;
	let t, k, u;
	let s = [];
	if (type == 1) {
		for (let i = 0; i < n; i++) {
			u = Math.floor(m * Math.random());
			s[i] = p[u];
		}
	}
	else {
		for (let j = 0; j < n; j++) {
			k = m - j;
			u = Math.floor(k * Math.random());
			s[j] = p[u];
			t = p[k - 1];
			p[k - 1] = p[u];
			p[u] = t;
		}
	}
	return s;
}
//Log gamma function
function logGamma(x) {
	const coef = [76.18009173, -86.50532033, 24.01409822, -1.231739516, 0.00120858003, -0.00000536382];
	const step = 2.50662827465, fpf = 5.5;
	let t = x - 1;
	let tmp = t + fpf;
	tmp = (t + 0.5) * Math.log(tmp) - tmp;
	let ser = 1;
	for (let i = 1; i <= 6; i++) {
		t++;
		ser += coef[i - 1]/t;
	}
	return tmp + Math.log(step * ser);
}
//Gamma function
function gamma(x) {
	return Math.exp(logGamma(x));
}
//Gamma series function
function gammaSeries(x, a) {
	const maxit = 100, eps = 0.0000003;
	let sum = 1 / a, ap = a, gln = logGamma(a), del = sum;
	for (let n = 1; n <= maxit; n++) {
		ap++;
		del = del * x / ap;
		sum += + del;
		if (Math.abs(del) < Math.abs(sum) * eps) break;
	}
	return sum * Math.exp(-x + a * Math.log(x) - gln);
}
//Gamma continued fraction function
function gammaCF(x, a) {
	const maxit = 100, eps = 0.0000003;
	let gln = logGamma(a), g = 0, gOld = 0, a0 = 1, a1 = x, b0 = 0, b1 = 1, fac = 1;
	let an, ana, anf;
	for (let n = 1; n <= maxit; n++) {
		an = 1.0 * n;
		ana = an - a;
		a0 = (a1 + a0 * ana) * fac;
		b0 = (b1 + b0 * ana) * fac;
		anf = an * fac;
		a1 = x * a0 + anf * a1;
		b1 = x * b0 + anf * b1;
		if (a1 !== 0) {
			fac = 1.0/a1;
			g = b1 * fac;
			if (Math.abs((g - gOld) / g) < eps) break;
			gOld = g;
		}
	}
	return Math.exp(-x + a * Math.log(x) - gln) * g;
}
//Gamma cdf
function gammaCDF(x, a) {
	if (x <= 0) return 0;
	else if (x < a + 1) return gammaSeries(x, a);
	else return 1 - gammaCF(x, a);
}
//Beta continued fraction function
	function betaCF(x, a, b) {
	const maxit = 100, eps = 0.0000003;
    let am = 1, bm = 1, az = 1, qab = a + b, qap = a + 1, qam = a - 1, bz = 1 - qab * x / qap, tem, em, d, bpp, bp, app, aOld, ap;
	for (let m = 1; m <= maxit; m++) {
		em = m;
		tem = em + em;
		d = em * (b - m) * x / ((qam + tem) * (a + tem));
		ap = az + d * am;
		bp = bz + d * bm;
		d = -(a + em) *(qab + em) * x / ((a + tem) * (qap + tem));
		app = ap + d * az;
		bpp = bp + d * bz;
		aOld = az;
		am = ap / bpp;
		bm = bp / bpp;
		az = app / bpp;
		bz = 1;
		if (Math.abs(az - aOld) < eps * Math.abs(az)) break;
	}
	return az;
}
//Beta cdf
function betaCDF(x, a, b) {
	let bt = 0;
	if ((x === 0) || (x === 1)) bt = 0;
	else bt = Math.exp(logGamma(a + b) - logGamma(a) - logGamma(b) + a * Math.log(x) + b * Math.log(1 - x));
	if (x < (a + 1) / (a + b + 2)) return bt * betaCF(x, a, b) / a;
	else return 1 - bt * betaCF(1 - x, b, a) / b;
}
//Zeta function
function zeta(s) {
	const digits = 4;
	const terms = Math.ceil(Math.pow(10, digits / s));
	let sum = 0;
	for (let n = 1; n < terms; n++)
	sum += 1 / n ** s;
	return sum;
}
//Interval data distribution taking values in an interval with a specified step size
class Data {
    constructor(lower, upper, step) {
		this.lower = lower;
		this.upper = upper;
		this.step = step;
        this.intervals = Math.round((this.upper - this.lower) / this.step) + 1;
		this.f = [];
		this.reset();
    }
	reset() {
		this.sum = 0;
		this.sumSq = 0;
		this.points = 0;
		this.maxFreq = 0;
		this.min = this.upper;
		this.max = this.lower;
		for(let i = 0; i < this.intervals; i++) this.f[i] = 0;
	}
	index(x) {
		if (this.lower <= x && x <= this.upper)	return Math.round((x - this.lower) / this.step);
		else return NaN;
	}
	center(x) {
		if (this.lower <= x && x <= this.upper)	return this.lower + this.index(x) * this.step;
		else return NaN;
	}
	setValue(x) {
		this.points++;
		this.sum += x;
		this.sumSq += x ** 2;
		if (x < this.min) this.min = x;
		if (x > this.max) this.max = x;
		let i = this.index(x);
		this.f[i]++;
		if (this.f[i] > this.maxFreq) this.maxFreq = this.f[i];
	}	
	mean() {
		return this.sum / this.points;
	}	
	meanSquare() {
		return this.sumSq / this.points;
	}	
	variance() {
        let n = this.points;
		return this.sumSq / (n - 1) - this.sum ** 2 / (n * (n - 1));
	}	
	stdDev() {
		return Math.sqrt(this.variance());
	}
	freq(x) {
		return this.f[this.index(x)];
	}
	relFreq(x) {
		return this.freq(x) / this.points;
	}
	density(x) {
		return this.relFreq(x) / this.step;
	}	
	maxRelFreq() {
		return this.maxFreq / this.points;
	}
	maxDensity() {
		return this.maxRelFreq() / this.step;
	}
}

//Complete data distribution
class CompleteData {
	constructor() {
		this.reset();
	}
	reset() {
		this.values = [];
		this.sum = 0;
		this.sumSq = 0;
		this.size = 0;
	}
	setValue(x) {
		this.values.push(x);
		this.sum += x;
		this.sumSq += x ** 2;
		this.size++;
	}
	mean() {
		return this.sum / this.size;
	}	
	varianceP() {
		return this.sumSq / this.size - this.mean() ** 2;
	}
	stdDevP() {
		return Math.sqrt(this.varianceP());
	}
	variance() {
        let n = this.size;
		return (n / (n - 1)) * this.varianceP();
	}	
	stdDev() {
		return Math.sqrt(this.variance());
	}
	orderStat(i) {
		let v1 = this.values;
		v1.sort(ascend)
		return v1[i - 1];
	}
	quantile(p) {
		let r = (this.size - 1) * p + 1;
		let k = Math.floor(r);
		let t = r - k;
		if (k == this.size) return this.orderStat(k);
		else return this.orderStat(k) + t * (this.orderStat(k + 1) - this.orderStat(k));
	}
	minValue() {
		return this.orderStat(1);
	}
	maxValue() {
		return this.orderStat(this.size);
	}
	median() {
		return this.quantile(0.5);
	}
	quartile(i) {
		if (i == 1) return this.quantile(0.25);
		else if (i == 2) return this.quantile(0.5);
		else if (i == 3) return this.quantile(0.75)
		else return NaN;
	}
	freq(a, b) {
		let k = 0;
		for (let i = 0; i < this.size; i++) if (a <= this.values[i] && this.values[i] <= b) k++;
		return k;
	}
	relFreq(a, b) {
		return this.freq(a, b) / this.size;
	}
	density(a, b) {
		return this.relFreq(a, b) / (b - a);
	}
}
//Generic probability distribution on the interval [a, b] with step size s of a give type with a given pdf
class Distribution {
	constructor(min, max, step, type, pdf) {
		this.min = min;
		this.max = max;
		this.step = step;
		this.type = type;
		this.pdf = pdf;
		if (this.type == DISC) this.dx = 1; else this.dx = this.step;
		this.data = new Data(min, max, step);
	}
	intervals() {
		return Math.round((this.max - this.min) / this.step + 1);
	}
	index(x) {
		if (this.min <= x && x <= this.max) return Math.round((x - this.min) / this.step);
		else return NaN;
	}
	density(x) {
		if (this.min <= x && x <= this.max) return this.pdf[this.index(x)];
		else return 0;
	}
	mode() {
        const min = this.min, max = this.max, step = this.step;
		let x0 = min, y0 = this.density(x0), y = y0;
		for (let x = min; x <= max; x += step) {
			y = this.density(x);
			if (y > y0) {
				y0 = y;
				x0 = x;
			}
		}
		return x0;
	}
	maxDensity() {
		return this.density(this.mode());
	}
	cdf(y) {
		const min = this.min, max = this.max, step = this.step, dx = this.dx;
		if (y < min) return 0;
		else if (y >= max) return 1;
		else {
			let sum = 0;
			for (let x = min; x <= y; x += step) sum += this.density(x) * dx;
			return sum;
		}
	}
	quantile(p) {
		const min = this.min, max = this.max, step = this.step;
		let x, q;
		if (p === 0) return min;
		else if (p === 1) return max;
		else if (0 < p & p < 1) {
			if (this.type == DISC) {
				x = min;
				q = this.density(x);
				while(q < p) {
					x += step;
					q += this.density(x);
				}
			}
			else {
				let x1 = this.min, x2 = this.max; 
				x = (x1 + x2) / 2;
				q = this.cdf(x); 
				let e = Math.abs(q - p), k = 1;
				while (e > 0.00001 && k < 500) {
					k++;
					if (q < p) x1 = x; else x2 = x;
					x = (x1 + x2) / 2;
					q = this.cdf(x);
					e = Math.abs(q - p);
				}
			}
			return x;
		}
		else return NaN;
	}
	moment(k, t) {
        const min = this.min, max = this.max, step = this.step;
		let sum = 0;
		for (let x = min; x <= max; x += step) sum += ((x - t) ** k) * this.density(x) * this.dx;
		return sum;
	}
	rawMoment(k) {
		return this.moment(k, 0);
	}
	mean() {
		return this.rawMoment(1);
	}
	centralMoment(k) {
		return this.moment(k, this.mean());
	}
	variance() {
		return this.centralMoment(2);
	}
	stdDev() {
		return Math.sqrt(this.variance());
	}
	skew() {
		return this.centralMoment(3) / this.stdDev() ** 3;
	}
	kurt() {
		return this.centralMoment(4) / this.stdDev() ** 4;
	}
	mgf(t) {
        const m = this.min, M = this.max, s = this.step;
		let sum = 0;
		for (let x = m; x <= M; x += s) sum += Math.exp(t * x) * this.density(x) * this.dx;
		return sum;
	}
	pgf(t) {
        const min = this.min, max = this.max, step = this.step, dx = this.dx;
		let sum = 0;
		for (let x = min; x <= max; x += step) sum += (t ** x) * this.density(x) * dx;
		return sum;
	}
	median() {
		return this.quantile(0.5);
	}
	quartile(i) {
		if (i == 1) return this.quantile(0.25);
		else if (i == 2) return this.quantile(0.5);
		else if (i == 3) return this.quantile(0.75);
		else return NaN;
	}
	simulate() {
		let x = this.quantile(Math.random());
		return this.setValue(x);
	}
	setValue(x) {
		this.data.setValue(x);
		return x;
	}
}
//Point mass distribution at a given point
class PointMassDistribution extends Distribution {
	constructor(x0) {
		super(x0, x0, 1, DISC);
		this.x0 = x0;
	}
	density(x) {
		if (x == this.x0) return 1;
		else return 0;
	}
	mode() {
		return this.x0;
	}
	mean() {
		return this.x0;
	}
	variance() {
		return 0;
	}
	cdf(x) {
		if (x < this.x0) return 0;
		else if (x >= this.x0) return 1;
		else return NaN;
	}
	quantile(p) {
		if (0 <= p && p <= 1) return this.x0;
		else return NaN;
	}
	simulate() {
		return this.setValue(this.x0);
	}
	pgf(t) {
		return t ** this.x0;
	}
}
//Distributions related to Bernoulli trials
//Binomial distribution with n trials and probability of success p
class BinomialDistribution extends Distribution {
	constructor(n, p) {
		super(0, n, 1, DISC);
		this.n = Math.round(n);
		if (p < 0) p = 0; else if (p > 1) p = 1;
		this.p = p;
	}
	density(x) {
        const n = this.n, p = this.p;
		if (0 <= x && x <= n) {
			let k = Math.round(x);
			return binomial(n, k) * (p ** k) * ((1 - p) ** (n - k));
		}
		else return 0;
	}
	mode() {
        const n = this.n, p = this.p;
		if (p === 1) return n;
		else return Math.floor((n + 1) * p);
	}
	mean() {
		return this.n * this.p;
	}
	variance() {
		return this.n * this.p * (1 - this.p);
	}
	simulate() {
        const n = this.n, p = this.p;
		let k = 0;
		for (let i = 1; i <= n; i++) if (Math.random() < p) k++;
		return this.setValue(k);
	}
	pgf(t) {
        const n = this.n, p = this.p;
		return (1 - p + p * t) ** n;
	}
	mgf(t) {
		return this.pgf(Math.exp(t));
	}
	skew() {
        const n = this.n, p = this.p;
		return (1 - 2 * p) / Math.sqrt(n * p * (1 - p));
	}
	kurt() {
        const n = this.n, p = this.p;
		return (1 - 6 * p * (1 - p)) / (n * p * (1 - p));
	}
	factorialMoment(k) {
        const n = this.n, p = this.p;
		return perm(n, k) * (p ** k);
	}
}
//Bernoulli distribution with parameter p
class BernoulliDistribution extends BinomialDistribution {
	constructor(p) {
		super(1, p);
	}
}
//Negative binomial distribution on N_k with stopping parameter k and success probability p
class NegativeBinomialDistribution extends Distribution {
	constructor(k, p) {
		super(k, k / p + 4 * Math.sqrt(k * (1 - p) / p ** 2), 1, DISC);
		this.k = k;
		this.p = p;
	}
	mode() {
		return Math.floor((this.k - 1) / this.p + 1);
	}
	density(x) {
        const k = this.k, p = this.p;
		let n = Math.round(x);
		if (n < k) return 0;
		else return binomial(n - 1, k - 1) * (p ** k) * ((1 - p) ** (n - k));
	}
	quantile(q) {
		if (q == 1 && this.p < 1) return Infinity;
		else return super.quantile(q);
	}
	mean() {
		return this.k / this.p;
	}
	variance() {
        const k = this.k, p = this.p;
		return k * (1 - p) / p ** 2;
	}
	simulate() {
        const k = this.k, p = this.p;
		let count = 0, trials = 0;
		while (count < k) {
			if (Math.random() < p) count++;
			trials++;
		}
		return this.setValue(trials);
	}
	pgf(t) {
        const k = this.k, p = this.p;
		if (Math.abs(t) >= 1 / (1 - p)) return NaN;
		else return ((p * t / (1 - (1 - p) * t))) ** k;
	}
	mgf(t) {
		return this.pgf(Math.exp(t));
	}
	skew() {
        const k = this.k, p = this.p;
		return (2 - p) / Math.sqrt(k * (1 - p));
	}
	kurt() {
        const k = this.k, p = this.p;
		return (1 / k) * (6 + p ** 2 / (1 - p));
	}
}

//Geometric distribution on N_+ with success parameter p
class GeometricDistribution extends NegativeBinomialDistribution {
	constructor(p) {
		super(1, p);
	}
	cdf(x) {
        const p = this.p;
		if (x < 1) return 0;
		else return 1 - (1 - p) ** x;
	}
	quantile(q) {
        const p = this.p;
		if (q == 1 && p < 1) return Infinity;
		else return Math.ceil(Math.log(1 - q) / Math.log(1 - p));
	}
}

//Negative binomial distribution on N with stopping parameter k and success probability p
class NegativeBinomialDistribution0 extends Distribution {
	constructor(k, p) {
		super(0, k * (1 - p) / p + 4 * Math.sqrt(k * (1 - p) / p ** 2), 1, DISC);
		this.k = k;
		this.p = p;
	}
	mode() {
		const k = this.k, p = this.p;
		return Math.floor(Math.abs(k - 1) * (1 - p) / p);
	}
	density(x) {
		const k = this.k, p = this.p;
		let n = Math.round(x);
		if (n < 0) return 0;
		else return binomial(n + k - 1, n) * p ** k * (1 - p) ** n;
	}
	quantile(q) {
		if (q == 1 && this.p < 1) return Infinity;
		else return super.quantile(q);
	}
	mean() {
		const k = this.k, p = this.p;
		return k * (1 - p) / p;
	}
	variance() {
		const k = this.k, p = this.p;
		return k * (1 - p) / p ** 2;
	}
	simulate() {
		const k = this.k, p = this.p;
		let count = 0, trials = 0;
		while (count < k){
			if (Math.random() < p) count++;
			trials++;
		}
		return this.setValue(trials - this.k);
	}
	pgf(t) {
		const k = this.k, p = this.p;
		if (Math.abs(t) >= 1 / (1 - p)) return NaN;
		else return (p / (1 - (1 - p) * t)) ** k;
	}
	mgf(t){
		return this.pgf(Math.exp(t));
	}
	skew() {
		const k = this.k, p = this.p;
		return (2 - p) / Math.sqrt(k * (1 - p));
	}
	kurt() {
		const k = this.k, p = this.p;
		return (3 * (k + 2) * (1 - p) + p ** 2) / (k * (1 - p));
	}
}
//Geometric distribution on N with success parameter p
class GeometricDistribution0 extends NegativeBinomialDistribution0 {
	constructor(p) {
		super(1, p);
	}
	cdf(x) {
		const p = this.p;
		if (x < 0) return 0;
		else return 1 - (1 - p) ** (x + 1);
	}
	quantile(q) {
		if (0 <= q && q <= 1) return Math.ceil(Math.log(1 - q) / Math.log(1 - this.p) - 1);
		else return NaN;
	}
}

//Beta-binomial distribution with left shape parameter a, right shape parameter b and n trials
class BetaBinomialDistribution extends Distribution {
	constructor(a, b, n) {
		super(0, n, 1, DISC);
		this.a = a;
		this.b = b;
		this.n = n;
	}
	density(x) {
        const a = this.a, b = this.b, n = this.n;
		return binomial(n, x) * risePow(a, x) * risePow(b, n - x) / risePow(a + b, n);
	}
	mean() {
		const a = this.a, b = this.b, n = this.n;
		return n * (a / (a + b));
	}
	variance() {
        const a = this.a, b = this.b, n = this.n;
		return (n * a * b / (a + b) ** 2) * (1 + (n - 1) / (a + b + 1));
	}
}
//Beta-negative binomial distribution with left shape parameter a, right shape parameter b, and k successes
class BetaNegativeBinomialDistribution extends Distribution {
	constructor(a, b, k) {
		let m = k * (a + b - 1) / (a - 1);
		let s2 = k * (a + b - 1) * (b + k * (a + b - 2)) / ((a - 1) * (a - 2)) - m ** 2;
		super(k, Math.round(m + 4 * Math.sqrt(s2)), 1, DISC);
		this.a = a;
		this.b = b;
		this.k = k;
	}
	density(x) {
        const a = this.a, b = this.b, k = this.k;
		let prod1 = 1, prod2 = 1;
		for (let i = 0; i < k; i++) prod1 *= (a + i) / (a + b + i);
		for (let j = 0; j < x - k; j++) prod2 *= (b + j) / (a + b + k + j);
		return binomial(x - 1, k - 1) * prod1 * prod2;
	}
	mean() {
        const a = this.a, b = this.b, k = this.k;
		return k * (a + b - 1) / (a - 1);
	}
	variance() {
        const a = this.a, b = this.b, k = this.k, m = this.mean();
		return k * (a + b - 1) * (b + k * (a + b - 2)) / ((a - 1) * (a - 2)) - m ** 2;
	}
}

//The binomial distribution with the number of trials randomized
class BinomialNDistribution extends Distribution {
	constructor(dist, p) {
		super(0, dist.max, 1, DISC);
		this.dist = dist;
		this.p = p;
	}
	density(x) {
        const N = this.dist.max, s = this.dist.step, p = this.p;
		let sum = 0;
		for (let n = x; n <= N; n += s) sum += this.dist.density(n) * binomial(n, x) * (p ** x) * ((1 - p) ** (n - x));
		return sum;
	}
	mean() {
		return this.dist.mean() * this.p
	}
	variance() {
        const m = this.dist.mean(), v = this.dist.variance(), p = this.p;
		return m * p * (1 - p) + (p ** 2) * v;
	}
	simulate() {
        const p = this.p;
		let trials = Math.round(this.dist.simulate());
		let successes = 0;
		for (let i = 0; i <= trials; i++) if (Math.random() <= p) successes++;
		return this.setValue(successes);
	}
}

//Distributions based on finite sampling models
//Hypergeometric distribution with population size m, number of red r, and sample size n
class HypergeometricDistribution extends Distribution {
	constructor(m, r, n) {
		super(Math.max(0, n - (m - r)), Math.min(n, r), 1, DISC)
		this.m = m;
		this.r = r;
		this.n = n;
	}
	density(x) {
        const m = this.m, r = this.r, n = this.n;
		return binomial(r, x) * binomial(m - r, n - x) / binomial(m, n);
	}
	mode() {
        const m = this.m, r = this.r, n = this.n;
		return Math.floor((r + 1) * (n + 1) / (m + 2));
	}
	mean() {
        const m = this.m, r = this.r, n = this.n;
		return n * (r / m);
	}
	variance() {
        const m = this.m, r = this.r, n = this.n;
		return n * (r / m) * (1 - r / m) * (m - n) / (m - 1);
	}
}

//Polya distribution with r initial red, g initial green, a added, and sample size n
class PolyaDistribution extends Distribution {
	constructor(r, g, a, n) {
		super(0, n, 1, DISC);
		this.r = r;
		this.g = g;
		this.a = a;
		this.n = n;
	}
	density(x) {
		const r = this.r, g = this.g, a = this.a, n = this.n;
		let p1 = 1, p2 = 1;
		for (let i = 0; i < x; i++) p1 *= (n - i) * (r + i * a) / ((r + g + i * a) * (x - i));
		for (let j = 0; j < n - x; j++) p2 *= (g + j * a) / (r + g + (x + j) * a);
		return p1 * p2;
	}
	mean() {
        const r = this.r, g = this.g, n = this.n;
		return n * r / (r + g);
	}
	variance() {
		const p = this.r / (this.r + this.g), q = this.a / (this.r + this.g + this.a);
		const n = this.n;
		return n * p * (1 - p) * (1 + (n - 1) * q);
	}
	simulate() {
		const a = this.a, n = this.n;
		let s = 0, rt = this.r, gt = this.g, p = 0;
		for (let i = 1; i <= n; i++) {
			p = rt / (rt + gt);
			if (Math.random() < p) {
				s++;
				rt += a;
			}
			else gt += a;
		}
		return this.setValue(s);
	}
}

//Birthday Distribution with population size m and sample size n
class BirthdayDistribution extends Distribution{
	constructor(m, n) {
		super(1, Math.min(m, n), 1, DISC);
		this.m = m;
		this.n = n;
		let upperIndex;
		this.prob = [];
		for (let i = 0; i < n + 1; i++) {
			this.prob[i] = [];
			for (let j = 0; j < m + 1; j++) this.prob[i][j] = 0;
		}
		this.prob[0][0] = 1;
		this.prob[1][1] = 1;
		for (let k = 1; k < n; k++) {
			if (k < m) upperIndex = k + 1; else upperIndex = m;
			for (let l = 1; l <= upperIndex; l++) {
				this.prob[k + 1][l] = this.prob[k][l] * (l / m) + this.prob[k][l - 1] * ((m - l + 1) / m);
			}
		}
	}
	density(x) {
		return this.prob[this.n][x];
	}
	mode() {
		const m = this.m, n = this.n, prob = this.prob;
		let k = 1;
		for (let x = 1; x <= Math.min(m, n); x++) if (prob[n][x] > prob[n][k]) k = x;
		return k;
	}
	mean() {
		const m = this.m, n = this.n;
		return m * (1 - (1 - 1 / m) ** n);
	}

	variance() {
		const m = this.m, n = this.n;
		return m * (m - 1) * (1 - 2 / m) ** n + m * (1 - 1 / m) ** n - m ** 2 * (1 - 1 / m) ** (2 * n);
	}
	simulate() {
		const m = this.m, n = this.n;
		let count = [], distinct = 0;
		for (let i = 0; i < m; i++) count[i] = 0;
		for (let i = 1; i <= n; i++) {
			let j = Math.floor(m * Math.random());
			if (count[j] === 0) distinct++;
			count[j]++;
		}
		return this.setValue(distinct);
	}
}

//Coupon collector distribution with population size m and k distinct 
class CouponDistribution extends Distribution {
	constructor(m, k) {
		let mu = 0, s2 = 0;
		for (let i = 1; i <= k; i++) mu += m / (m - i + 1);
		for (let i = 1; i <= k; i++) s2 += (m * (i - 1)) / ((m - i + 1) * (m - i + 1));
		super(k, Math.round(mu + 4 * Math.sqrt(s2)), 1, DISC);
		this.m = m;
		this.k = k;
	}
	density(x) {
		const m = this.m, k = this.k;
		let sum = 0;
		for (let j = 0; j < k; j++) sum += (-1) ** j * binomial(k - 1, j) * ((k - j - 1) / m) ** (x - 1);
		return binomial(m - 1, k - 1) * sum;
	}
	mean() {
		const m = this.m, k = this.k;
		let mu = 0;
		for (let i = 1; i <= k; i++) mu += m / (m - i + 1);
		return mu;
	}
	variance() {
		const m = this.m, k = this.k;
		let s2 = 0;
		for (let i = 1; i <= k; i++) s2 += (m * (i - 1)) / (m - i + 1) ** 2;
		return s2;
	}
	simulate() {
		const m = this.m, k = this.k;
		let cellCount = [], ballIndex = 0, occupiedCells = 0, ballCount = 0;
		for (let i = 0; i < m; i++) cellCount[i] = 0;
		while (occupiedCells < k) {
			ballCount++;
			ballIndex = Math.floor(m * Math.random());
			if (cellCount[ballIndex] === 0) occupiedCells++;
			cellCount[ballIndex]++;
		}
		return this.setValue(ballCount);
	}
}

//Finite order statistic distribution with population size m, sample size n, and order k
class FiniteOrderStatistic extends Distribution{
	constructor(m, n, k) {
		super(k, m - n + k, 1, DISC);
		this.m = m;
		this.n = n;
		this.k = k;
	}
	density(x) {
		const m = this.m, n = this.n, k = this.k;
		return binomial(x - 1, k - 1) * binomial(m - x, n - k) / binomial(m, n);
	}
	mean() {
		const m = this.m, n = this.n, k = this.k;
		return k * (m + 1) / (n + 1);
	}
	variance() {
		const m = this.m, n = this.n, k = this.k;
		return (m + 1) * (m - n) * k * (n + 1 - k) / ((n + 1) ** 2 * (n + 2));
	}
}

//Matching distribtion with population size n
class MatchDistribution extends Distribution {
	constructor(n) {
		super(0, n, 1, DISC);
		this.n = n;
	}
	density(x) {
		const n = this.n;
		let sum = 0, sign = -1;
		for (let j = 0; j <= n - x; j++) {
			sign = -sign;
			sum += sign / factorial(j);
		}
		return sum / factorial(x);	}
	mode() {
		if (this.n === 2) return 0; 
		else return 1;
	}
	mean() {
		return 1;
	}
	variance() {
		return 1;
	}
	simulate() {
		const n = this.n; 
		let p = [], s = [], sum = 0;
		for (let i = 0; i < n; i++) p[i] = i + 1;
		s = sample(p, n);
		for (let j = 0; j < n; j++) if (s[j] === j + 1) sum++;
		return this.setValue(sum);
	}
}
//Distributions related to random walks
//Distribution of the maximum position in the simple random walk with n steps
class WalkMaxDistribution extends Distribution {
	constructor(n) {
		super(0, n, 1, DISC);
		this.n = n;
	}
	density(x) {
		const n = this.n;
		let m = 0;
		if ((x + n) % 2 === 0) m = (x + n) / 2;
		else m = (x + n + 1) / 2;
		return binomial(n, m) / 2 ** n;
	}
	mode() {
		return 0;
	}
	simulate() {
		const n = this.n;
		let step = 0, max = 0, position = 0;
		for (let i = 1; i <= n; i++) {
			if (Math.random() < 0.5) step = 1;
			else step = -1;
			position += step;
			if (position > max) max = position;
		}
		return this.setValue(max);
	}}

//Distribution of the final position in the simple random walk with n steps
class WalkPositionDistribution extends Distribution {
	constructor(n, p) {
		super(-n, n, 2, DISC);
		this.n = n;
		this.p = p;
	}
	density(x) {
		const n = this.n, p = this.p;
		let k = 0;
		if ((x + n) % 2 === 0) {
			k = (x + n) / 2;
			return binomial(n, k) * (p ** k) * (1 - p) ** (n - k);
		}
		else return 0;
	}
	mode() {
		const n = this.n, p = this.p;
		if (p === 1) return n;
		else return 2 * Math.floor((n + 1) * p) - n;
	}
	mean() {
		const n = this.n, p = this.p;
		return n * (2 * p - 1);
	}
	variance() {
		const n = this.n, p = this.p;
		return 4 * n * p * (1 - p);
	}
	simulate() {
		const n = this.n, p = this.p;
		let step = 0, position = 0;
		for (let i = 1; i <= n; i++) {
			if (Math.random() < p) step = 1;
			else step = -1;
			position += step;
		}
		return this.setValue(position);
	}
}

//Discrete arcsine distribution with parameter n (even)
class DiscreteArcsineDistribution extends Distribution {
	constructor(n) {
		super(0, n, 2, DISC);
		this.n = n;
	}
	density(x) {
		const n = this.n;
		if (x % 2 == 0 && x >= 0 && x <= n) return binomial(x, x / 2) * binomial(n - x, (n - x) / 2) / 2 ** n;
		else return 0;
	}
	mode() {
		return 0;
	}
	mean() {
		return this.n / 2;
	}
	variance() {
		const n = this.n;
		return n * (n + 2) / 8;
	}
	simulate() {
		const n = this.n;
		let step = 0, lastZero = 0, position = 0;
		for (let i = 1; i <= n; i++) {
			if (Math.random() < 0.5) step = 1;
			else step = -1;
			position += step;
			if (position === 0) lastZero = i;
		}
		return this.setValue(lastZero);
	}
}

//Distributions related to the normal distribution
//Normal distribution with mean m and standard deviation s
class NormalDistribution extends Distribution {
	constructor(m, s) {
		super(m - 4 * s, m + 4 * s, s / 10, CONT);
		this.m = m;
		this.s = s;
		this.c = 1 / (s * Math.sqrt(2 * Math.PI));
	}
	mode() {
		return this.m;
	}
	maxDensity() {
		return this.c;
	}
	density(x) {
		let z = (x - this.m) / this.s;
		return this.c * Math.exp(-0.5 * z ** 2);
	}
	cdf(x) {
		return stdNormalCDF((x - this.m) / this.s);
	}	
	quantile(p) {
		let z = 0;
		if (p == 0) return -Infinity;
		else if (p == 1) return Infinity;
		else if (p == 1 / 2) return this.m;
		else if (p > 1 / 2) {
			while (stdNormalCDF(z) < p) z += 0.0001;
			return this.m + z * this.s;
		}
		else {
			while (stdNormalCDF(z) < 1 - p) z += 0.0001;
			return this.m - z * this.s;
		}
	}
	mean() {
		return this.m;
	}
	variance() {
		return this.s ** 2;
	}
	stdDev() {
		return this.s;
	}
	mgf(t) {
		const m = this.m, s = this.s;
		return Math.exp(m + 0.5 * (s ** 2) * (t ** 2));
	}
	pgf(t) {
		if (t <= 0) return NaN;
		else return this.mgf(Math.log(t));
	}
	centralMoment(n) {
		const s = this.s;
		let k = 0;
		if (n % 2 == 0) {
			k = n / 2;
			return (factorial(n) / (factorial(k) * 2 ** k)) * s ** n;
		}
		else return 0;
	}
	simulate() {
		const m = this.m, s = this.s;
		let r = Math.sqrt(-2 * Math.log(Math.random()));
		let theta = 2 * Math.PI * Math.random();
		let x = m + s * r * Math.cos(theta);
        return this.setValue(x);  
	}
}

//Folded Normal distribution with normal mean a and normal standard deviation b
class FoldedNormalDistribution extends Distribution {
	constructor(a, b) {
		let m = b * Math.sqrt(2 / Math.PI) * Math.exp(-Math.pow(a, 2) / (2 * Math.pow(b, 2))) + a * (1 - 2 * stdNormalCDF(-a / b));		let s2 = Math.pow(a, 2) + Math.pow(b, 2) - Math.pow(b * Math.sqrt(2 / Math.PI) * Math.exp(-Math.pow(a, 2) / (2 * Math.pow(b, 2))) + a * (1 - 2 * stdNormalCDF(-a / b)), 2);
		let s = Math.sqrt(s2);
		let mn = Math.max(0, m - 3 * s);
		let mx = m + 3 * s;
		super(mn, mx, (mx - mn) / 100, CONT);
		this.a = a;
		this.b = b;
	}
    density(x) {
		const a = this.a, b = this.b, c = 1 / (b * Math.sqrt(2 * Math.PI));
		let z = -1 / (2 * b ** 2);
        if (x >= 0) return c * Math.exp(z * (x + a) ** 2) + c * Math.exp(z * (x - a) ** 2);
        else return 0;
     }
	 maxDensity() {
		const a = this.a;
    	return Math.max(this.density(Math.abs(a)), this.density(0));
	}
    cdf(x) {
		const a = this.a, b = this.b;
		return 0.5 * (erf((x + a) / (Math.sqrt(2) * b)) + erf((x - a) / (Math.sqrt(2) * b)));
	}
	mean() {
		const a = this.a, b = this.b;
		return b * Math.sqrt(2 / Math.PI) * Math.exp(-(a ** 2) / (2 * b ** 2)) + a * (1 - 2 * stdNormalCDF(-a / b));
	}
    variance() {
		const a = this.a, b = this.b;
		return a ** 2 + b ** 2 - Math.pow(b * Math.sqrt(2 / Math.PI) * Math.exp(-(a ** 2) / (2 * b ** 2)) + a * (1 - 2 * stdNormalCDF(-a / b)), 2);
	}
	simulate() {
		const a = this.a, b = this.b;
		let r = Math.sqrt(-2 * Math.log(Math.random()));
		let theta = 2 * Math.PI * Math.random();
		let x = Math.abs(a + b * r * Math.cos(theta)); 
        return this.setValue(x);  
	}
}
//Half normal distribution with scale parameter b
class HalfNormalDistribution extends FoldedNormalDistribution {
	constructor(b) {
		super(0, b);
	}
	mode() {
		return 0;
	}
}
//Maxwell-Boltzmann distributiion with scale parameter b
class MaxwellBoltzmannDistribution extends Distribution {
	constructor(b) {
		let m = 2 * b * Math.sqrt(2 / Math.PI);
		let s = b * Math.sqrt(3 - 8 / Math.PI);
		let mx = m + 4 * s;
		super(0, mx, mx / 100, CONT);
		this.b = b;
	}
	density(x) {
		const b = this.b;
		if (x >= 0) return Math.sqrt(2 / Math.PI) * x ** 2 * Math.exp(-(x ** 2) / (2 * b ** 2)) / b ** 3;
		else return 0;
	}
	mode() {
		return Math.sqrt(2) * this.b;
	}
	mean() {
		return 2 * this.b * Math.sqrt(2 / Math.PI);;
	}
	variance() {
		const b = this.b;
		return (b * Math.sqrt(3 - 8 / Math.PI)) ** 2;
	}
	simulate() {
		let r = 0, theta = 0, x = 0, sum = 0;
		for (let i = 0; i < 3; i++) {
			r = Math.sqrt(-2 * Math.log(Math.random()));
			theta = 2 * Math.PI * Math.random();
			sum += (this.b * r * Math.cos(theta)) ** 2;
		}
		x = Math.sqrt(sum);
		return this.setValue(x); 
	}
}
//Student t distribution with n degrees of freedom
class StudentDistribution extends Distribution {
	constructor(n) {
		let mx;
		if (n == 1) mx = 8;
		else if (n == 2) mx = 7;
		else mx = 4 * Math.sqrt(n / (n - 2));
		super(-mx, mx, mx / 50, CONT);
		this.n = n;
	}
	mode() {
		return 0;
	}
	density(x) {
		const n = this.n, c = gamma((n + 1) / 2) / (Math.sqrt(n * Math.PI) * gamma(n / 2));
		return c * Math.pow(1 + x ** 2 / n, -(n + 1) / 2);
	}
	cdf(x) {
		const n = this.n;
		let u = n / (n + x ** 2);
		if (x > 0) return 1 - 0.5 * betaCDF(u, 0.5 * n, 0.5);
		else return 0.5 * betaCDF(u, 0.5 * n, 0.5);
	}
	mean() {
		if (this.n == 1) return NaN;
		else return 0;
	}
	variance() {
		const n = this.n;
		if (n == 1) return NaN;
		else if (n == 2) return Infinity;
		else return n / (n - 2);
	}
	simulate() {
		const n = this.n;
		let x = 0, v = 0, z = 0, r = 0, theta = 0;
		for (let i = 1; i <= n; i++) {
			r = Math.sqrt(-2 * Math.log(Math.random()));
			theta = 2 * Math.PI * Math.random();
			z = r * Math.cos(theta);
			v += z ** 2;
		}
		r = Math.sqrt(-2 * Math.log(Math.random()));
		theta = 2 * Math.PI * Math.random();
		z = r * Math.cos(theta);
		x = z / Math.sqrt(v / n);
		return this.setValue(x);
	}
}
//F distribution with n degrees of freedom in the numberator and d degrees of freedom in the denominator
class FDistribution extends Distribution {
	constructor(n, d) {
		let mn, mx;
		if (n < 2) mn = 0.01; else mn = 0;
		if (d <= 4) mx = 20; 
		else mx = d / (d - 2)  + 4 * Math.sqrt(2.0 * (d / (d - 2)) * (d / (d - 2)) * (d + n - 2) / (n * (d - 4)));
		super(mn, mx, (mx - mn) / 100, CONT);
		this.n = n;
		this.d = d;
	}
	mode() {
		const n = this.n, d = this.d;
		if (n <= 2) return this.min;
		else return ((n - 2) * d) / (n * (d + 2));
	}
	density(x) {
		const n = this.n, d = this.d, c = (gamma((n + d) / 2)/(gamma(n / 2) * gamma(d / 2))) * (n / d) ** (n / 2);
		return c * x ** ((n - 2) / 2) / ((1 + (n / d) * x) ** ((n + d) / 2));
	}
	cdf(x) {
		const n = this.n, d = this.d;
		let u = d / (d + n * x);
		if (x <= 0) return 0;
		else return 1 - betaCDF(u, 0.5 * d, 0.5 * n);
	}
	mean() {
		const d = this.d;
		if (d <= 2) return Infinity;
		else return d / (d - 2);
	}
	variance() {
		const n = this.n, d = this.d;
		if (d <= 2) return NaN;
		else if (d <= 4) return Infinity;
		else return 2.0 * (d / (d - 2)) * (d / (d - 2))	* (d + n - 2) / (n * (d - 4));
	}
	simulate() {
		const n = this.n, d = this.d;
		let x, u = 0, v = 0, z, r, theta;
		for (let i = 1; i <= n; i++) {
			r = Math.sqrt(-2 * Math.log(Math.random()));
			theta = 2 * Math.PI * Math.random();
			z = r * Math.cos(theta);
			u = u + z ** 2;
		}
		for (let j = 1; j <= d; j++) {
			r = Math.sqrt(-2 * Math.log(Math.random()));
			theta = 2 * Math.PI * Math.random();
			z = r * Math.cos(theta);
			v = v + z ** 2;
		}
		x = (u / n) / (v / d);
		return this.setValue(x);
	}
}
//Lognormal distribution with log-scale parameter m and shape parameter s
class LogNormalDistribution extends Distribution {
	constructor(m, s) {
		let mn = Math.exp(m + s * s / 2);
		let va = Math.exp(2 * (m + s * s)) - Math.exp(2 * m + s * s);
		let mx = mn + 3 * Math.sqrt(va);
		super(0, mx, mx / 100, CONT);
		this.m = m;
		this.s = s;
	}
	density(x) {
		const m = this.m, s = this.s;
		if (x == 0) return 0;
		else {
			let y = (Math.log(x) - m) ** 2;
			return Math.exp(-y / (2 * s ** 2)) / (Math.sqrt(2 * Math.PI) * s * x);
		}
	}
	mode() {
		const m = this.m, s = this.s;
		return Math.exp(m - s ** 2);
	}
	cdf(x) {
		let z = 0;
		if (x <= 0) return 0;
		else {
			z = (Math.log(x) - this.m) / this.s;
			if (z >= 0) return 0.5 + 0.5 * gammaCDF(0.5 * z ** 2, 0.5);
			else return 0.5 - 0.5 * gammaCDF(0.5 * z ** 2, 0.5);
		}
	}
	mean() {
		const m = this.m, s = this.s;
		return Math.exp(m + s ** 2 / 2);
	}
	variance() {
		const m = this.m, s = this.s;
		return Math.exp(2 * (m + s ** 2)) - Math.exp(2 * m + s ** 2);
	}
	simulate() {
		const m = this.m, s = this.s;
		let r = Math.sqrt(-2 * Math.log(Math.random()));
		let theta = 2 * Math.PI * Math.random();
		let x = Math.exp(m + s * r * Math.cos(theta));
		return this.setValue(x); 
	}
}
//Distributions related to the Poisson and gamma
//Poisson distribution with rate r
class PoissonDistribution extends Distribution{
	constructor(r) {
		super(0, Math.ceil(r + 4 * Math.sqrt(r)), 1, DISC);
		this.r = r;
	}
	density(x) {
		const r = this.r;
		let k = Math.round(x), p = 1;
		if (k >= 0) {
			for (let i = 0; i < k; i++) p *= r / (k - i);
			return Math.exp(-r) * p;
		}
		else return 0;
	}
	mode() {
		return Math.floor(this.r);
	}
	cdf(x) {
		return 1 - gammaCDF(this.r, x + 1);
	}
	mean() {
		return this.r;
	}
	variance() {
		return this.r;
	}
	simulate() {
		const r = this.r;
		let arrivals = 0;
		let sum = -Math.log(1 - Math.random());
		while (sum <= r) {
			arrivals++;
			sum = sum - Math.log(1 - Math.random());
		}
		return this.setValue(arrivals);
	}
	setRate(r) {
		this.r = r;
	}
}
//Gamma Distribution with shape parameter k and scale parameter b
class GammaDistribution extends Distribution {
	constructor(k, b) {
		let m, v, mn, mx;
		if (k >= 1) mn = 0; else mn = 0.01;
		m = k * b;
		v = k * Math.pow(b, 2);
		mx = m + 4 * Math.sqrt(v);
		super(mn, mx, (mx - mn) / 100, CONT);
		this.k = k;
		this.b = b;
		this.c = 1 / (gamma(k) * b ** k);
	}	mode() {
		const k = this.k, b = this.b;
		if (k < 1) return this.min;
		else return b * (k - 1);
	}
	density(x) {
		const k = this.k, b = this.b, c = this.c;
		if (x >= 0) return c * x ** (k - 1) * Math.exp(-x / b);
		else return 0;
	}
	cdf(x) {
		return gammaCDF( x / this.b, this.k);
	}
	mean() {
		return this.k * this.b;
	}
	variance() {
		const k = this.k, b = this.b;
		return k * b ** 2;
	}
	shape() {
		return this.k;
	}
	scale() {
		return this.b;
	}
	rate() {
		return 1 / this.b;
	}
}
//Chi-square distribution with n degrees of freedom
class ChiSquareDistribution extends GammaDistribution {
	constructor(n) {
		super(n / 2, 2);
		this.n = n;
	}
	simulate() {
		const n = this.n;
		let v = 0, z, r, theta;
		for (let i = 1; i <= n; i++) {
			r = Math.sqrt(-2 * Math.log(Math.random()));
			theta = 2 * Math.PI * Math.random();
			z = r * Math.cos(theta);
			v = v + z ** 2;
		}
		return this.setValue(v);
	}
}
//Exponential distribution with scale parameter b
class ExponentialDistribution extends GammaDistribution {
	constructor(b) {
		super(1, b);
	}
	cdf(x) {
		if (x >= 0) return 1 - Math.exp(-x / this.b);
		else return 0;
	}
	quantile(p) {
		if (0 <= p && p <= 1) return -this.b * Math.log(1 - p);
		else return NaN;
	}
}
//Distribution related to the beta distribution
//Beta distribution with left shape parameter a and right shape parameter b
class BetaDistribution extends Distribution {
	constructor(a, b) {
		let mn, mx;
		if (a < 1) mn = 0.01; else mn = 0;
		if (b < 1) mx = 0.99; else mx = 1;
		super(mn, mx, 0.01, CONT);
		this.a = a;
		this.b = b;
		this.c = gamma(a + b) / (gamma(a) * gamma(b));
	}
	mode() {
		const a = this.a, b = this.b;
		let m = 0;
		if (a < 1 && b < 1) {
			if (a < b) m = 0.01; else m = 0.99;
		}
		else if (a < 1 && b >= 1) m = 0.01;
		else if (a >= 1 && b < 1) m = 0.99;
		else if (a >= 1 && b == 1) m = 1;
		else if (a == 1 && b >= 1) m = 0;
		else m = (a - 1) / (a + b - 2);
		return m;
	}
	density(x) {
		const a = this.a, b = this.b, c = this.c;
		if (0 <= x && x <= 1) return c * x ** (a - 1) * (1 - x) ** (b - 1);
		else return 0;
	}
	cdf(x) {
		if (x <= 0) return 0;
		else if (x >= 1) return 1;
		else return betaCDF(x, this.a, this.b);
	}
	mean() {
		const a = this.a, b = this.b;
		return a / (a + b);
	}
	variance() {
		const a = this.a, b = this.b;
		return a * b / ((a + b) ** 2 * (this.a + this.b + 1));
	}
}
//Beta prime distribution with shape parameters a and b
class BetaPrimeDistribution extends Distribution {
	constructor(a, b) {
		let mn, mx;
		if (a >= 1) mn = 0;	else mn = 0.01;
		if (b > 2) mx = 4 * Math.sqrt(a * (a + b - 1) / ((b - 2) * Math.pow(b - 1, 2)));
		else mx = 4 * a / b;
		super(mn, mx, (mx - mn) / 100, CONT);
		this.a = a; 
		this.b = b;
		this.c = gamma(a + b) / (gamma(a) * gamma(b));
	}
	mode() {
		const a = this.a, b = this.b;
		if (a >= 1) return (a - 1) / (b + 1);
		else return this.min;
	}
	density(x) {
		const a = this.a, b = this.b, c = this.c;
		if (x > 0 || (x == 0) && (a == 1)) return c * x ** (a - 1) / (1 + x) ** (a + b);
		else return 0;
	}
	cdf(x) {
		const a = this.a, b = this.b;
		if (x <= 0) return 0; 
		else return betaCDF(x / (x + 1), a, b);
	}
	mean() {
		const a = this.a, b = this.b;
		if (b > 1) return a / (b - 1);
		else return Infinity;
	}
	variance() {
		const a = this.a, b = this.b;
		if (b > 2) return a * (a + b - 1) / ((b - 2) * (b - 1) ** 2) ;
		else if (b > 1) return Infinity;
		else return NaN;
	}
	simulate() {
	 	let u = new BetaDistribution(this.a, this.b).simulate();
	 	let x = u / (1 - u);
	 	return this.setValue(x);
	 }
}
//Uniform  and related distributions
//Uniform distribution on the interval [a, a + w]
class UniformDistribution extends Distribution {
	constructor(a, w) {
		super(a, a + w, w / 100, CONT);
		this.a = a;
		this.w = w;
	}
	density(x) {
		const a = this.a, w = this.w;
		if (a <= x && x <= a + w) return 1 / w;
		else return 0;
	}
	mode() {
		return this.a;
	}
	cdf(x) {
		const a = this.a, w = this.w;
		if (x < a) return 0;
		else if (x > a + w) return 1;
		else return (x - a) / w;
	}
	quantile(p) {
		const a = this.a, w = this.w;
		if (p < 0 || p > 1) return NaN;
		else return a + p * w;
	}	mean() {
		const a = this.a, w = this.w;
		return a + w / 2;
	}
	variance() {
		const w = this.w;
		return w ** 2 / 12;
	}
}
//Discrete uniform distribution on n points, starting at a, and with step size h
class DiscreteUniformDistribution extends Distribution {
	constructor(a, n, h) {
		let b = a + (n - 1) * h;
		super(a, b, h, DISC);
		this.a = a;
		this.n = n;
		this.h = h;
		this.b = b;
	}
	density(x) {
		const a = this.a, n = this.n, h = this.h;
		let j = Math.round((x - a) / h);
		if (0 <= j && j < n) return 1 / n;
		else return 0;
	}
	mode() {
		return this.a;
	}
	cdf(x) {
		const a = this.a, n = this.n, h = this.h;
		let j = Math.round((x - a) / h);
		if (j < 0) return 0;
		else if (j > n - 1) return 1;
		else return (j + 1) / n;
	}
	simulate() {
		const a = this.a, n = this.n, h = this.h;
		let x = a + h * Math.floor(n * Math.random());
		return this.setValue(x);
	}
	mean() {
		const a = this.a, b = this.b;
		return (a + b) / 2;
	}
	variance() {
		const a = this.a, n = this.n, h = this.h;
		return (n - 1) * (n + 1) * h ** 2 / 12;
	}
}
//Irwin-Hall distribution
class IrwinHallDistribution extends Distribution {
	constructor(n) {
		super(0, n, n / 100, CONT);
		this.n = n;
	}
	mode() {
		return this.n / 2;
	}
	density(x) {
		const n = this.n;
		let sum = 0;
		if (n == 1) return 1;
		else {
			for (let k = 0; k <= n; k++) sum += (-1) ** k * binomial(n, k)*  (x - k) ** (n - 1) * sgn(x - k);
			return sum / (2 * factorial(n - 1));
		}
	}
	cdf(x) {
		const n = this.n;
		let sum = 0;
		if (x < 0) return 0;
		else if (x > n) return 1;
		else {
			for (let k = 0; k <= n; k++) sum += (-1) ** k * binomial(n, k) * sgn(x - k) * (x - k) ** n;
			return 0.5 + sum / (2 * factorial(n));
		}
	}
	simulate() {
		const n = this.n;
		let sum = 0;
		for (let i = 0; i < n; i++) sum += Math.random();
		return this.setValue(sum);
	}
	mean() {
		return this.n / 2;
	}
	variance() {
		return this.n / 12;
	}
}
//Distributions based on shapes
//Triangle distribution on the interval [a, a + w] with vertex at a + p w
class TriangleDistribution extends Distribution {
	constructor(a, w, p) {
		super(a, a + w, w / 100, CONT);
		this.a = a;
		this.w = w;
		this.p = p;
	}
	standardDensity(x) {
		const p = this.p;
		if (p == 0 && 0 <= x && x <= 1) return 2 * (1 - x);
		else if (p == 1 && 0 <= x && x <= 1) return 2 * x;
		else if (0 <= x && x <= p) return 2 * x / p;
		else if (p < x && x <= 1) return 2 * (1 - x) / (1 - p);
		else return 0;
	}
	standardCDF(x) {
		const p = this.p;
		if (x < 0) return 0;
		else if (p == 0 && 0 <= x && x <= 1) return 1 - (1 - x) ** 2;
		else if (p == 1 && 0 <= x & x <= 1) return x ** 2;
		else if (0 <= x && x <= p) return x ** 2 / p;
		else if (p < x && x <= 1) return 1 - (1 - x) ** 2 / (1 - p);
		else return 1;
	}
	standardQuantile(q) {
		const p = this.p;
		if (0 <= q && q <= p) return Math.sqrt(q * p);
		else if (p < q && q <= 1) return 1 - Math.sqrt((1 - q) * (1 - p));
		else return NaN;
	}
	density(x) {
		const a = this.a, w = this.w;
		return (1 / w) * this.standardDensity((x - a) / w);
	}
	cdf(x) {
		const a = this.a, w = this.w;
		return this.standardCDF((x - a) / w);
	}
	quantile(q) {
		return this.a + this.w * this.standardQuantile(q);
	}
	mode() {
		const a = this.a, w = this.w, p = this.p;
		let m = a + p * w;
		if (p == 1) m = a + w;
		return m;
	}
	mean() {
		const a = this.a, w = this.w, p = this.p;
		return a + w * (1 + p) / 3;
	}
	variance() {
		const a = this.a, w = this.w, p = this.p;
		return w ** 2 * (1 - p + p ** 2) / 18;
	}
}
//Semicircle distribution with center a and radius r
class SemiCircleDistribution extends Distribution {
	constructor(a, r) {
		super(a - r, a + r, r / 50, CONT);
		this.a = a;
		this.r = r;
	}
	standardDensity(x) {
		if (x < -1 || x > 1) return 0;
		else return 2 * Math.sqrt(1 - x ** 2) / Math.PI;
	}
	standardCDF(x) {
		if (x < -1) return 0;
		else if (x > 1) return 1;
		else return 0.5 + x * Math.sqrt(1 - x ** 2) / Math.PI + Math.asin(x) / Math.PI;
	}
	density(x) {
		const a = this.a, r = this.r;
		return (1 / r) * this.standardDensity((x - a) / r);
	}
	cdf(x) {
		return this.standardCDF((x - this.a) / this.r);
	}
	mode() {
		return this.a;
	}
	mean() {
		return this.a;
	}
	variance() {
		const r = this.r;
		return r ** 2 / 4;
	}
	simulate() {
		const a = this.a, r = this.r;
		let u = Math.random(), v = Math.random(), t = Math.max(u, v);
		let theta = 2 * Math.PI * Math.random();
		let x = a + r * t * Math.cos(theta);
		return this.setValue(x);
	}
}
//U-quadratic distribution with shape parameter k, location parameter a and scale parameter b
class UPowerDistribution extends Distribution {
	constructor(k, a, b) {
		super(a - b, a + b, b / 100, CONT);
		this.k = k;
		this.a = a;
		this.b = b;
	}
	density(x) {
		const k = this.k, a = this.a, b = this.b;
		if (a - b <= x && x <= a + b) return ((2 * k + 1) / (2 * b)) * ((x - a) / b) ** (2 * k);
		else return 0;
	}
	cdf(x) {
		const k = this.k, a = this.a, b = this.b;
		if (x < a - b) return 0;
		else if (x > a + b) return 1;
		else return (1 / 2) * (1 + ((x - a) / b) ** (2 * k + 1));
	}
	quantile(p) {
		const k = this.k, a = this.a, b = this.b;
		if (0 <= p && p <= 0.5) return a - b * (1 - 2 * p) ** (1 / (2 * k + 1));
		else if (0.5 < p && p <= 1) return a + b * (2 * p - 1) ** (1 / (2 * k + 1)) ;
		else return NaN;
	}
	mode() {
		return this.a - this.b;
	}
	mean() {
		return this.a;
	}
	variance() {
		const k = this.k, b = this.b;
		return b ** 2 * (2 * k + 1) / (2 * k + 3);
	}
}
//Gilbert's sine distribution with location parameter a and scale parameter b
class SineDistribution extends Distribution {
	constructor(a, b) {
		super(a, a + b, b / 100, CONT);
		this.a = a;
		this.b = b;
	}
	density(x) {
		const a = this.a, b = this.b;
		if (x >= a && x <= a + b) return (Math.PI / (2 * b)) * Math.sin(Math.PI * (x - a) / b);
		else return 0;
	}
	mode() {
		return this.a + this.b / 2;
	}
	cdf(x) {
		return (1 / 2) * (1 - Math.cos(Math.PI * (x - this.a) / this.b));
	}
	quantilen(p) {
		return this.a + (this.b / Math.PI) * Math.acos(1 - 2 * p);
	}
	mean() {
		return this.a + this.b / 2;
	}
	variance() {
		return this.b ** 2 * (1 / 4 - 2 / Math.pow(Math.PI, 2));
	}
}
//Sine-square distribution with location parameter a and scale parameter b
class SineSquareDistribution extends Distribution {
	constructor(a, b) {
		super(a, a + b, b / 100, CONT);
		this.a = a;
		this.b = b;
	}
	density(x) {
		const a = this.a, b = this.b;
		if (x >= a && x <= a + b) return (2 / b) * (Math.sin(Math.PI * (x - a) / b)) ** 2;
		else return 0;
	}
	mode() {
		return this.a + this.b / 2;
	}
	cdf(x) {
		let a = this.a, b = this.b;
		if (x < a) return 0;
		else if (x > a + b) return 1;
		else return (x - a) / b - (1 / (2 * Math.PI)) * Math.sin(2 * Math.PI * (x - a) / b);
	}
	mean() {
		return this.a + this.b / 2;
	}
	variance() {
		return this.b ** 2 * (1 / 12 - 1 / (2 * Math.PI ** 2));
	}
}
//Other continuous distributions
//Weibull distribution with shape parameter k and scale parameter b
class WeibullDistribution extends Distribution {
	constructor(k, b) {
		let m, v, mn, mx;
		m = b * gamma(1 + 1 / k);
		v = b * b * gamma(1 + 2 / k) - Math.pow(m, 2);
		if (k < 1) mn = 0.01; else mn = 0;
		mx = m + 4 * Math.sqrt(v);
		super(mn, mx, (mx - mn) / 100, CONT);
		this.k = k;
		this.b = b;
		this.c = k / (b ** k);
	}
	density(x) {
		const k = this.k, b = this.b, c = this.c;
		if (x >= 0) return c * x ** (k - 1) * Math.exp(-((x / b) ** k));
		else return 0;
	}
	mode() {
		const k = this.k, b = this.b;
		if (k < 1) return this.min;
		else return b * ((k - 1) / k) ** (1 / k);
	}	cdf(x) {
		const k = this.k, b = this.b;
		return 1 - Math.exp(-((x / b) ** k));
	}
	quantile(p) {
		const k = this.k, b = this.b;
		return b * (-Math.log(1 - p)) ** (1 / k);
	}
	mean() {
		const k = this.k, b = this.b;
		return b * gamma(1 + 1 / k);
	}
	variance() {
		const k = this.k, b = this.b, m = this.mean();
		return b ** 2 * gamma(1 + 2 / k) - m ** 2;
	}
}
//Pareto distribution with shape parameter k and scale parameter b
class ParetoDistribution extends Distribution {
	constructor(k, b) {
		let mx = b * (1 + 6 / k);
		super(b, mx, (mx - b) / 100, CONT);
		this.b = b;
		this.k = k
		this.c = k * b ** k;
	}
	density(x) {
		const k = this.k, b = this.b, c = this.c;
		if (x < b) return 0;
		else return c / x ** (k + 1);
	}
	mode() {
		return this.b;
	}
	cdf(x) {
		const k = this.k, b = this.b;
		return 1 - (b / x) ** k;
	}
	quantile(p) {
		const k = this.k, b = this.b;
		if (0 <= p && p <= 1) return b / (1 - p) ** (1 / k);
		else return NaN;
	}
	mean() {
		if (this.k <= 1) return Infinity;
		else return (this.k * this.b) / (this.k - 1);
	}
	variance() {
		const k = this.k, b = this.b;
		if (k <= 1) return NaN;
		else if (k > 1 && k <= 2) return Infinity;
		else return (k * b ** 2) / ((k - 1) * (k - 2) ** 2);
	}
}
//Logistic distribution with location parameter a and scale parameter b
class LogisticDistribution extends Distribution { 
	constructor(a, b) {
		let v = (b * b * Math.PI * Math.PI) / 3;
		let mn = a - 4 * Math.sqrt(v);
		let mx = a + 4 * Math.sqrt(v);
		super(mn, mx, (mx - mn) / 100, CONT);
		this.a = a;
		this.b = b;
	}
	density(x) {
		const a = this.a, b = this.b;
		let e = Math.exp((x - a) / b);
		return e / (b * (1 + e) ** 2);
	}
	mode() {
		return this.a;
	}
	cdf(x) {
		const a = this.a, b = this.b;
		let e = Math.exp((x - a) / b);
		return e / (1 + e);
	}
	quantile(p) {
		if (0 <= p && p <= 1) return this.a + this.b * Math.log(p / (1 - p));
		else return NaN;
	}
	mean() {
		return this.a;
	}
	variance() {
		const b = this.b;
		return (b ** 2 * Math.PI ** 2) / 3;
	}
}
//Log-logistic distribution with scale parameter a and shape parameter b
class LogLogisticDistribution extends Distribution {
	constructor(a, b) {
		let mn, mx;
		if (b >= 1) mn = 0; else mn = 0.001;
		if (b >= 2) mx = a * Math.pow(100, 1 / b); else mx = a * 10;
		super(mn, mx, (mx - mn) / 100, CONT);
		this.a = a;
		this.b = b;
	}
	density(x) {
		const a = this.a, b = this.b;
		if (x >= 0) return (b / a) * (x / a) ** (b - 1) / (1 + (x / a) ** b) ** 2;
		else return 0;
	}
	mode() {
		const a = this.a, b = this.b;
		if (b >= 1) return a * ((b - 1) / (b + 1)) ** (1 / b);
		else return this.min;
	}
	mean() {
		const a = this.a, b = this.b;
		if (b > 1) return ((a * Math.PI) / b) / Math.sin(Math.PI / b);
		else return Infinity;
	}
	variance() {
		const a = this.a, b = this.b, t = Math.PI / b;
		if (b > 2) return a ** 2 * ((2 * t) / Math.sin(2 * t) - t ** 2 / (Math.sin(t)) ** 2);
		else if (this.b > 1) return Infinity;
		else return NaN;
	}
	cdf(x) {
		const a = this.a, b = this.b;
		if (x < 0) return 0;
		else return x ** b / (a ** b + x ** b);
	}
	quantile(p) {
		const a = this.a, b = this.b;
		if (0 <= p && p <= 1) return a * (p / (1 - p)) ** (1 / this.b);
		else return NaN;
	}
}
//Extreme value distribution with location paramter a and scale parameter b
class ExtremeValueDistribution extends Distribution {
	constructor(a, b) {
		let m = a + b * EULER; 
		let v = Math.pow(b * Math.PI, 2) / 6;
		let mx = m + 4 * Math.sqrt(v); 
		let mn = m - 4 * Math.sqrt(v);
		super(mn, mx, (mx - mn) / 100, CONT);
		this.a = a;
		this.b = b;
	}
	density(x) {
		const a = this.a, b = this.b;
		let e = Math.exp(-(x - a) / b);
		return e * Math.exp(-e) / b;
	}
	mode() {
		return this.a;
	}
	cdf(x) {
		const a = this.a, b = this.b;
		return Math.exp(-Math.exp(-(x - a) / b));
	}
	quantile(p) {
		const a = this.a, b = this.b;
		if (0 <= p && p <= 1) return a - b * Math.log(-Math.log(p));
		else return NaN;
	}
	mean() {
		return this.a + this.b * EULER;
	}
	variance() {
		const b = this.b;
		return (b * Math.PI) ** 2 / 6;
	}
}
//Exponential-Logarithmic distribution with shape parameter p and scale parameter b
class ExponentialLogarithmicDistribution extends Distribution {
	constructor(p, b) {
		super(0, 4 / b, 1 / (25 * b), CONT);
		this.p = p;
		this.b = b;
	}
	mode() {
		return 0;
	}
	density(x) {
		const p = this.p, b = this.b;
		if (x >= 0) return -b * (1 - p) * Math.exp(-b * x) / (Math.log(p) * (1 - (1 - p) * Math.exp(-b * x)));
		else return 0;
	}
	cdf(x) {
		const p = this.p, b = this.b;
		if (x < 0) return 0;
		else return 1 - Math.log(1 - (1 - p) * Math.exp(-b * x)) / Math.log(p);
	}
	quantile(q) {
		const p = this.p, b = this.b;
		if (0 <= q && q <= 1) return Math.log((1 - p) / (1 - p ** (1 - q))) / b;
		else return NaN;
	}
	mean() {
		const p = this.p, b = this.b;
		return -polyLog(2, 1 - p) / (b * Math.log(p));
	}
	variance() {
		const p = this.p, b = this.b, m = this.mean();
		return -2 * polyLog(3, 1 - p) / (b ** 2 * Math.log(p)) - m ** 2;
	}
}
//Cauchy distribution with location parameter a and scale parameter b
class CauchyDistribution extends Distribution {
	constructor(a, b) {
		super(a - 5 * b, a + 5 * b, b / 10, CONT);
		this.a = a;
		this.b = b;
	}
	mode() {
		return this.a;
	}
	density(x) {
		const a = this.a, b = this.b;
		return b / (Math.PI * (b ** 2 + (x - a) ** 2));
	}
	cdf(x) {
		const a = this.a, b = this.b;
		return 1 / 2 + (1 / Math.PI) * Math.atan((x - a) / b);
	}
	quantile(p) {
		const a = this.a, b = this.b;
		return a + b * Math.tan(Math.PI * (p - 0.5));
	}	mean() {
		return NaN;
	}
	variance() {
		return NaN;
	}
}
//Arcsine distribution with location parameter a and scale parameter b
class ArcsineDistribution extends Distribution {
	constructor(a, b) {
		let c = b / 100;
		super(a + c, a + b - c, c, CONT);
		this.a = a;
		this.b = b;
	}
	mode() {
		return NaN;
	}
	maxDensity() {
		return this.density(this.min);
	}
	density(x) {
		const a = this.a, b = this.b;
		if (x <= a || x >= a + b) return 0;
		else return 1 / (Math.PI * Math.sqrt((x - a) * (a + b - x)));
	}
	cdf(x) {
		const a = this.a, b = this.b;
		if (x <= a) return 0;
		else if (x >= a + b) return 1;
		else return (2 / Math.PI) * Math.asin(Math.sqrt((x - a) / b));
	}
	quantile(p) {
		const a = this.a, b = this.b;
		if (0 <= p && p <= 1) return a + b * (Math.sin(p * Math.PI / 2)) ** 2;
		else return NaN;
	}
	mean() {
		const a = this.a, b = this.b;
		return a +  b / 2;
	}
	variance() {
		const b = this.b;
		return b ** 2 / 8;
	}
}
//Hyperbolic Secant distribution wuith mean m and standard deviation s
class HyperbolicSecantDistribution extends Distribution {
	constructor(m, s) {
		super(m - 4 * s, m + 4 * s, (4 * s) / 25, CONT);
		this.m = m;
		this.s = s;
	}
	mode() {
		return this.m;
	}
	density(x) {
		const m = this.m, s = this.s;
		let t = (Math.PI / 2) * ((x - m) / s);
		return 1 / (s * (Math.exp(t) + Math.exp(-t)));
	}
	cdf(x) {
		const m = this.m, s = this.s;
		return (2 / Math.PI) * Math.atan(Math.exp((Math.PI / 2) * (x - m) / s));
	}
	quantile(p) {
		const m = this.m, s = this.s;
		return m + s * (2 / Math.PI) * Math.log(Math.tan((Math.PI / 2) * p));
	}
	mean() {
		return this.m;
	}
	stdDev() {
		return this.s;
	}
	variance() {
		const s = this.s;
		return s ** 2;
	}
}
//Laplace distribution with location parameter a and scale parameter b
class LaplaceDistribution extends Distribution {
	constructor(a, b) {
		super(a - 5 * b, a + 5 * b, b / 10, CONT);
		this.a = a;
		this.b = b;
	}
	mode() {
		return this.a;
	}
	density(x) {
		const a = this.a, b = this.b;
		return Math.exp(-Math.abs(x - a) / b) / (2 * b);
	}
	mean() {
		return this.a;
	}
	variance() {
		const b = this.b;
		return 2 * b ** 2;
	}	quantile(p) {
		const a = this.a, b = this.b;
		if (0 <= p && p <= 0.5) return a + b * Math.log(2 * p);
		else if (0.5 < p && p <= 1) return a - b * Math.log(2 * (1 - p));
		else return NaN;
	}
	cdf(x) {
		const a = this.a, b = this.b;
		if (x <= a) return 0.5 * Math.exp((x - a) / b);
		else return 1 - 0.5 * Math.exp(-(x - a) / b);
	}
}
//Rayleigh distribution with scale parameter b
class RayleighDistribution extends Distribution {
	constructor(b) {
		let m = b * Math.sqrt(Math.PI / 2);
		let s = b * Math.sqrt(2 - Math.PI / 2);
		let mx = m + 4 * s;
		super(0, mx, mx / 100, CONT);
		this.b = b;
	}
	density(x) {
		const b = this.b
		if (x >= 0) return (x / b ** 2) * Math.exp(-0.5 * (x / b) ** 2);
		else return 0;
	}
	cdf(x) {
		const b = this.b;
		if (x >= 0) return 1 - Math.exp(-0.5 * (x / b) ** 2);
		else return 0;
	}
	quantile(p) {
		const b = this.b;
		if (p >= 0 && p < 1) return b * Math.sqrt(-2 * Math.log(1 - p));
		else if (p == 1) return Infinity;
		else return NaN;
	}
	mode() {
		return this.b;
	}
	mean() {
		return this.b * Math.sqrt(Math.PI / 2);
	}
	variance() {
		const b = this.b;
		return (b * Math.sqrt(2 - Math.PI / 2)) ** 2;
	}
}
//Levy distribution with location parameter a and scale parameter b
class LevyDistribution extends Distribution {
	constructor(a, b) {
		let mx = a + 10 * b;
		super(a, mx, (mx - a) / 100, CONT);
		this.a = a;
		this.b = b;
	}
	density(x) {
		const a = this.a, b = this.b;
		if (x > a) return Math.sqrt(b / (2 * Math.PI)) * (1 / (x - a) ** (3 / 2)) * Math.exp(-b / (2 * (x - a)));
		else return 0;
	}
	cdf(x) {
		const a = this.a, b = this.b;
		if (x >= a) return 1 - erf(Math.sqrt(b / (2 * (x - a))));
		else return 0;
	}
	mode() {
		return this.a + this.b / 3;
	}
	simulate() {
		let r = Math.sqrt(-2 * Math.log(Math.random()));
		let theta = 2 * Math.PI * Math.random();
		let z = r * Math.cos(theta);
		let x = this.a + this.b / z ** 2;
		return this.setValue(x); 
	}
	mean() {
		return Infinity;
	}
	variance() {
		return NaN;
	}
}
//Wald distribution with shape mean m and shape parameter s
class WaldDistribution extends Distribution {
	constructor(m, s) {
		let mx = m + 3 * Math.sqrt(Math.pow(m, 3) / s);
		super(0, mx, mx / 100, CONT);
		this.m = m;
		this.s = s;
	}
	density(x) {
		const m = this.m, s = this.s;
		if (x > 0) return Math.sqrt(s / (2 * Math.PI * x ** 3)) * Math.exp(-s * (x - m) ** 2 / (2 * m ** 2 * x));
		else return 0;
	}
	cdf(x) {
		const m = this.m, s = this.s;
		if (x > 0) return stdNormalCDF(Math.sqrt(s / x) * (x / m - 1)) + Math.exp(2 * s / m) * stdNormalCDF(-Math.sqrt(s / x) * (x / m + 1));
		else return 0;
	}
	mode() {
		const m = this.m, s = this.s;
		return m * (Math.sqrt(1 + (3 * m / (2 * s)) ** 2) - 3 * m / (2 * s));
	}
	simulate() {
		const m = this.m, s = this.s;
		let w;
		let r = Math.sqrt(-2 * Math.log(Math.random()));
		let theta = 2 * Math.PI * Math.random();
		let z = r * Math.cos(theta);
		let y = Math.pow(z, 2);
		let x = m + (m ** 2 * y) / (2 * s) - (m / (2 * s)) * Math.sqrt(4 * m * s * y + m ** 2 * y ** 2);
		if (Math.random() <= m / (m + x)) w = x;
		else w = m ** 2 / x;
		return this.setValue(w);
	}
	mean() {
		return this.m;
	}
	variance() {
		const m = this.m, s = this.s;
		return m ** 3 / s;
	}
}
//Gompertz distribution with shape parameter k and scale parameter b
class GompertzDistribution extends Distribution {
	constructor(k, b) {
		let mx = b * Math.log(1 - (1 / k) * Math.log(0.0005));
		super(0, mx, mx / 100, CONT);
		this.k = k;
		this.b = b;
		this.c = (k / b) * Math.exp(k);
	}
	density(x) {
		const k = this.k, b = this.b, c = this.c;
		let e = 0;
		if (x < 0) return 0;
		else {
			e = Math.exp(x / b);
			return c * e * Math.exp(-k * e);
		}
	}
	mode() {
		const k = this.k, b = this.b;
		if (k < 1) return -b * Math.log(k);
		else return 0;
	}
	cdf(x) {
		const k = this.k, b = this.b;
		if (x < 0) return 0;
		else return 1 - Math.exp(-k * (Math.exp(x / b) - 1));
	}
	quantile(p) {
		if (0 <= p && p <= 1) return this.b * Math.log(1 - (1 / this.k) * Math.log(1 -p));
		else return NaN;
	}
}
//Distributions related to Benford's law
//Benford mantissa distribution with base b
class BenfordMantissaDistribution extends Distribution {
	constructor(b) {
		super(1 / b, 1, (1 - 1 / b) / 100, CONT);
		this.b = b;
	}	mode() {
		return this.min;
	}
	density(x) {
		let b = this.b;
		if (1 / b <= x && x <= 1) return 1 / (x * Math.log(this.b));
		else return 0;
	}
	cdf(x) {
		let b = this.b;
		if (x < 1 / b) return 0;
		else if (x > 1) return 1;
		else return 1 + Math.log(x) / Math.log(this.b);
	}
	quantile(p) {
		const b = this.b;
		if (0 <= p && p <= 1) return 1 / b ** (1 - p);
		else return NaN;
	}
	mean() {
		const b = this.b;
		return (b - 1) / (b * Math.log(b));
	}
	variance() {
		const b = this.b;
		return ((b - 1) / (b ** 2 * Math.log(b))) * ((b + 1) / 2 - (b - 1) / Math.log(b));
	}
}
//Benford first digit distribution with base b
class BenfordDigitDistribution extends Distribution {
	constructor(b) {
		super(1, b - 1, 1, DISC);
		this.b = b;
	}
	mode() {
		return 1;
	}
	density(x) {
		return (Math.log(x + 1) - Math.log(x)) / Math.log(this.b);
	}
	cdf(x) {
		return Math.log(x + 1) / Math.log(this.b);
	}
	quantile(p) {
		const b = this.b;
		return Math.ceil(b ** p - 1);
	}
}
//Other discrete distributions
//Zeta distribution with shape parameter a
class ZetaDistribution extends Distribution {
	constructor(a) {
		super(1, Math.ceil(Math.pow(10, 3.5 / a)), 1, DISC);
		this.a = a;
		this.c = zeta(a);
	}
	density(x) {
		const a = this.a, c = this.c;
		return 1 / (c * x ** a);
	}
	mean() {
		const a = this.a;
		if (a > 2) return zeta(a - 1) / zeta(a);
		else return Infinity;
	}
	variance() {
		const a = this.a, m = this.mean();
		if (a > 3) return zeta(a - 2) / zeta(a) - m ** 2;
		else if (a > 2) return Infinity;
		else return NaN;
	}
}
//Logarithmic series distribution with shape parameter p
class LogarithmicDistribution extends Distribution {
	constructor(p) {
		let m = -p / (Math.log(1 - p) * (1 - p));
		let s2 = -p * (p + Math.log(1 - p)) / (Math.pow(1 - p, 2) * Math.pow(Math.log(1 - p), 2));
		super(1, m + 4 * Math.sqrt(s2), 1, DISC);
		this.p = p;
	}
	density(x) {
		const p = this.p;
		return -Math.pow(p, x) / (x * Math.log(1 - p));
	}
	mode() {
		return 1;
	}
	mean() {
		const p = this.p;
		return -p / (Math.log(1 - p) * (1 - p));
	}
	variance() {
		const p = this.p;
		return -p * (p + Math.log(1 - p)) / ((1 - p) ** 2 * (Math.log(1 - this.p)) ** 2);
	}
}
//General classes of distributions
//The location scale distribution with distribution dist, location parameter a, and scale parameter b
class LocationScaleDistribution extends Distribution {
	constructor(dist, a, b) {
		super(a + b * dist.min, a + b * dist.max, b * dist.step, dist.type);
		this.a = a;
		this.b = b;
		this.dist = dist;
	}
	density(x) {
		const a = this.a, b = this.b;
		let y = (x - a) / b;
		if (this.type == DISC) return this.dist.density(y);
		else return this.dist.density(y) / b;
	}
	mode() {
		return this.a + this.b * this.dist.mode();
	}
	maxDensity() {
		if (this.type == DISC) return this.dist.maxDensity();
		else return this.dist.maxDensity() / this.b;
	}
	cdf(x) {
		const a = this.a, b = this.b;
		return this.dist.cdf((x - a) / b);
	}
	quantile(p) {
		return this.a + this.b * this.dist.quantile(p);
	}
	mean() {
		return this.a + this.b * this.dist.mean();
	}
	variance() {
		return this.b ** 2 * this.dist.variance();
	}
	simulate() {
		let x = this.a + this.b * this.dist.simulate();
		return this.setValue(x);
	}}
//Convolution power of a distribution dist of order n
class Convolution extends Distribution {
	constructor(dist, n) {
		super(n * dist.min, n * dist.max, dist.step, dist.type);
		let a = dist.min, b = dist.max, s = dist.step;
		let m = Math.round((b - a) / s) + 1;
		let delta = 1;
		if (dist.type == CONT) delta = dist.step();
		this.dist = dist;
		this.n = n;
		this.pdf = [];
		for (let k = 0; k < n; k++) this.pdf[k] = [];
		for (let j = 0; j < m; j++) this.pdf[0][j] = dist.density(a + j * s);
		for (let k1 = 1; k1 < n; k1++) {
			for (let j1 = 0; j1 < (k1 + 1) * m - k1; j1++) {
				let sum = 0;
				for (let i = Math.max(0, j1 - m + 1); i < Math.min(j1 + 1, k1 * m - k1 + 1); i++) sum += this.pdf[k1 - 1][i] * this.pdf[0][j1 - i] * delta;
				this.pdf[k1][j1] = sum;
			}
		}
	}
	density(x) {
		let index = Math.round((x - this.min) / this.step);
		return this.pdf[this.n - 1][index];
	}
	mean () {
		return this.n * this.dist.mean();
	}
	variance() {
		return this.n * this.dist.variance();
	}
	simulate() {
		const n = this.n;
		let sum = 0;
		for (let i = 1; i <= n; i++) sum += this.dist.simulate();
		return this.setValue(sum);
	}
}
//Distribution of the order statistic from distribution dist with sample size n and order k
class OrderStatistic extends Distribution {
	constructor(dist, n, k) {
		super(dist.min, dist.max, dist.step, dist.type);
		this.dist = dist;
		this.n = n;
		this.k = k;
	}	
	density(x) {
		const n = this.n, k = this.k;
		if (this.type == DISC) return this.cdf(x) - this.cdf(x - this.step);
		else {
			let p = this.dist.cdf(x);
			return k * binomial(n, k) * p ** (k - 1) * (1 - p) ** (n - k) * this.dist.density(x);
		}
	}
	cdf(x) {
		const n = this.n, k = this.k;
		let sum = 0, p = this.dist.cdf(x);
		for (let j = k; j <= n; j++) sum += binomial(n, j) * p ** j * (1 - p) ** (n - j);
		return sum;
	}
	simulate() {
		const n = this.n, k = this.k;
		let sample = [];
		for (let i = 0; i < n; i++) sample[i] = this.dist.simulate();
		sample.sort(ascend);
		let x = sample[k - 1];
		return this.setValue(x);
	}
}

