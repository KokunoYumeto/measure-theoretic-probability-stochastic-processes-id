---
title: "Penilaian Kumulatif D30 — Formulir B"
lang: id-ID
author:
  - "OpenAI Codex (penyusunan materi asli atas arahan pengguna)"
assessment:
  course_id: "course.o009.d30"
  assessment_id: "assessment.o009.d30.cumulative.form-b"
  alternate_of: "assessment.o009.d30.cumulative.form-a"
  form: "B"
  version: "1.0.0"
  total_points: 100
  recommended_time_minutes: 240
  target_locale: "id-ID"
  rights_id: "rights.o009.assessment.cumulative.form-b.cc-by-4.0"
  license: "CC-BY-4.0"
  model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Penilaian Kumulatif D30 — Formulir B {#assessment.o009.d30.cumulative.form-b}

## Identitas, tujuan, dan waktu {#assessment.o009.d30.cumulative.form-b.section.01}

Penilaian ini adalah bentuk alternatif Formulir A untuk peran kurikulum
**O009/D30: Probabilitas Teoretis-Ukuran dan Proses Stokastik**. Formulir B
mengukur domain, hasil belajar, bobot, dan tingkat pembuktian yang sama melalui
objek dan jalur penyelesaian yang berbeda. Kedua formulir tidak dikerjakan
bersamaan.

- **Jumlah soal:** 8; kerjakan semuanya.
- **Nilai maksimum:** 100 poin.
- **Waktu yang dianjurkan:** 240 menit.
- **Pembagian waktu yang dianjurkan:** Soal 1–8 berturut-turut
  30, 30, 35, 25, 30, 25, 35, dan 30 menit.
- **Bahan bantu:** kalkulator non-simbolik boleh dipakai, tetapi tidak
  diperlukan. Semua langkah matematis utama harus ditulis.
- **Konvensi:** semua kesamaan antara peubah acak bersyarat dipahami hampir
  pasti terhadap ukuran yang relevan, kecuali dinyatakan titik demi titik.
  Simbol \(\Phi\) menyatakan fungsi distribusi normal standar.

Jawaban numerik tanpa penalaran tidak memperoleh poin penuh. Bila memakai
sebuah teorema, sebutkan hipotesis yang membuat pemakaiannya sah. Grafik atau
simulasi dapat membantu intuisi, tetapi tidak menggantikan pembuktian
probabilistik.

## Prasyarat yang boleh dipakai {#assessment.o009.d30.cumulative.form-b.section.02}

Modul sampling, hukum bilangan besar (LLN), dan teorema limit pusat (CLT) dari
jalur bersama **O006/C140** merupakan prasyarat. Peserta boleh memakai hasil
berikut tanpa membuktikannya kembali.

1. **SLLN i.i.d.** Jika \(Y_1,Y_2,\ldots\) i.i.d. dan
   \(\mathbb E|Y_1|<\infty\), maka
   \(\overline Y_n\to\mathbb EY_1\) hampir pasti.
2. **CLT i.i.d.** Jika \(Y_1,Y_2,\ldots\) i.i.d.,
   \(\mathbb EY_1=\mu\), dan
   \(0<\operatorname{Var}(Y_1)=\sigma^2<\infty\), maka
   \[
   \frac{\sqrt n(\overline Y_n-\mu)}{\sigma}
   \Rightarrow N(0,1).
   \]
3. Teorema konvergensi monoton, Fatou, konvergensi terdominasi, sifat dasar
   nilai harapan bersyarat, teorema kontinuitas Lévy, dan teorema Slutsky
   boleh dipakai dengan hipotesis yang dinyatakan.
4. **Teorema Vitali.** Jika \(W_n\to W\) dalam probabilitas dan
   \((W_n)_n\) terintegralkan seragam, maka \(W_n\to W\) dalam \(L^1\).
5. Teorema penghentian opsional boleh dipakai pada waktu henti terbatas.
   Pelewatan dari \(\tau\wedge n\) ke \(\tau\) tetap harus dibenarkan.
6. Prinsip refleksi untuk gerak Brown standar boleh dipakai, tetapi hubungan
   yang diminta pada Soal 7 harus diturunkan dengan jelas.

Prasyarat ini tidak mengizinkan pertukaran limit dan ekspektasi tanpa kendali
ekor atau penaikan konvergensi distribusi berdimensi hingga menjadi
konvergensi hukum lintasan tanpa keketatan.

## Cakupan hasil belajar {#assessment.o009.d30.cumulative.form-b.section.03}

Pemetaan berikut sama dengan Formulir A dan menggunakan ID hasil belajar yang
stabil.

| Soal | Domain utama | ID hasil belajar yang dinilai |
|---:|---|---|
| 1 | probabilitas teoretis-ukuran; mode konvergensi; interpretasi LLN/CLT | <code>outcome.o009.distinguish-convergence-modes</code>; <code>outcome.o009.prove-convergence-in-probability</code>; <code>outcome.o009.explain-lln-monte-carlo</code>; <code>outcome.o009.distinguish-evidence-proof</code> |
| 2 | nilai harapan bersyarat; disintegrasi; kernel dan versi nol | <code>outcome.o009.construct-regular-conditional-distribution</code>; <code>outcome.o009.derive-disintegration-and-null-value-versions</code>; <code>outcome.o009.audit-conditional-version-uniqueness</code> |
| 3 | martingal; penghentian; keterintegralan seragam | <code>outcome.o009.prove-stopped-martingale</code>; <code>outcome.o009.check-optional-stopping-conditions</code>; <code>outcome.o009.compute-random-time-expectations</code>; <code>outcome.o009.characterize-ui-martingales</code> |
| 4 | rantai Markov diskret; periodisitas; hukum limit | <code>outcome.o009.compute-discrete-transition-laws</code>; <code>outcome.o009.characterize-markov-periodicity</code>; <code>outcome.o009.solve-finite-limiting-models</code>; <code>outcome.o009.analyze-markov-ergodic-periodic-limits</code> |
| 5 | CTMC; generator; semigrup; proses Poisson | <code>outcome.o009.construct-markov-kernels</code>; <code>outcome.o009.audit-and-repair-stochastic-process-claims</code> |
| 6 | ukuran acak Poisson; hukum bersyarat; penipisan dan superposisi | <code>outcome.o009.formulate-poisson-random-measures</code>; <code>outcome.o009.derive-conditional-poisson-point-laws</code>; <code>outcome.o009.analyze-poisson-thinning-superposition</code> |
| 7 | gerak Brown; hukum Gaussian; martingal; pencapaian dan penskalaan | <code>outcome.o009.characterize-standard-brownian-motion</code>; <code>outcome.o009.solve-brownian-drift-joint-conditional-law</code>; <code>outcome.o009.derive-brownian-hitting-maximum-laws</code> |
| 8 | jembatan Brown; versi bersyarat; FDD versus hukum lintasan | <code>outcome.o009.construct-brownian-bridges</code>; <code>outcome.o009.solve-brownian-bridge-conditional-law</code>; <code>outcome.o009.audit-fdd-versus-path-law-convergence</code> |

## Rubrik penskoran umum {#assessment.o009.d30.cumulative.form-b.rubric.global}

Rubrik per soal bersifat otoritatif dan jumlahnya tepat 100 poin. Poin penuh
memerlukan kesimpulan benar beserta alasan yang memadai. Secara lintas soal:

- ruang, ukuran, filtrasi, versi, dan mode konvergensi adalah bagian jawaban;
- kesalahan aritmetika lokal hanya mengurangi poin pada langkah terdampak;
- teorema yang dipakai tanpa pemeriksaan hipotesis memperoleh paling banyak
  setengah poin pada langkah tersebut;
- bukti empiris tidak menggantikan bukti probabilistik;
- jawaban ringkas menunjukkan target akhir, sedangkan penyelesaian lengkap
  menunjukkan standar penalaran untuk poin penuh.

---

## Bagian I — Dasar ukuran, limit, dan pengondisian {#assessment.o009.d30.cumulative.form-b.section.04}

### Soal 1 — Ukuran sampel Poisson, konsistensi, dan CLT (14 poin) {#assessment.o009.d30.cumulative.form-b.problem.01}

Misalkan \(Y_1,Y_2,\ldots\) i.i.d. dengan
\(\mathbb EY_1=\mu\) dan
\(0<\operatorname{Var}(Y_1)=\sigma^2<\infty\). Untuk setiap \(n\),
misalkan \(N_n\sim\operatorname{Poisson}(n)\), bebas dari seluruh \(Y_k\).
Tuliskan \(S_m=\sum_{k=1}^mY_k\) dan
\[
\widehat\mu_n=
\begin{cases}
S_{N_n}/N_n,&N_n>0,\\
0,&N_n=0.
\end{cases}
\]

1. Buktikan \(N_n/n\to1\) dalam \(L^2\) dan dalam probabilitas, serta
   \(\mathbb P(N_n=0)\to0\). **(4 poin)**
2. Dengan fungsi karakteristik, buktikan
   \[
   \frac{S_{N_n}-\mu N_n}{\sigma\sqrt n}
   \Rightarrow N(0,1).
   \]
   **(3 poin)**
3. Buktikan \(\widehat\mu_n\to\mu\) dalam probabilitas dan
   \[
   \frac{\sqrt{N_n}(\widehat\mu_n-\mu)}{\sigma}
   \Rightarrow N(0,1),
   \]
   dengan konvensi nol pada \(\{N_n=0\}\). **(4 poin)**
4. Jelaskan peran berbeda LLN dan CLT dalam estimasi Monte Carlo. Ketika
   ukuran sampel yang teramati adalah \(m\), hitung galat kuadrat rata-rata
   dan galat baku estimator, lalu jelaskan mengapa satu keluaran simulasi
   bukan bukti kedua teorema. **(3 poin)**

#### Rubrik Soal 1 {#assessment.o009.d30.cumulative.form-b.problem.01.rubric}

| Komponen | Poin |
|---|---:|
| Momen Poisson, konvergensi \(L^2\)/probabilitas, dan kejadian nol | 4 |
| Fungsi karakteristik majemuk dan limit Gaussian | 3 |
| Konsistensi serta normalisasi ukuran sampel acak melalui Slutsky | 4 |
| Interpretasi LLN/CLT, galat kuadrat rata-rata, galat baku, dan batas bukti simulasi | 3 |

#### Petunjuk 1 {#assessment.o009.d30.cumulative.form-b.problem.01.hint.01}

Gunakan
\(\mathbb EN_n=\operatorname{Var}(N_n)=n\). Jika
\(\psi(u)=\mathbb E e^{iu(Y_1-\mu)}\), maka
\[
\mathbb E\exp\!\left\{
it\frac{S_{N_n}-\mu N_n}{\sigma\sqrt n}
\right\}
=\exp\!\left[
n\left\{\psi\!\left(\frac{t}{\sigma\sqrt n}\right)-1\right\}
\right].
\]

#### Petunjuk 2 {#assessment.o009.d30.cumulative.form-b.problem.01.hint.02}

Peubah pada limit fungsi karakteristik bersifat ketat. Pada
\(\{N_n>0\}\), faktorkan estimator dengan \(N_n/n\), lalu gunakan Slutsky;
peluang kejadian pelengkap adalah \(e^{-n}\).

#### Jawaban ringkas {#assessment.o009.d30.cumulative.form-b.problem.01.answer}

\(N_n/n\to1\) dalam \(L^2\) karena variansnya \(1/n\), dan
\(\mathbb P(N_n=0)=e^{-n}\). Ekspansi
\(\psi(u)=1-\sigma^2u^2/2+o(u^2)\) memberi limit normal untuk jumlah
terpusat. Slutsky kemudian memberi
\(\widehat\mu_n\to\mu\) dalam probabilitas serta CLT dengan normalisasi
\(\sqrt{N_n}\). LLN menjelaskan konsistensi; CLT menjelaskan fluktuasi.
Untuk ukuran sampel \(m\), galat kuadrat rata-rata adalah \(\sigma^2/m\)
dan galat bakunya \(\sigma/\sqrt m\). Satu simulasi hanyalah satu realisasi.

#### Penyelesaian lengkap {#assessment.o009.d30.cumulative.form-b.problem.01.solution}

Momen Poisson memberi
\[
\mathbb E\!\left(\frac{N_n}{n}-1\right)^2
=\frac{\operatorname{Var}(N_n)}{n^2}
=\frac1n\longrightarrow0.
\]
Jadi \(N_n/n\to1\) dalam \(L^2\), dan karena itu dalam probabilitas.
Selain itu, \(\mathbb P(N_n=0)=e^{-n}\to0\).

Untuk \(W_k=Y_k-\mu\), fungsi karakteristiknya memenuhi
\[
\psi(u)=1-\frac{\sigma^2u^2}{2}+o(u^2)
\quad(u\to0).
\]
Independensi \(N_n\) dari sampel dan fungsi pembangkit Poisson memberi
\[
\begin{aligned}
\mathbb E\exp\!\left\{
it\frac{S_{N_n}-\mu N_n}{\sigma\sqrt n}
\right\}
&=\exp\!\left[
n\left\{\psi\!\left(\frac{t}{\sigma\sqrt n}\right)-1\right\}
\right]\\
&\longrightarrow e^{-t^2/2}.
\end{aligned}
\]
Teorema kontinuitas Lévy menghasilkan limit \(N(0,1)\).

Tuliskan
\[
A_n=\frac{S_{N_n}-\mu N_n}{\sigma\sqrt n},
\qquad R_n=\frac{N_n}{n}.
\]
Pada \(\{N_n>0\}\),
\[
\widehat\mu_n-\mu
=\frac{\sigma A_n}{\sqrt n\,R_n}.
\]
Karena \(A_n\) ketat, \(R_n\to1\) dalam probabilitas, dan
\(\mathbb P(N_n=0)\to0\), ruas kanan menuju nol dalam probabilitas. Maka
\(\widehat\mu_n\to\mu\) dalam probabilitas. Selanjutnya,
\[
\frac{\sqrt{N_n}(\widehat\mu_n-\mu)}{\sigma}
=A_n\sqrt{\frac n{N_n}}
=A_nR_n^{-1/2}
\Rightarrow N(0,1)
\]
pada kejadian \(N_n>0\); konvensi pada kejadian nol tidak mengubah limit.

Untuk ukuran sampel deterministik \(m\), SLLN memberi konsistensi hampir
pasti dan CLT memberi pendekatan normal bagi fluktuasi skala \(\sqrt m\).
Jika ukuran sampel yang teramati adalah \(m>0\), independensi memberi
\[
\mathbb E(\overline Y_m-\mu)^2=\frac{\sigma^2}{m},
\]
sehingga galat baku teoretis rataan Monte Carlo adalah
\(\sigma/\sqrt m\); secara tipikal \(m\) dekat dengan \(n\). Hasil di atas
untuk \(N_n\) secara langsung membuktikan mode yang dinyatakan:
probabilitas untuk konsistensi dan distribusi untuk CLT. Penguatan hampir pasti
juga tersedia bila seluruh barisan ditempatkan pada satu ruang peluang: batas
Chernoff Poisson membuat
\(\sum_n\mathbb P(|N_n/n-1|>\varepsilon)<\infty\), sehingga
Borel--Cantelli memberi \(N_n/n\to1\) hampir pasti; SLLN kemudian berlaku pada
subbarisan acak \(N_n\). Penguatan ini memakai argumen tambahan, bukan semata
rantai implikasi dari konvergensi dalam probabilitas.
Simulasi dapat mengilustrasikan perilaku, tetapi tidak membuktikan kuantor
teorema atas semua ukuran sampel dan realisasi.

### Soal 2 — Disintegrasi segitiga dan komposisi kernel (13 poin) {#assessment.o009.d30.cumulative.form-b.problem.02}

Pada ruang Borel standar, \((X,Y)\) mempunyai kerapatan gabungan
\[
f(x,y)=2\mathbf1_{\{0<x<y<1\}}
\]
terhadap ukuran Lebesgue. Secara bersyarat pada \((X,Y)\), peubah
\(Z\in\{0,1\}\) dihasilkan oleh kernel Bernoulli
\[
\mathbb P(Z=1\mid X,Y)=Y;
\]
jadi kernel tersebut hanya bergantung pada \(Y\).

1. Hitung kerapatan marginal \(X\) dan bangun satu kernel reguler
   \(K(x,dy)\) untuk hukum \(Y\mid X=x\). **(3 poin)**
2. Verifikasi identitas disintegrasi untuk \(K\), lalu hitung
   \(\mathbb P(Z=1\mid X=x)\) melalui komposisi kernel dan periksa sifat
   menara bagi fungsi terbatas \(h:\{0,1\}\to\mathbb R\). **(4 poin)**
3. Berikan dua pilihan kernel yang berbeda di luar \((0,1)\), tetapi
   mewakili hukum bersyarat yang sama. Jelaskan ukuran yang menentukan kata
   “hampir di mana-mana”. **(2 poin)**
4. Jelaskan mengapa pemilihan versi
   \(\mathbb P(Y\in B\mid\mathcal G)\) secara terpisah untuk setiap \(B\)
   belum tentu membentuk ukuran pada setiap titik. Nyatakan peran sasaran
   Borel standar dan kelas penentu terhitung. **(4 poin)**

#### Rubrik Soal 2 {#assessment.o009.d30.cumulative.form-b.problem.02.rubric}

| Komponen | Poin |
|---|---:|
| Marginal dan kernel ternormalisasi | 3 |
| Disintegrasi, komposisi Bernoulli, dan sifat menara | 4 |
| Dua versi pada himpunan marginal nol | 2 |
| Koherensi ukuran, keberadaan, dan keunikan kernel | 4 |

#### Petunjuk 1 {#assessment.o009.d30.cumulative.form-b.problem.02.hint.01}

Integrasikan \(f(x,y)\) terhadap \(y\). Untuk \(0<x<1\), hukum bersyarat
adalah hukum seragam pada \((x,1)\).

#### Petunjuk 2 {#assessment.o009.d30.cumulative.form-b.problem.02.hint.02}

Gunakan
\[
\mathbb E[h(Z)\mid Y=y]=(1-y)h(0)+yh(1).
\]
Untuk keunikan umum, satukan himpunan nol hanya pada kelas penentu terhitung,
lalu gunakan ketunggalan ukuran.

#### Jawaban ringkas {#assessment.o009.d30.cumulative.form-b.problem.02.answer}

\[
f_X(x)=2(1-x)\mathbf1_{(0,1)}(x),\qquad
K(x,dy)=\frac{\mathbf1_{\{x<y<1\}}}{1-x}\,dy
\]
untuk \(0<x<1\). Komposisi memberi
\(\mathbb P(Z=1\mid X=x)=(1+x)/2\). Nilai \(K\) di luar dukungan \(X\)
bebas dipilih secara terukur dan semua pilihan tersebut sama
\(\mathbb P_X\)-hampir di mana-mana. Sasaran Borel standar memberi kernel
koheren; kelas penentu terhitung memberi satu himpunan nol bersama untuk
keunikan sebagai ukuran.

#### Penyelesaian lengkap {#assessment.o009.d30.cumulative.form-b.problem.02.solution}

Integrasi pada penampang \(x<y<1\) memberi
\[
f_X(x)=\int_x^1 2\,dy=2(1-x),
\qquad 0<x<1.
\]
Jadi satu versi kernel adalah
\[
K(x,A)=\frac{\lambda(A\cap(x,1))}{1-x},
\qquad 0<x<1,
\]
dan, misalnya, \(K(x,\cdot)=\delta_0\) di luar \((0,1)\). Untuk himpunan
Borel \(C,D\),
\[
\begin{aligned}
\int_C K(x,D)\,\mathbb P_X(dx)
&=\int_{C\cap(0,1)}
\frac{\lambda(D\cap(x,1))}{1-x}\,2(1-x)\,dx\\
&=\int_C\int_D2\mathbf1_{\{0<x<y<1\}}\,dy\,dx\\
&=\mathbb P(X\in C,Y\in D).
\end{aligned}
\]
Ini memverifikasi disintegrasi.

Komposisi dengan kernel Bernoulli memberi
\[
\mathbb P(Z=1\mid X=x)
=\int_x^1y\,\frac{dy}{1-x}
=\frac{1+x}{2}.
\]
Jika \(g(y)=(1-y)h(0)+yh(1)\), maka
\[
\begin{aligned}
\mathbb E[g(Y)\mid X=x]
&=h(0)\left(1-\frac{1+x}{2}\right)
 +h(1)\frac{1+x}{2},
\end{aligned}
\]
tepat nilai harapan \(h\) di bawah hukum Bernoulli dengan parameter
\((1+x)/2\). Jadi sifat menara berlaku.

Ganti pilihan di luar \((0,1)\) dari \(\delta_0\) menjadi, misalnya,
\(\delta_1\). Kedua kernel berbeda titik demi titik, tetapi himpunan tempat
mereka berbeda mempunyai ukuran \(\mathbb P_X\) nol. Karena disintegrasi
mengintegralkan terhadap \(\mathbb P_X\), keduanya mewakili hukum bersyarat
yang sama.

Untuk satu \(B\) tetap,
\(\mathbb E[\mathbf1_{\{Y\in B\}}\mid\mathcal G]\) hanya ditentukan modulo
himpunan nol yang dapat bergantung pada \(B\). Pilihan terpisah bagi tak
terhitung banyak \(B\) belum tentu aditif terhitung pada satu \(\omega\).
Pada sasaran Borel standar tersedia satu distribusi bersyarat reguler
\(K(\omega,\cdot)\) yang koheren. Jika dua kernel mewakili hukum yang sama,
samakan dahulu keduanya pada kelas penentu terhitung. Gabungan terhitung
himpunan nolnya tetap nol; di luar gabungan itu, ketunggalan ukuran
memperluas kesamaan ke seluruh aljabar-σ sasaran.

---

## Bagian II — Martingal dan penghentian {#assessment.o009.d30.cumulative.form-b.section.05}

### Soal 3 — Gerak acak bias, martingal eksponensial, dan waktu keluar (14 poin) {#assessment.o009.d30.cumulative.form-b.problem.03}

Misalkan \(0<p<1\), \(p\ne1/2\), \(q=1-p\), dan
\(\xi_1,\xi_2,\ldots\) i.i.d. dengan
\(\mathbb P(\xi_k=1)=p\) dan \(\mathbb P(\xi_k=-1)=q\).
Tetapkan \(S_0=0\), \(S_n=\sum_{k=1}^n\xi_k\), serta
\(\mathcal F_n=\sigma(\xi_1,\ldots,\xi_n)\). Untuk
\(a,b\in\mathbb N_{\ge1}\), definisikan
\[
\tau=\inf\{n\ge0:S_n\in\{-a,b\}\},
\qquad r=\frac qp.
\]

1. Buktikan \(M_n=r^{S_n}\) adalah martingal dan
   \((M_{n\wedge\tau})_{n\ge0}\) adalah martingal berhenti. **(3 poin)**
2. Buktikan \(\tau\) mempunyai ekor geometrik, tunjukkan keluarga
   \((M_{n\wedge\tau})_n\) terintegralkan seragam, lalu hitung
   \(u=\mathbb P(S_\tau=b)\). **(4 poin)**
3. Gunakan martingal
   \(S_n-(p-q)n\) untuk menghitung \(\mathbb E\tau\). Benarkan pelewatan
   limit. **(4 poin)**
4. Dengan SLLN, buktikan \(M_n\to0\) hampir pasti dan simpulkan bahwa
   martingal nonnegatif \((M_n)\) tidak terintegralkan seragam walaupun
   \(\mathbb EM_n=1\). **(3 poin)**

#### Rubrik Soal 3 {#assessment.o009.d30.cumulative.form-b.problem.03.rubric}

| Komponen | Poin |
|---|---:|
| Martingal eksponensial dan pembuktian martingal berhenti | 3 |
| Ekor geometrik, keterintegralan seragam, dan peluang batas atas | 4 |
| Martingal hanyutan dan nilai harapan waktu keluar | 4 |
| Limit hampir pasti dan diagnosis kegagalan UI | 3 |

#### Petunjuk 1 {#assessment.o009.d30.cumulative.form-b.problem.03.hint.01}

Periksa \(pr+qr^{-1}=1\). Untuk proses berhenti, tulis inkremennya sebagai
\(\mathbf1_{\{\tau>n\}}(M_{n+1}-M_n)\). Dari setiap keadaan interior, satu
urutan semua langkah ke kanan atau semua langkah ke kiri mencapai batas
dalam paling banyak \(a+b\) langkah.

#### Petunjuk 2 {#assessment.o009.d30.cumulative.form-b.problem.03.hint.02}

Gunakan
\[
1=\mathbb EM_\tau=ur^b+(1-u)r^{-a}.
\]
Untuk waktu rata-rata, hitung
\(\mathbb ES_\tau=bu-a(1-u)\). Untuk limit martingal tanpa penghentian,
periksa tanda \((p-q)\log(q/p)\).

#### Jawaban ringkas {#assessment.o009.d30.cumulative.form-b.problem.03.answer}

\[
u=\frac{1-r^a}{1-r^{a+b}},
\qquad
\mathbb E\tau=\frac{(a+b)u-a}{p-q}.
\]
Proses \(M_{n\wedge\tau}\) dibatasi seragam, sehingga merupakan martingal
terintegralkan seragam dan limit penghentiannya sah. Sebaliknya,
\((p-q)\log(q/p)<0\), sehingga \(M_n\to0\) hampir pasti sementara
\(\mathbb EM_n=1\); jadi \((M_n)\) tidak terintegralkan seragam.

#### Penyelesaian lengkap {#assessment.o009.d30.cumulative.form-b.problem.03.solution}

Karena \(\xi_{n+1}\) bebas dari \(\mathcal F_n\),
\[
\mathbb E(M_{n+1}\mid\mathcal F_n)
=r^{S_n}\mathbb E(r^{\xi_{n+1}})
=r^{S_n}(pr+qr^{-1})
=M_n.
\]
Jadi \(M\) martingal. Selanjutnya,
\[
M_{(n+1)\wedge\tau}-M_{n\wedge\tau}
=\mathbf1_{\{\tau>n\}}(M_{n+1}-M_n).
\]
Indikator itu \(\mathcal F_n\)-terukur, sehingga ekspektasi bersyarat
inkremennya nol. Maka \((M_{n\wedge\tau})_n\) martingal.

Ambil \(c=\min(p,q)^{a+b}>0\). Dari setiap keadaan interior, peluang mengikuti
urutan langkah yang mencapai salah satu batas dalam \(a+b\) langkah paling
sedikit \(c\). Dengan sifat Markov,
\[
\mathbb P(\tau>k(a+b))\le(1-c)^k.
\]
Jadi \(\tau<\infty\) hampir pasti dan \(\mathbb E\tau<\infty\). Sebelum dan
pada waktu keluar, \(S_{n\wedge\tau}\in[-a,b]\). Karena himpunan ini
berhingga, \(M_{n\wedge\tau}\) dibatasi oleh konstanta deterministik; keluarga
tersebut terintegralkan seragam. Maka
\[
1=\mathbb EM_0=\mathbb EM_\tau
=ur^b+(1-u)r^{-a}.
\]
Penyelesaian memberi
\[
u=\frac{1-r^{-a}}{r^b-r^{-a}}
=\frac{1-r^a}{1-r^{a+b}}.
\]

Proses \(L_n=S_n-(p-q)n\) adalah martingal karena
\(\mathbb E\xi_{n+1}=p-q\). Penghentian pada \(\tau\wedge n\) memberi
\[
\mathbb ES_{\tau\wedge n}=(p-q)\mathbb E(\tau\wedge n).
\]
Ruas kiri menuju \(\mathbb ES_\tau\) dengan konvergensi terdominasi karena
\(|S_{\tau\wedge n}|\le\max(a,b)\); ruas kanan menuju
\((p-q)\mathbb E\tau\) dengan konvergensi monoton. Karena
\[
\mathbb ES_\tau=bu-a(1-u)=(a+b)u-a,
\]
diperoleh
\[
\mathbb E\tau=\frac{(a+b)u-a}{p-q}.
\]
Pembilang dan penyebut mempunyai tanda sama, sehingga hasilnya positif.

SLLN memberi \(S_n/n\to p-q\) hampir pasti. Karena
\[
\frac1n\log M_n=\frac{S_n}{n}\log(q/p)
\longrightarrow(p-q)\log(q/p)<0,
\]
maka \(M_n\to0\) hampir pasti. Namun sifat martingal memberi
\(\mathbb EM_n=1\) untuk semua \(n\). Jika \((M_n)\) terintegralkan seragam,
Vitali akan memberi konvergensi \(L^1\) ke nol dan memaksa
\(\mathbb EM_n\to0\), suatu kontradiksi. Jadi keterbatasan \(L^1\) melalui
rataan satu tidak cukup untuk UI.

---

## Bagian III — Markov, CTMC, dan Poisson {#assessment.o009.d30.cumulative.form-b.section.06}

### Soal 4 — Rantai periodik tiga kelas siklik (12 poin) {#assessment.o009.d30.cumulative.form-b.problem.04}

Pada ruang keadaan \(E=\{0,1,2,3\}\), pertimbangkan rantai Markov homogen
dengan
\[
P=
\begin{pmatrix}
0&\tfrac12&\tfrac12&0\\
0&0&0&1\\
0&0&0&1\\
1&0&0&0
\end{pmatrix}.
\]

1. Hitung \(P^2\) dan tunjukkan bahwa rantai tak tereduksi. **(3 poin)**
2. Tentukan periode semua keadaan dengan dekomposisi kelas siklik.
   **(2 poin)**
3. Tentukan distribusi stasioner tunggal \(\pi\). **(3 poin)**
4. Jika \(X_0=0\), tentukan tiga limit subsekuens
   \(\mathcal L(X_{3n+j})\), \(j=0,1,2\), dan limit Cesàro hukum waktu.
   Jelaskan mengapa hukum waktu biasa tidak konvergen. **(4 poin)**

#### Rubrik Soal 4 {#assessment.o009.d30.cumulative.form-b.problem.04.rubric}

| Komponen | Poin |
|---|---:|
| \(P^2\) dan komunikasi seluruh keadaan | 3 |
| Periode tiga dan kelas siklik | 2 |
| Persamaan invarian dan normalisasi | 3 |
| Tiga limit subsekuens, limit Cesàro, dan diagnosis periodisitas | 4 |

#### Petunjuk 1 {#assessment.o009.d30.cumulative.form-b.problem.04.hint.01}

Gunakan kelas siklik
\(\{0\}\to\{1,2\}\to\{3\}\to\{0\}\). Waktu kembali harus merupakan
kelipatan tiga, dan kembali dalam tiga langkah mempunyai peluang positif.

#### Petunjuk 2 {#assessment.o009.d30.cumulative.form-b.problem.04.hint.02}

Dari \(0\), hukum pada tiga waktu pertama adalah
\(\delta_0\), \((0,1/2,1/2,0)\), dan \(\delta_3\); pola itu berulang.

#### Jawaban ringkas {#assessment.o009.d30.cumulative.form-b.problem.04.answer}

\[
P^2=
\begin{pmatrix}
0&0&0&1\\
1&0&0&0\\
1&0&0&0\\
0&\tfrac12&\tfrac12&0
\end{pmatrix}.
\]
Rantai tak tereduksi dan berperiode tiga. Distribusi stasionernya
\(\pi=(1/3,1/6,1/6,1/3)\). Dari \(0\), tiga hukum subsekuens berturut-turut
adalah \(\delta_0\), \((0,1/2,1/2,0)\), dan \(\delta_3\); rata-rata Cesàro
menuju \(\pi\), tetapi hukum biasa berosilasi.

#### Penyelesaian lengkap {#assessment.o009.d30.cumulative.form-b.problem.04.solution}

Perkalian langsung memberi
\[
P^2=
\begin{pmatrix}
0&0&0&1\\
1&0&0&0\\
1&0&0&0\\
0&\tfrac12&\tfrac12&0
\end{pmatrix}.
\]
Dari \(0\) rantai mencapai \(1\) dan \(2\); keduanya mencapai \(3\), lalu
\(3\) mencapai \(0\). Jadi setiap keadaan dapat mencapai semua keadaan lain,
sehingga rantai tak tereduksi.

Transisi selalu bergerak melalui tiga kelas
\[
C_0=\{0\},\qquad C_1=\{1,2\},\qquad C_2=\{3\}
\]
secara siklik. Waktu kembali harus habis dibagi tiga. Kembali dalam tiga
langkah mempunyai peluang positif dari setiap keadaan, sehingga gcd waktu
kembali adalah tiga dan semua keadaan berperiode tiga.

Jika \(\pi=(\pi_0,\pi_1,\pi_2,\pi_3)\), persamaan \(\pi P=\pi\) memberi
\[
\pi_1=\tfrac12\pi_0,\quad
\pi_2=\tfrac12\pi_0,\quad
\pi_3=\pi_1+\pi_2=\pi_0,\quad
\pi_0=\pi_3.
\]
Normalisasi menghasilkan
\[
\pi=(\tfrac13,\tfrac16,\tfrac16,\tfrac13).
\]

Karena \(P^3\) membawa \(\delta_0\) kembali ke \(\delta_0\), untuk setiap
\(n\ge0\),
\[
\mathcal L(X_{3n})=\delta_0,\quad
\mathcal L(X_{3n+1})=(0,\tfrac12,\tfrac12,0),\quad
\mathcal L(X_{3n+2})=\delta_3.
\]
Ketiga limit berbeda, sehingga tidak ada limit waktu biasa. Masing-masing
kelas residu mempunyai frekuensi asimtotik \(1/3\); karena itu
\[
\frac1N\sum_{k=0}^{N-1}\mathcal L(X_k)
\longrightarrow
\tfrac13\delta_0
+\tfrac13(0,\tfrac12,\tfrac12,0)
+\tfrac13\delta_3
=\pi.
\]
Ketunggalan distribusi stasioner tidak menghapus osilasi akibat
periodisitas.

### Soal 5 — CTMC tiga keadaan dan uniformisasi Poisson (13 poin) {#assessment.o009.d30.cumulative.form-b.problem.05}

Sebuah CTMC pada \(E=\{0,1,2\}\) mempunyai generator
\[
Q=\lambda
\begin{pmatrix}
-1&1&0\\
1&-2&1\\
0&1&-1
\end{pmatrix},
\qquad \lambda>0.
\]

1. Tentukan laju keluar, hukum waktu tunggu, dan rantai lompatan tertanam.
   Buktikan proses tidak meledak. **(3 poin)**
2. Dengan vektor eigen
   \((1,1,1)\), \((1,0,-1)\), dan \((1,-2,1)\), hitung
   \(P_t=e^{tQ}\) secara eksplisit. **(4 poin)**
3. Tentukan distribusi invarian dan limit \(P_t\). Jelaskan mengapa
   kesimpulan ketidakmeledakan ini tidak mengikuti dari setiap matriks
   intensitas formal pada ruang keadaan tak hingga. **(3 poin)**
4. Ambil
   \(R=I+Q/(2\lambda)\). Buktikan
   \[
   P_t=e^{-2\lambda t}
   \sum_{n=0}^{\infty}\frac{(2\lambda t)^n}{n!}R^n
   \]
   dan tafsirkan rumus tersebut dengan jam Poisson. **(3 poin)**

#### Rubrik Soal 5 {#assessment.o009.d30.cumulative.form-b.problem.05.rubric}

| Komponen | Poin |
|---|---:|
| Laju, waktu tunggu, rantai tertanam, dan ketidakmeledakan | 3 |
| Dekomposisi spektral dan semigrup eksplisit | 4 |
| Invariansi, limit, serta audit ruang keadaan tak hingga | 3 |
| Uniformisasi dan interpretasi jam Poisson | 3 |

#### Petunjuk 1 {#assessment.o009.d30.cumulative.form-b.problem.05.hint.01}

Ketiga nilai eigen \(Q\) adalah \(0,-\lambda,-3\lambda\). Vektor yang
diberikan saling ortogonal dengan kuadrat norma \(3,2,6\).

#### Petunjuk 2 {#assessment.o009.d30.cumulative.form-b.problem.05.hint.02}

Karena \(Q=2\lambda(R-I)\), pisahkan dua eksponensial matriks yang saling
komutatif. Periksa bahwa \(R\) stokastik; lompatan semu boleh berupa
tinggal di keadaan yang sama.

#### Jawaban ringkas {#assessment.o009.d30.cumulative.form-b.problem.05.answer}

Laju keluar di \(0,1,2\) adalah \(\lambda,2\lambda,\lambda\), dan rantai
tertanam bergerak \(0\to1\), \(2\to1\), serta dari \(1\) ke \(0\) atau \(2\)
dengan peluang \(1/2\). Jika \(x=e^{-\lambda t}\) dan
\(y=e^{-3\lambda t}\), maka
\[
P_t=
\begin{pmatrix}
\frac13+\frac x2+\frac y6&\frac13-\frac y3&\frac13-\frac x2+\frac y6\\
\frac13-\frac y3&\frac13+\frac{2y}3&\frac13-\frac y3\\
\frac13-\frac x2+\frac y6&\frac13-\frac y3&\frac13+\frac x2+\frac y6
\end{pmatrix}.
\]
Distribusi invarian adalah seragam dan setiap baris menuju seragam.
Uniformisasi memakai jam Poisson berlaju \(2\lambda\) dan matriks langkah
\(R\).

#### Penyelesaian lengkap {#assessment.o009.d30.cumulative.form-b.problem.05.solution}

Laju keluar adalah \(-q_{ii}\). Jadi waktu tunggu di \(0\) dan \(2\)
berdistribusi \(\operatorname{Exp}(\lambda)\), sedangkan di \(1\)
berdistribusi \(\operatorname{Exp}(2\lambda)\). Setelah meninggalkan \(0\)
atau \(2\), proses pasti menuju \(1\); setelah meninggalkan \(1\), ia menuju
\(0\) atau \(2\) dengan peluang sama. Semua laju keluar dibatasi di atas oleh
\(2\lambda\). Uniformisasi, atau dominasi jumlah lompatan oleh proses Poisson
berlaju \(2\lambda\), menunjukkan bahwa jumlah lompatan pada selang waktu
terbatas hampir pasti berhingga.

Normalisasi proyeksi ortogonal pada ketiga ruang eigen memberi
\[
P_t=
\frac13
\begin{pmatrix}1&1&1\\1&1&1\\1&1&1\end{pmatrix}
+\frac{x}{2}
\begin{pmatrix}1&0&-1\\0&0&0\\-1&0&1\end{pmatrix}
+\frac{y}{6}
\begin{pmatrix}1&-2&1\\-2&4&-2\\1&-2&1\end{pmatrix},
\]
dengan \(x=e^{-\lambda t}\) dan \(y=e^{-3\lambda t}\). Jadi
\[
P_t=
\begin{pmatrix}
\frac13+\frac x2+\frac y6&\frac13-\frac y3&\frac13-\frac x2+\frac y6\\
\frac13-\frac y3&\frac13+\frac{2y}3&\frac13-\frac y3\\
\frac13-\frac x2+\frac y6&\frac13-\frac y3&\frac13+\frac x2+\frac y6
\end{pmatrix}.
\]
Pada \(t=0\), matriks ini adalah \(I\), dan turunannya di nol adalah \(Q\).
Karena dibangun sebagai \(e^{tQ}\), ia memenuhi persamaan Kolmogorov dan
sifat semigrup.

Matriks \(Q\) simetris dan jumlah setiap kolomnya nol, sehingga
\[
\pi=(\tfrac13,\tfrac13,\tfrac13)
\]
memenuhi \(\pi Q=0\). Ketika \(t\to\infty\), \(x,y\to0\) dan setiap baris
\(P_t\) menuju \(\pi\). Bukti ketidakmeledakan di atas bergantung pada batas
seragam laju keluar. Pada ruang keadaan tak hingga, laju dapat tak terbatas
dan waktu tunggu dapat berakumulasi dalam waktu berhingga. Karena itu matriks
intensitas formal belum menjamin proses konservatif, ketidakmeledakan, domain
operator yang sesuai, atau keunikan kelas solusi.

Perhitungan langsung memberi
\[
R=I+\frac{Q}{2\lambda}
=
\begin{pmatrix}
\tfrac12&\tfrac12&0\\
\tfrac12&0&\tfrac12\\
0&\tfrac12&\tfrac12
\end{pmatrix},
\]
sebuah matriks stokastik. Karena \(Q=2\lambda(R-I)\),
\[
\begin{aligned}
e^{tQ}
&=e^{2\lambda t(R-I)}
=e^{-2\lambda t}e^{2\lambda tR}\\
&=e^{-2\lambda t}
\sum_{n=0}^{\infty}\frac{(2\lambda t)^n}{n!}R^n.
\end{aligned}
\]
Artinya, jam Poisson berlaju \(2\lambda\) menghasilkan calon waktu lompatan;
pada setiap calon waktu, keadaan diperbarui menurut \(R\). Di keadaan ujung,
sebagian calon lompatan adalah lompatan semu yang mempertahankan keadaan.

### Soal 6 — Lokasi bersyarat, penandaan, dan superposisi Poisson (10 poin) {#assessment.o009.d30.cumulative.form-b.problem.06}

Misalkan \(N\) adalah ukuran acak Poisson pada \((E,\mathcal E)\) dengan
ukuran intensitas σ-terhingga \(\nu\). Ambil
\(A\in\mathcal E\) dengan \(0<\nu(A)<\infty\), dan partisi terukur
\(A=A_1\sqcup\cdots\sqcup A_k\). Bersyarat pada \(N\), setiap atom yang
terletak di \(x\) ditandai merah secara independen dengan probabilitas
\(p(x)\), dengan \(p:E\to[0,1]\) terukur, dan ditandai biru selainnya.

1. Turunkan fungsional Laplace \(N\) dan gunakan untuk menghitung
   \(\mathbb EN(A)\) serta \(\operatorname{Var}N(A)\). **(3 poin)**
2. Buktikan bahwa, bersyarat pada \(N(A)=m\), lokasi \(m\) titik bersifat
   i.i.d. dengan hukum \(\nu(\cdot\cap A)/\nu(A)\). Turunkan hukum
   multinomial vektor \((N(A_1),\ldots,N(A_k))\). **(3 poin)**
3. Buktikan ukuran merah dan biru independen dengan intensitas
   \(p\nu\) dan \((1-p)\nu\). Jika \(\widetilde N\) adalah ukuran acak
   Poisson independen berintensitas \(\eta\), buktikan
   \(N+\widetilde N\) berintensitas \(\nu+\eta\). **(3 poin)**
4. Nyatakan nilai \(N(C)\) hampir pasti bila \(\nu(C)=\infty\), dan
   kualifikasikan istilah “hingga secara lokal”. **(1 poin)**

#### Rubrik Soal 6 {#assessment.o009.d30.cumulative.form-b.problem.06.rubric}

| Komponen | Poin |
|---|---:|
| Fungsional Laplace dan dua momen | 3 |
| Hukum lokasi bersyarat dan multinomial | 3 |
| Penandaan independen dan superposisi | 3 |
| Intensitas tak hingga dan syarat lokal | 1 |

#### Petunjuk 1 {#assessment.o009.d30.cumulative.form-b.problem.06.hint.01}

Untuk \(f\ge0\),
\[
\mathbb E e^{-\int f\,dN}
=\exp\!\left\{-\int(1-e^{-f})\,d\nu\right\}.
\]
Bersyarat pada jumlah total \(m\), bandingkan peluang hitungan partisi dengan
peluang Poisson independen sebelum pengondisian.

#### Petunjuk 2 {#assessment.o009.d30.cumulative.form-b.problem.06.hint.02}

Satu titik di \(x\) menyumbang
\(p(x)e^{-f(x)}+(1-p(x))e^{-g(x)}\) pada fungsional Laplace bersama.
Untuk superposisi, gunakan independensi untuk mengalikan dua fungsional
Laplace.

#### Jawaban ringkas {#assessment.o009.d30.cumulative.form-b.problem.06.answer}

\[
\mathbb E e^{-\int f\,dN}
=\exp\!\left\{-\int(1-e^{-f})\,d\nu\right\},
\qquad
\mathbb EN(A)=\operatorname{Var}N(A)=\nu(A).
\]
Bersyarat pada \(N(A)=m\), lokasi i.i.d. menurut
\(\nu(\cdot\cap A)/\nu(A)\), sehingga hitungan partisi multinomial dengan
peluang \(\nu(A_j)/\nu(A)\). Penandaan memberi dua ukuran acak Poisson
independen berintensitas \(p\nu\) dan \((1-p)\nu\); superposisi independen
menjumlahkan intensitas. Jika \(\nu(C)=\infty\), maka \(N(C)=\infty\) hampir
pasti.

#### Penyelesaian lengkap {#assessment.o009.d30.cumulative.form-b.problem.06.solution}

Karena \(\nu\) σ-terhingga, pilih \(E_1\subseteq E_2\subseteq\cdots\uparrow E\)
dengan \(\nu(E_r)<\infty\). Mula-mula ambil fungsi sederhana nonnegatif
\(f=\sum_jc_j\mathbf1_{C_j}\) yang didukung oleh suatu \(E_r\), dengan
himpunan \(C_j\) saling lepas; khususnya \(\nu(C_j)<\infty\). Independensi
hitungan Poisson memberi
\[
\begin{aligned}
\mathbb E e^{-\int f\,dN}
&=\prod_j
\mathbb E e^{-c_jN(C_j)}\\
&=\exp\!\left\{
-\sum_j(1-e^{-c_j})\nu(C_j)
\right\}\\
&=\exp\!\left\{-\int(1-e^{-f})\,d\nu\right\}.
\end{aligned}
\]
Untuk \(f\ge0\) terukur yang sebarang, aproksimasikan \(f\) dari bawah oleh
fungsi sederhana yang dipotong pada \(E_r\). Konvergensi monoton pada integral
dan konvergensi terbatas pada ekspektasi memperluas rumus tersebut ke semua
\(f\ge0\), termasuk ketika ruas kanan bernilai nol karena eksponennya tak
hingga. Untuk \(a=\nu(A)<\infty\), transformasi Laplace
\[
L_A(t)=\mathbb E e^{-tN(A)}=\exp\{-a(1-e^{-t})\}
\]
memenuhi \(L_A'(0)=-a\) dan \(L_A''(0)=a+a^2\). Karena
\(\mathbb EN(A)=-L_A'(0)\) dan \(\mathbb E[N(A)^2]=L_A''(0)\), diperoleh
\(\mathbb EN(A)=a\) dan
\(\operatorname{Var}N(A)=a+a^2-a^2=a\).

Untuk bilangan bulat taknegatif \(m_1,\ldots,m_k\) dengan
\(\sum_jm_j=m\), independensi sebelum pengondisian memberi
\[
\begin{aligned}
&\mathbb P\!\left(
N(A_j)=m_j,\ 1\le j\le k\mid N(A)=m
\right)\\
&\quad=
\frac{m!}{m_1!\cdots m_k!}
\prod_{j=1}^k
\left(\frac{\nu(A_j)}{\nu(A)}\right)^{m_j}.
\end{aligned}
\]
Ini adalah hukum multinomial dan sama dengan hukum hitungan dari \(m\)
lokasi i.i.d. yang masing-masing mempunyai distribusi
\(\nu(\cdot\cap A)/\nu(A)\). Identitas pada semua partisi berhingga
menentukan hukum lokasi bersyarat tersebut.

Tuliskan \(N_R,N_B\) untuk ukuran merah dan biru. Untuk \(f,g\ge0\), rumus
eksponensial Poisson memberi
\[
\begin{aligned}
&\mathbb E\exp\!\left\{-\int f\,dN_R-\int g\,dN_B\right\}\\
&\quad=
\exp\!\left[
-\int\{1-pe^{-f}-(1-p)e^{-g}\}\,d\nu
\right]\\
&\quad=
\exp\!\left\{-\int(1-e^{-f})p\,d\nu\right\}
\exp\!\left\{-\int(1-e^{-g})(1-p)\,d\nu\right\}.
\end{aligned}
\]
Faktorisasi membuktikan independensi dan mengidentifikasi intensitas
\(p\nu\) serta \((1-p)\nu\). Jika \(\widetilde N\) independen dari \(N\),
\[
\begin{aligned}
\mathbb E e^{-\int f\,d(N+\widetilde N)}
&=\mathbb E e^{-\int f\,dN}
  \mathbb E e^{-\int f\,d\widetilde N}\\
&=\exp\!\left\{-\int(1-e^{-f})\,d(\nu+\eta)\right\},
\end{aligned}
\]
sehingga superposisinya merupakan ukuran acak Poisson berintensitas
\(\nu+\eta\).

Jika \(\nu(C)=\infty\), pilih \(C_m\uparrow C\) dengan
\(\nu(C_m)<\infty\) dan \(\nu(C_m)\to\infty\). Untuk setiap \(K\),
\[
\mathbb P(N(C)\le K)
\le\mathbb P(N(C_m)\le K)\longrightarrow0.
\]
Jadi \(N(C)=\infty\) hampir pasti. “Hingga secara lokal” hanya bermakna
setelah kelas lokal—misalnya himpunan relatif kompak—ditentukan, dan
memerlukan \(\nu\) hingga pada kelas itu.

---

## Bagian IV — Gerak Brown dan hukum lintasan {#assessment.o009.d30.cumulative.form-b.section.07}

### Soal 7 — Gerak Brown dengan hanyutan dan transformasi waktu kena (14 poin) {#assessment.o009.d30.cumulative.form-b.problem.07}

Misalkan \(B=(B_t)_{t\ge0}\) gerak Brown standar,
\[
X_t=B_t+\mu t,\qquad
\tau_a=\inf\{t\ge0:X_t=a\},
\]
dengan \(a>0\). Ambil \(0<s<t\).

1. Tentukan hukum Gaussian bersama \((X_s,X_t)\), termasuk vektor rataan,
   matriks kovarians, dan hukum \(X_t\mid X_s=x\). **(4 poin)**
2. Untuk \(r\in\mathbb R\), buktikan
   \[
   M_t(r)=\exp\{rX_t-(\mu r+r^2/2)t\}
   \]
   adalah martingal terhadap filtrasi alami Brown yang dilengkapi dan
   kontinu kanan. **(3 poin)**
3. Untuk \(\lambda\ge0\), tentukan
   \(\mathbb E[e^{-\lambda\tau_a};\tau_a<\infty]\), lalu turunkan
   \(\mathbb P(\tau_a<\infty)\). Berikan batas eksplisit bagi suku sisa
   pada penghentian. **(4 poin)**
4. Buktikan \(c^{-1/2}B_{ct}\) adalah gerak Brown standar untuk \(c>0\).
   Untuk \(\mu=0\), turunkan
   \(T_a\overset d=a^2T_1\) dan, dengan prinsip refleksi,
   \[
   \mathbb P\!\left(\sup_{0\le u\le t}B_u\ge a\right)
   =2\left[1-\Phi\!\left(\frac a{\sqrt t}\right)\right].
   \]
   **(3 poin)**

#### Rubrik Soal 7 {#assessment.o009.d30.cumulative.form-b.problem.07.rubric}

| Komponen | Poin |
|---|---:|
| Hukum Gaussian bersama dan bersyarat | 4 |
| Martingal eksponensial dengan ekspektasi bersyarat | 3 |
| Transformasi Laplace, batas sisa, dan peluang pencapaian | 4 |
| Penskalaan Brown, waktu kena, dan hukum maksimum | 3 |

#### Petunjuk 1 {#assessment.o009.d30.cumulative.form-b.problem.07.hint.01}

Gunakan \(X_t=X_s+\mu(t-s)+(B_t-B_s)\). Untuk transformasi Laplace, pilih
\[
r=-\mu+\sqrt{\mu^2+2\lambda},
\]
sehingga \(\mu r+r^2/2=\lambda\).

#### Petunjuk 2 {#assessment.o009.d30.cumulative.form-b.problem.07.hint.02}

Pada \(\{\tau_a>n\}\), kontinuitas memberi \(X_n<a\). Karena \(r\ge0\),
\[
0\le\mathbb E[M_n(r);\tau_a>n]\le e^{ra-\lambda n}
\]
ketika \(\lambda>0\). Untuk penskalaan, periksa kontinuitas, Gaussianitas,
inkremen stasioner, dan independensi inkremen.

#### Jawaban ringkas {#assessment.o009.d30.cumulative.form-b.problem.07.answer}

\[
(X_s,X_t)\sim N\!\left(
\binom{\mu s}{\mu t},
\begin{pmatrix}s&s\\s&t\end{pmatrix}
\right),
\qquad
X_t\mid X_s=x\sim N(x+\mu(t-s),t-s).
\]
Proses \(M(r)\) adalah martingal, dan
\[
\mathbb E[e^{-\lambda\tau_a};\tau_a<\infty]
=\exp\!\left\{a\left(\mu-\sqrt{\mu^2+2\lambda}\right)\right\}.
\]
Peluang pencapaian adalah satu untuk \(\mu\ge0\) dan \(e^{2\mu a}\) untuk
\(\mu<0\). Penskalaan Brown memberi \(T_a\overset d=a^2T_1\), sedangkan
prinsip refleksi memberi hukum maksimum yang dinyatakan.

#### Penyelesaian lengkap {#assessment.o009.d30.cumulative.form-b.problem.07.solution}

Vektor \((X_s,X_t)\) Gaussian dengan rataan
\((\mu s,\mu t)\). Karena
\(\operatorname{Cov}(B_s,B_t)=s\),
\[
\operatorname{Cov}(X_s,X_t)
=
\begin{pmatrix}
s&s\\
s&t
\end{pmatrix}.
\]
Identitas
\[
X_t=X_s+\mu(t-s)+(B_t-B_s)
\]
dan kebebasan \(B_t-B_s\) dari \(\mathcal F_s\) memberi
\[
X_t\mid X_s=x\sim N(x+\mu(t-s),t-s).
\]

Karena
\[
M_t(r)=\exp\{rB_t-r^2t/2\},
\]
untuk \(u<t\),
\[
\frac{M_t(r)}{M_u(r)}
=\exp\{r(B_t-B_u)-r^2(t-u)/2\}.
\]
Faktor ini bebas dari \(\mathcal F_u\) dan mempunyai rataan satu menurut
fungsi pembangkit momen normal. Jadi
\(\mathbb E[M_t(r)\mid\mathcal F_u]=M_u(r)\).

Untuk \(\lambda>0\), ambil
\[
r=-\mu+\sqrt{\mu^2+2\lambda}>0.
\]
Penghentian pada \(\tau_a\wedge n\) sah karena waktunya terbatas dan peubah
berhenti dibatasi oleh \(e^{ra}\). Maka
\[
1=
\mathbb E[e^{ra-\lambda\tau_a};\tau_a\le n]
+\mathbb E[M_n(r);\tau_a>n].
\]
Pada kejadian \(\{\tau_a>n\}\), berlaku \(X_n<a\), sehingga
\[
0\le\mathbb E[M_n(r);\tau_a>n]
\le e^{ra-\lambda n}\longrightarrow0.
\]
Konvergensi monoton pada suku pencapaian memberi
\[
\mathbb E[e^{-\lambda\tau_a};\tau_a<\infty]
=e^{-ra}
=\exp\!\left\{
a\left(\mu-\sqrt{\mu^2+2\lambda}\right)
\right\}.
\]
Membiarkan \(\lambda\downarrow0\), sekali lagi dengan konvergensi monoton,
memberi
\[
\mathbb P(\tau_a<\infty)
=
\begin{cases}
1,&\mu\ge0,\\
e^{2\mu a},&\mu<0.
\end{cases}
\]

Untuk \(W_t=c^{-1/2}B_{ct}\), lintasan kontinu, \(W_0=0\), dan
\[
W_t-W_s=c^{-1/2}(B_{ct}-B_{cs})\sim N(0,t-s).
\]
Inkremen pada selang terpisah tetap independen. Jadi \(W\) memenuhi
karakterisasi gerak Brown standar. Untuk \(\mu=0\),
\[
T_a=\inf\{t:B_t=a\}
\overset d=
a^2\inf\{u:a^{-1}B_{a^2u}=1\}
=a^2T_1.
\]
Kontinuitas lintasan dan prinsip refleksi selanjutnya memberi
\[
\begin{aligned}
\mathbb P\!\left(\sup_{0\le u\le t}B_u\ge a\right)
&=\mathbb P(T_a\le t)\\
&=2\mathbb P(B_t\ge a)
=2\left[1-\Phi\!\left(\frac a{\sqrt t}\right)\right].
\end{aligned}
\]

### Soal 8 — Jembatan Brown dan puncak deterministik bergerak (10 poin) {#assessment.o009.d30.cumulative.form-b.problem.08}

Definisikan
\[
\beta_t=B_t-tB_1,\qquad 0\le t\le1.
\]
Untuk \(n\ge2\), definisikan pula fungsi deterministik kontinu
\[
z_n(t)=\bigl(1-n|t-1/n|\bigr)_+,\qquad 0\le t\le1.
\]

1. Buktikan \(\beta\) Gaussian terpusat dengan kovarians
   \(K(u,v)=\min(u,v)-uv\), serta buktikan \(\beta\) bebas dari \(B_1\).
   Jelaskan hubungannya dengan satu versi hukum \(B\mid B_1=0\). **(4 poin)**
2. Untuk \(0<s<t<1\), tentukan hukum
   \(\beta_t\mid\beta_s=x\). **(2 poin)**
3. Buktikan semua distribusi berdimensi hingga \(z_n\) konvergen ke proses
   nol, tetapi \(\delta_{z_n}\) tidak konvergen lemah ke \(\delta_0\) dalam
   \(C[0,1]\). Buktikan secara eksplisit bahwa keluarga tersebut tidak
   ketat. **(3 poin)**
4. Nyatakan dua gerbang yang diperlukan untuk menaikkan CLT berdimensi
   hingga gerak acak menjadi teorema Donsker pada ruang lintasan.
   **(1 poin)**

#### Rubrik Soal 8 {#assessment.o009.d30.cumulative.form-b.problem.08.rubric}

| Komponen | Poin |
|---|---:|
| Gaussianitas, kovarians, independensi, dan versi jembatan | 4 |
| Hukum Gaussian bersyarat jembatan | 2 |
| FDD, kegagalan norma supremum, dan bukti tidak ketat | 3 |
| Topologi lintasan dan keketatan untuk Donsker | 1 |

#### Petunjuk 1 {#assessment.o009.d30.cumulative.form-b.problem.08.hint.01}

Hitung \(K(s,s)\), \(K(t,t)\), dan \(K(s,t)\). Kovarians
\(\operatorname{Cov}(\beta_t,B_1)\) adalah nol; gunakan Gaussianitas bersama.

#### Petunjuk 2 {#assessment.o009.d30.cumulative.form-b.problem.08.hint.02}

Untuk setiap \(t\) tetap, \(z_n(t)\) akhirnya nol, tetapi
\(\|z_n\|_\infty=1\). Jika \(1/n\le\delta\), bandingkan nilai pada \(0\) dan
\(1/n\) dalam modulus kontinuitas \(w(z_n,\delta)\).

#### Jawaban ringkas {#assessment.o009.d30.cumulative.form-b.problem.08.answer}

\(\beta\) Gaussian terpusat dengan kovarians
\(\min(u,v)-uv\) dan bebas dari \(B_1\); karena itu hukumnya merupakan versi
alami hukum lintasan Brown bersyarat pada \(B_1=0\). Untuk \(s<t\),
\[
\beta_t\mid\beta_s=x
\sim
N\!\left(
\frac{1-t}{1-s}x,\,
\frac{(t-s)(1-t)}{1-s}
\right).
\]
Semua FDD \(z_n\) menuju nol, tetapi norma supremumnya tetap satu dan
modulus kontinuitasnya gagal seragam, sehingga hukum lintasannya tidak ketat.
Donsker memerlukan topologi ruang lintasan yang dinyatakan serta keketatan,
selain konvergensi FDD.

#### Penyelesaian lengkap {#assessment.o009.d30.cumulative.form-b.problem.08.solution}

Setiap vektor nilai \(\beta\) adalah transformasi linear vektor Gaussian dari
\(B\), sehingga Gaussian dan memiliki rataan nol. Untuk \(u,v\in[0,1]\),
\[
\begin{aligned}
\operatorname{Cov}(\beta_u,\beta_v)
&=\operatorname{Cov}(B_u-uB_1,B_v-vB_1)\\
&=\min(u,v)-uv.
\end{aligned}
\]
Selain itu,
\[
\operatorname{Cov}(\beta_t,B_1)=t-t=0.
\]
Setiap vektor berdimensi hingga dari \(\beta\) karena itu bebas dari \(B_1\).
Karena ruang \(C[0,1]\) separabel dan sigma-aljabar Borelnya dihasilkan oleh
evaluasi pada himpunan waktu rapat terhitung, \(\beta\) sebagai peubah acak
bernilai lintasan bebas dari \(B_1\). Identitas
\[
B_t=tB_1+\beta_t
\]
menunjukkan bahwa hukum \(t\mapsto ty+\beta_t\) adalah satu kernel reguler
bagi \(B\mid B_1=y\). Pada \(y=0\) kernel itu adalah hukum jembatan.
Karena \(\mathbb P(B_1=0)=0\), nilai tersebut merupakan pilihan versi alami
yang dipilih oleh kontinuitas kernel dalam \(y\).

Untuk \(0<s<t<1\),
\[
K(s,s)=s(1-s),\quad
K(t,t)=t(1-t),\quad
K(s,t)=s(1-t).
\]
Rumus kondisional Gaussian memberi
\[
\mathbb E(\beta_t\mid\beta_s=x)
=\frac{s(1-t)}{s(1-s)}x
=\frac{1-t}{1-s}x
\]
dan
\[
\begin{aligned}
\operatorname{Var}(\beta_t\mid\beta_s)
&=t(1-t)
-\frac{s^2(1-t)^2}{s(1-s)}\\
&=\frac{(t-s)(1-t)}{1-s}.
\end{aligned}
\]

Untuk \(t=0\), \(z_n(0)=0\). Jika \(t>0\) tetap, maka untuk semua \(n\)
cukup besar berlaku \(t>2/n\), sehingga
\(|t-1/n|>1/n\) dan \(z_n(t)=0\). Jadi untuk setiap keluarga waktu hingga,
vektor nilainya akhirnya tepat nol; seluruh FDD menuju proses nol. Namun
\[
\|z_n\|_\infty=z_n(1/n)=1.
\]
Jika \(\delta_{z_n}\Rightarrow\delta_0\) dalam \(C[0,1]\), pemetaan kontinu
\(f\mapsto\|f\|_\infty\) akan memaksa
\(\|z_n\|_\infty\to0\), suatu kontradiksi. Lebih kuat, untuk setiap
\(\delta>0\) dan \(n\) cukup besar dengan \(1/n\le\delta\),
\[
w(z_n,\delta)
\ge|z_n(1/n)-z_n(0)|=1.
\]
Kriteria Arzelà–Ascoli/keketatan pada \(C[0,1]\) karena itu gagal; keluarga
\((\delta_{z_n})\) tidak ketat.

CLT pada satu atau beberapa waktu hanya memberi konvergensi FDD. Teorema
Donsker juga memerlukan pemilihan ruang dan topologi lintasan—misalnya
\(C[0,1]\) untuk interpolasi poligonal atau \(D[0,1]\) dengan topologi
Skorokhod untuk proses tangga—serta keketatan hukum pada ruang tersebut.
Keketatan dan identifikasi FDD bersama-sama menentukan setiap limit
subsekuensial sebagai hukum gerak Brown.

---

## Rekapitulasi nilai dan pemeriksaan kelengkapan {#assessment.o009.d30.cumulative.form-b.section.08}

| Soal | Poin | Waktu anjuran |
|---:|---:|---:|
| 1 | 14 | 30 menit |
| 2 | 13 | 30 menit |
| 3 | 14 | 35 menit |
| 4 | 12 | 25 menit |
| 5 | 13 | 30 menit |
| 6 | 10 | 25 menit |
| 7 | 14 | 35 menit |
| 8 | 10 | 30 menit |
| **Total** | **100** | **240 menit** |

Formulir B mempunyai cetak biru, hasil belajar, bobot, waktu, dan aturan bahan
bantu yang sama dengan Formulir A. Objek uji berbeda: ukuran sampel Poisson,
disintegrasi pada segitiga, gerak acak bias, rantai tiga kelas siklik, CTMC
tiga keadaan, penandaan spasial, transformasi Laplace waktu kena, serta
puncak deterministik bergerak.

## Hak, provenans, dan pernyataan tanpa dukungan {#assessment.o009.d30.cumulative.form-b.section.09}

Teks **Penilaian Kumulatif D30 — Formulir B**, termasuk soal, data, rubrik,
petunjuk, jawaban, dan penyelesaian, merupakan materi asli berbahasa Indonesia
yang disusun untuk edisi ini. Sejauh hak baru timbul, materi ini dilisensikan
di bawah
[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
(CC BY 4.0). ID hak stabilnya adalah
<code>rights.o009.assessment.cumulative.form-b.cc-by-4.0</code>.

Penyusunan dibantu oleh **OpenAI Codex gpt-5.6-sol, Ultra.** atas arahan
pengguna. Provenans ruang lingkup dan istilah hasil belajar berasal dari
indeks kurikulum lokal D30 dan registri hasil belajar O009/D30. Hasil
matematis standar disebut sebagai teorema; formulasi soal, parameter,
petunjuk, dan penyelesaian ditulis baru untuk bentuk alternatif ini.

Lisensi CC BY 4.0 hanya berlaku pada kontribusi baru dalam formulir ini. Ia
tidak melisensikan ulang materi Random, QuantEcon, Žitković, MathJax, atau
komponen lain dalam edisi gabungan, dan tidak menyiratkan dukungan atau
pengesahan dari penulis maupun lembaga sumber.
