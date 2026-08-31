---
title: "Penilaian Kumulatif D30 — Formulir A"
lang: id-ID
author:
  - "OpenAI Codex (penyusunan materi asli atas arahan pengguna)"
assessment:
  course_id: "course.o009.d30"
  assessment_id: "assessment.o009.d30.cumulative.form-a"
  alternate_of: "assessment.o009.d30.cumulative.form-b"
  form: "A"
  version: "1.0.0"
  total_points: 100
  recommended_time_minutes: 240
  target_locale: "id-ID"
  rights_id: "rights.o009.assessment.cumulative.form-a.cc-by-4.0"
  license: "CC-BY-4.0"
  model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Penilaian Kumulatif D30 — Formulir A {#assessment.o009.d30.cumulative.form-a}

## Identitas, tujuan, dan waktu {#assessment.o009.d30.cumulative.form-a.section.01}

Penilaian ini menguji penguasaan kumulatif peran kurikulum
**O009/D30: Probabilitas Teoretis-Ukuran dan Proses Stokastik**. Formulir ini
berdiri sendiri: semua notasi khusus, data model, dan teorema prasyarat yang
boleh dipakai dinyatakan di bawah.

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
sebuah teorema, sebutkan hipotesis yang membuat pemakaiannya sah. Bukti
empiris atau simulasi tidak menggantikan pembuktian probabilistik.

## Prasyarat yang boleh dipakai {#assessment.o009.d30.cumulative.form-a.section.02}

Modul sampling, hukum bilangan besar (LLN), dan teorema limit pusat (CLT) dari
jalur bersama **O006/C140** merupakan prasyarat. Dalam formulir ini peserta
boleh memakai hasil berikut tanpa membuktikannya kembali.

1. **SLLN i.i.d.** Jika \(Y_1,Y_2,\ldots\) i.i.d. dan
   \(\mathbb E|Y_1|<\infty\), maka
   \(\overline Y_n\to\mathbb E Y_1\) hampir pasti.
2. **CLT i.i.d.** Jika \(Y_1,Y_2,\ldots\) i.i.d.,
   \(\mathbb E Y_1=\mu\), dan
   \(0<\operatorname{Var}(Y_1)=\sigma^2<\infty\), maka
   \[
   \frac{\sqrt n(\overline Y_n-\mu)}{\sigma}
   \Rightarrow N(0,1).
   \]
3. Teorema konvergensi monoton, Fatou, konvergensi terdominasi, sifat dasar
   nilai harapan bersyarat, dan fakta bahwa konvergensi dalam distribusi
   menuju limit konstan ekuivalen dengan konvergensi dalam probabilitas boleh
   dipakai dengan hipotesis yang dinyatakan.
4. **Teorema Vitali.** Jika \(W_n\to W\) dalam probabilitas dan keluarga
   \((W_n)_n\) terintegralkan seragam, maka \(W_n\to W\) dalam \(L^1\).
   Khususnya, konvergensi hampir pasti bersama keterintegralan seragam
   mengizinkan pelewatan limit melalui ekspektasi.
5. Untuk martingal waktu diskret, teorema penghentian opsional boleh dipakai
   pada waktu henti terbatas. Pelewatan dari
   \(\tau\wedge n\) ke \(\tau\) tetap harus dibenarkan.
6. Prinsip refleksi untuk gerak Brown standar boleh dipakai, tetapi hubungan
   yang diminta pada Soal 7 harus diturunkan dengan jelas.

Prasyarat ini tidak memberi izin untuk menyimpulkan mode konvergensi yang
lebih kuat, menukar limit dan ekspektasi tanpa kendali ekor, atau menaikkan
konvergensi distribusi berdimensi hingga menjadi konvergensi hukum lintasan
tanpa keketatan.

## Cakupan hasil belajar {#assessment.o009.d30.cumulative.form-a.section.03}

Tabel berikut adalah cetak biru penilaian. ID hasil belajar dipertahankan
secara verbatim agar pemetaan tetap stabil.

| Soal | Domain utama | ID hasil belajar yang dinilai |
|---:|---|---|
| 1 | probabilitas teoretis-ukuran; mode konvergensi; interpretasi LLN/CLT | <code>outcome.o009.distinguish-convergence-modes</code>; <code>outcome.o009.prove-convergence-in-probability</code>; <code>outcome.o009.explain-lln-monte-carlo</code>; <code>outcome.o009.distinguish-evidence-proof</code> |
| 2 | nilai harapan bersyarat; disintegrasi; kernel dan versi nol | <code>outcome.o009.construct-regular-conditional-distribution</code>; <code>outcome.o009.derive-disintegration-and-null-value-versions</code>; <code>outcome.o009.audit-conditional-version-uniqueness</code> |
| 3 | martingal; penghentian; keterintegralan seragam | <code>outcome.o009.prove-stopped-martingale</code>; <code>outcome.o009.check-optional-stopping-conditions</code>; <code>outcome.o009.compute-random-time-expectations</code>; <code>outcome.o009.characterize-ui-martingales</code> |
| 4 | rantai Markov diskret; periodisitas; hukum limit | <code>outcome.o009.compute-discrete-transition-laws</code>; <code>outcome.o009.characterize-markov-periodicity</code>; <code>outcome.o009.solve-finite-limiting-models</code>; <code>outcome.o009.analyze-markov-ergodic-periodic-limits</code> |
| 5 | CTMC; generator; semigrup; proses Poisson | <code>outcome.o009.construct-markov-kernels</code>; <code>outcome.o009.audit-and-repair-stochastic-process-claims</code> |
| 6 | ukuran acak Poisson; hukum bersyarat; penipisan | <code>outcome.o009.formulate-poisson-random-measures</code>; <code>outcome.o009.derive-conditional-poisson-point-laws</code>; <code>outcome.o009.analyze-poisson-thinning-superposition</code> |
| 7 | gerak Brown; hukum Gaussian; martingal; pencapaian; variasi kuadratik | <code>outcome.o009.characterize-standard-brownian-motion</code>; <code>outcome.o009.solve-brownian-drift-joint-conditional-law</code>; <code>outcome.o009.derive-brownian-hitting-maximum-laws</code> |
| 8 | jembatan Brown; versi bersyarat; FDD versus hukum lintasan | <code>outcome.o009.construct-brownian-bridges</code>; <code>outcome.o009.solve-brownian-bridge-conditional-law</code>; <code>outcome.o009.audit-fdd-versus-path-law-convergence</code> |

## Rubrik penskoran umum {#assessment.o009.d30.cumulative.form-a.rubric.global}

Rubrik per soal di bawah bersifat otoritatif dan jumlahnya tepat 100 poin.
Pada setiap baris rubrik, poin penuh memerlukan kesimpulan yang benar beserta
alasan yang memadai. Secara lintas soal:

- syarat, ruang, ukuran, filtrasi, dan mode konvergensi merupakan bagian dari
  jawaban, bukan hiasan;
- salah hitung kecil yang konsisten hanya mengurangi poin pada langkah yang
  terdampak;
- kesimpulan benar dari teorema yang hipotesisnya tidak diperiksa memperoleh
  paling banyak setengah poin pada langkah tersebut;
- bukti dengan kasus khusus dapat memperoleh kredit parsial, tetapi tidak
  menggantikan klaim umum yang diminta;
- jawaban ringkas di kunci menunjukkan target akhir, sedangkan penyelesaian
  lengkap menunjukkan standar penalaran untuk poin penuh.

---

## Bagian I — Dasar ukuran, limit, dan pengondisian {#assessment.o009.d30.cumulative.form-a.section.04}

### Soal 1 — Konvergensi, kendali ekor, dan pembacaan LLN/CLT (14 poin) {#assessment.o009.d30.cumulative.form-a.problem.01}

Pada ruang probabilitas \(\Omega=(0,1]\) dengan aljabar-σ Borel dan ukuran
Lebesgue, definisikan
\[
X_n(\omega)=n\mathbf 1_{(0,1/n]}(\omega).
\]
Secara terpisah, misalkan \(Y_1,Y_2,\ldots\) i.i.d. dengan
\(\mathbb E Y_1=\mu\) dan
\(0<\operatorname{Var}(Y_1)=\sigma^2<\infty\), serta
\(\overline Y_n=n^{-1}\sum_{k=1}^nY_k\).

1. Buktikan bahwa \(X_n\to0\) hampir pasti. Tentukan apakah konvergensi juga
   berlaku dalam probabilitas, dalam distribusi, dan dalam \(L^1\). **(4 poin)**
2. Hitung \(\mathbb E|X_n|\), lalu uji keterintegralan seragam langsung dari
   definisi ekor. Jelaskan mengapa keterbatasan dalam \(L^1\) tidak cukup
   untuk menukar limit dan ekspektasi. **(3 poin)**
3. Nyatakan kesimpulan SLLN dan CLT yang tepat untuk \(\overline Y_n\).
   Dari CLT, buktikan—dengan argumen keketatan—bahwa
   \(\overline Y_n\to\mu\) dalam probabilitas. Jelaskan mengapa langkah itu
   tidak membuktikan konvergensi hampir pasti. **(4 poin)**
4. Hitung
   \(\mathbb E[(\overline Y_n-\mu)^2]\), berikan galat baku Monte Carlo
   teoretis, dan bedakan pernyataan probabilistik tersebut dari bukti
   empiris berbasis satu keluaran simulasi. **(3 poin)**

#### Rubrik Soal 1 {#assessment.o009.d30.cumulative.form-a.problem.01.rubric}

| Komponen | Poin |
|---|---:|
| Limit titik demi titik dan implikasi a.s. \(\Rightarrow\) probabilitas \(\Rightarrow\) distribusi; keputusan \(L^1\) benar | 4 |
| Perhitungan ekor yang membuktikan kegagalan keterintegralan seragam dan interpretasinya | 3 |
| Pernyataan SLLN/CLT dengan mode dan hipotesis tepat; bukti keketatan | 4 |
| Galat kuadrat rata-rata, galat baku, dan batas bukti simulasi | 3 |

#### Petunjuk 1 {#assessment.o009.d30.cumulative.form-a.problem.01.hint.01}

Untuk \(\omega>0\) tetap, pilih \(n>1/\omega\). Untuk uji ekor, setelah
\(K>0\) diberikan, pilih bilangan bulat \(n>K\).

#### Petunjuk 2 {#assessment.o009.d30.cumulative.form-a.problem.01.hint.02}

Jika
\[
Z_n=\frac{\sqrt n(\overline Y_n-\mu)}{\sigma}\Rightarrow Z,
\]
maka \((Z_n)\) ketat. Untuk \(\varepsilon>0\), bandingkan
\(\mathbb P(|\overline Y_n-\mu|>\varepsilon)\) dengan
\(\mathbb P(|Z_n|>\varepsilon\sqrt n/\sigma)\).

#### Jawaban ringkas {#assessment.o009.d30.cumulative.form-a.problem.01.answer}

Berlaku \(X_n\to0\) hampir pasti, dalam probabilitas, dan dalam distribusi,
tetapi tidak dalam \(L^1\), sebab \(\mathbb E|X_n|=1\). Keluarga itu tidak
terintegralkan seragam. SLLN memberi
\(\overline Y_n\to\mu\) hampir pasti, sedangkan CLT memberi limit normal bagi
skala \(\sqrt n\). Keketatan peubah berskala memberi konsistensi dalam
probabilitas, bukan konvergensi hampir pasti.
Selain itu,
\(\mathbb E[(\overline Y_n-\mu)^2]=\sigma^2/n\) dan galat baku teoretisnya
\(\sigma/\sqrt n\). Satu simulasi hanya merupakan realisasi, bukan bukti
teorema.

#### Penyelesaian lengkap {#assessment.o009.d30.cumulative.form-a.problem.01.solution}

Untuk setiap \(\omega\in(0,1]\), jika \(n>1/\omega\), maka
\(1/n<\omega\), sehingga \(X_n(\omega)=0\). Jadi konvergensi ke nol berlaku
pada setiap titik, khususnya hampir pasti. Konvergensi hampir pasti
menyiratkan konvergensi dalam probabilitas, dan konvergensi dalam
probabilitas menyiratkan konvergensi dalam distribusi.

Namun
\[
\mathbb E|X_n|
=\int_0^{1/n}n\,d\omega
=1.
\]
Karena limitnya nol,
\(\mathbb E|X_n-0|=1\) untuk semua \(n\); jadi tidak ada konvergensi
\(L^1\). Untuk \(K>0\), pilih \(n>K\). Pada penyangga \(X_n\),
\(|X_n|=n>K\), sehingga
\[
\mathbb E\!\left[
 |X_n|\mathbf 1_{\{|X_n|>K\}}
\right]=1.
\]
Akibatnya
\[
\sup_n\mathbb E\!\left[
 |X_n|\mathbf 1_{\{|X_n|>K\}}
\right]\ge1
\]
untuk setiap \(K\), dan limit supremum ekor tidak menuju nol. Keluarga
\((X_n)\) tidak terintegralkan seragam walaupun
\(\sup_n\mathbb E|X_n|=1\). Massa harapan berada pada kejadian yang makin
jarang tetapi makin tinggi; inilah sebab limit tidak boleh dilewatkan melalui
ekspektasi. Teorema Vitali akan memperbaiki langkah tersebut bila
konvergensi dalam probabilitas dipasangkan dengan keterintegralan seragam.

Untuk sampel i.i.d., SLLN yang diizinkan memberi
\[
\overline Y_n\longrightarrow\mu\quad\text{hampir pasti},
\]
sedangkan CLT memberi
\[
Z_n:=\frac{\sqrt n(\overline Y_n-\mu)}{\sigma}
\Rightarrow N(0,1).
\]
Konvergensi dalam distribusi membuat \((Z_n)\) ketat. Jadi, untuk setiap
\(\eta>0\), ada \(M<\infty\) sehingga, untuk semua \(n\) cukup besar,
\(\mathbb P(|Z_n|>M)<\eta\). Jika juga
\(\varepsilon\sqrt n/\sigma>M\), maka
\[
\mathbb P(|\overline Y_n-\mu|>\varepsilon)
=\mathbb P\!\left(
 |Z_n|>\frac{\varepsilon\sqrt n}{\sigma}
\right)
\le \mathbb P(|Z_n|>M)<\eta.
\]
Jadi \(\overline Y_n\to\mu\) dalam probabilitas. Argumen ini hanya
mengendalikan peluang marginal pada setiap \(n\); ia tidak mengendalikan
kejadian lintas semua \(n\) yang diperlukan untuk konvergensi hampir pasti.
Konvergensi hampir pasti di sini datang dari SLLN, bukan dari CLT semata.

Terakhir, independensi memberi
\[
\mathbb E[(\overline Y_n-\mu)^2]
=\operatorname{Var}(\overline Y_n)
=\frac{1}{n^2}\sum_{k=1}^n\sigma^2
=\frac{\sigma^2}{n}.
\]
Karena itu galat baku teoretis estimator Monte Carlo \(\overline Y_n\) adalah
\(\sigma/\sqrt n\). Bila \(\sigma\) tidak diketahui, ia lazim ditaksir dengan
simpangan baku sampel; interval normal yang dihasilkan bersifat asimtotik
kecuali ada hasil hingga-sampel tambahan. Satu jejak simulasi dapat
menunjukkan perilaku yang konsisten dengan teori, tetapi tidak membuktikan
SLLN, CLT, atau laju galat untuk semua realisasi.

### Soal 2 — Nilai harapan bersyarat, disintegrasi, dan versi nol (13 poin) {#assessment.o009.d30.cumulative.form-a.problem.02}

Misalkan \(X\) bernilai dalam \(S=\{0,1,2\}\) dan \(Y\) bernilai dalam
\(T=\{0,1\}\), dengan
\[
\mathbb P(X=0)=\mathbb P(X=1)=\tfrac12,\qquad
\mathbb P(X=2)=0,
\]
serta
\[
\mathbb P(Y=1\mid X=0)=\tfrac14,\qquad
\mathbb P(Y=1\mid X=1)=\tfrac34.
\]
Untuk setiap \(c\in[0,1]\), definisikan kernel \(K_c\) dengan
\[
K_c(0,\{1\})=\tfrac14,\qquad
K_c(1,\{1\})=\tfrac34,\qquad
K_c(2,\{1\})=c,
\]
dan \(K_c(x,\{0\})=1-K_c(x,\{1\})\).

1. Tentukan satu versi \(\mathbb E[Y\mid\sigma(X)]\), lalu hitung
   \(\mathbb E Y\) dengan sifat menara. **(3 poin)**
2. Verifikasi bahwa setiap \(K_c\) merupakan kernel probabilitas dan memenuhi
   identitas disintegrasi
   \[
   \mathbb P(X\in A,Y\in B)
   =\int_A K_c(x,B)\,\mathbb P_X(dx)
   \]
   untuk semua \(A\subseteq S\) dan \(B\subseteq T\). **(4 poin)**
3. Jelaskan dengan tepat dalam arti apa kernel-kernel \(K_c\) itu sama, dan
   mengapa hukum gabungan tidak menentukan nilai di \(x=2\). **(2 poin)**
4. Pada ruang sasaran Borel standar umum, jelaskan perbedaan antara memilih
   versi \(\mathbb P(Y\in B\mid\mathcal G)\) secara terpisah untuk setiap
   \(B\) dan memiliki satu distribusi bersyarat reguler
   \(K(\omega,\cdot)\). Nyatakan peran kelas penentu terhitung dalam
   keunikan. **(4 poin)**

#### Rubrik Soal 2 {#assessment.o009.d30.cumulative.form-a.problem.02.rubric}

| Komponen | Poin |
|---|---:|
| Versi nilai harapan bersyarat dan sifat menara | 3 |
| Dua syarat kernel serta verifikasi disintegrasi | 4 |
| Keunikan hampir di mana-mana dan kebebasan pada nilai nol | 2 |
| Koherensi ukuran, hipotesis Borel standar, dan kelas penentu terhitung | 4 |

#### Petunjuk 1 {#assessment.o009.d30.cumulative.form-a.problem.02.hint.01}

Karena \(S\) dan \(T\) berhingga, keterukuran kernel otomatis setelah setiap
nilainya ditentukan. Dalam integral disintegrasi, suku dengan \(x=2\)
dikalikan oleh \(\mathbb P_X(\{2\})\).

#### Petunjuk 2 {#assessment.o009.d30.cumulative.form-a.problem.02.hint.02}

Untuk keunikan pada sasaran umum, mula-mula samakan dua kernel pada satu kelas
penentu terhitung. Gabungkan himpunan-himpunan nol dengan mengambil gabungan
terhitung, lalu gunakan ketunggalan ukuran.

#### Jawaban ringkas {#assessment.o009.d30.cumulative.form-a.problem.02.answer}

Satu versi adalah
\[
\mathbb E[Y\mid\sigma(X)]
=\tfrac14\mathbf1_{\{X=0\}}+\tfrac34\mathbf1_{\{X=1\}},
\]
dengan nilai bebas pada kejadian \(\{X=2\}\); maka \(\mathbb EY=1/2\).
Setiap \(K_c\) adalah kernel Bernoulli dan semua memenuhi disintegrasi karena
\(\mathbb P_X(\{2\})=0\). Kernel-kernel itu sama
\(\mathbb P_X\)-hampir di mana-mana, tetapi tidak harus sama titik demi titik.
Pada sasaran Borel standar, satu kernel memilih probabilitas bersyarat secara
koheren untuk semua kejadian; kelas penentu terhitung memungkinkan satu
himpunan nol bersama untuk pernyataan keunikan ukuran.

#### Penyelesaian lengkap {#assessment.o009.d30.cumulative.form-a.problem.02.solution}

Karena \(Y\) bernilai nol-satu,
\[
\mathbb E[Y\mid X=x]=\mathbb P(Y=1\mid X=x)
\]
untuk \(x\) yang mempunyai massa positif. Jadi satu versi ialah
\[
g(X)=\tfrac14\mathbf1_{\{X=0\}}
     +\tfrac34\mathbf1_{\{X=1\}}.
\]
Nilai \(g(2)\) boleh dipilih sebarang karena \(\mathbb P(X=2)=0\).
Sifat menara memberi
\[
\mathbb EY
=\mathbb E[g(X)]
=\tfrac12\cdot\tfrac14+\tfrac12\cdot\tfrac34
=\tfrac12.
\]

Untuk setiap \(x\), pemetaan \(B\mapsto K_c(x,B)\) adalah ukuran peluang
Bernoulli pada \(T\). Untuk setiap \(B\subseteq T\), pemetaan
\(x\mapsto K_c(x,B)\) terukur karena domainnya berhingga. Jadi \(K_c\)
merupakan kernel probabilitas. Selanjutnya,
\[
\int_AK_c(x,B)\,\mathbb P_X(dx)
=\sum_{x\in A}K_c(x,B)\mathbb P(X=x).
\]
Suku \(x=0\) dan \(x=1\) sama dengan probabilitas gabungan yang ditentukan
oleh model, sedangkan suku \(x=2\) selalu nol. Karena itu jumlah tersebut
sama dengan \(\mathbb P(X\in A,Y\in B)\), untuk setiap \(A,B\) dan setiap
\(c\in[0,1]\).

Bila \(c\ne c'\), kernel \(K_c\) dan \(K_{c'}\) berbeda pada \(x=2\), tetapi
\[
K_c(x,\cdot)=K_{c'}(x,\cdot)
\quad\text{untuk }\mathbb P_X\text{-hampir setiap }x.
\]
Disintegrasi hanya mengintegralkan kernel terhadap \(\mathbb P_X\), sehingga
tidak dapat mengidentifikasi nilainya pada himpunan nol marginal. Pernyataan
\(Y\mid X=2\) karena itu membutuhkan pilihan versi atau struktur tambahan;
hukum gabungan saja tidak memilih \(c\).

Secara umum, untuk satu \(B\) tetap,
\(\mathbb E[\mathbf1_{\{Y\in B\}}\mid\mathcal G]\) hanya merupakan kelas
fungsi modulo kesamaan hampir pasti. Jika versi dipilih secara terpisah untuk
tak terhitung banyak \(B\), himpunan nolnya dapat bergantung pada \(B\);
pilihan tersebut belum tentu aditif terhitung sebagai fungsi \(B\) pada satu
\(\omega\). Distribusi bersyarat reguler adalah satu kernel
\[
K:(\Omega,\mathcal G)\rightsquigarrow(T,\mathcal T)
\]
yang sekaligus terukur dalam \(\omega\), merupakan ukuran peluang dalam
argumen himpunan, dan mewakili semua peluang bersyarat. Sasaran Borel standar
memberi teorema keberadaan yang dipakai di sini dan memiliki kelas penentu
terhitung \(\mathcal C\). Jika dua kernel mewakili hukum yang sama, keduanya
sama hampir pasti untuk setiap \(C\in\mathcal C\). Gabungan terhitung dari
himpunan nol tersebut masih nol; di luar gabungan itu kedua ukuran sepakat
pada \(\mathcal C\), lalu teorema ketunggalan ukuran memberi kesamaan pada
seluruh \(\mathcal T\). Kesimpulannya tetap hampir di mana-mana sebagai
ukuran, bukan kesamaan pada setiap titik.

---

## Bagian II — Martingal dan penghentian {#assessment.o009.d30.cumulative.form-a.section.05}

### Soal 3 — Keluar dari selang dan audit penghentian opsional (14 poin) {#assessment.o009.d30.cumulative.form-a.problem.03}

Misalkan \(\xi_1,\xi_2,\ldots\) i.i.d. dengan
\(\mathbb P(\xi_k=1)=\mathbb P(\xi_k=-1)=1/2\),
\[
S_n=\sum_{k=1}^n\xi_k,\qquad S_0=0,\qquad
\mathcal F_n=\sigma(\xi_1,\ldots,\xi_n),
\]
dan
\[
\tau=\inf\{n\ge0:S_n\in\{-2,3\}\}.
\]

1. Tunjukkan bahwa \(S_n\) dan \(S_n^2-n\) adalah martingal, lalu buktikan
   bahwa proses berhenti \((S_{n\wedge\tau})_{n\ge0}\) juga martingal.
   Buktikan bahwa \(\tau<\infty\) hampir pasti. **(3 poin)**
2. Dengan menghentikan pada \(\tau\wedge n\), buktikan
   \(\mathbb E S_\tau=0\) dan hitung
   \(\mathbb P(S_\tau=3)\). Sebutkan kendali limit yang dipakai. **(4 poin)**
3. Gunakan martingal \(S_n^2-n\) untuk menghitung
   \(\mathbb E\tau\). Benarkan setiap pelewatan limit. **(4 poin)**
4. Bandingkan dengan
   \(\rho=\inf\{n\ge0:S_n=1\}\). Diketahui \(\rho<\infty\) hampir pasti.
   Jelaskan mengapa fakta itu saja tidak membenarkan
   \(\mathbb E S_\rho=\mathbb E S_0\), dan simpulkan sifat
   \((S_{\rho\wedge n})_n\) yang gagal. **(3 poin)**

#### Rubrik Soal 3 {#assessment.o009.d30.cumulative.form-a.problem.03.rubric}

| Komponen | Poin |
|---|---:|
| Dua verifikasi martingal, sifat martingal proses berhenti, dan keterhinggaan waktu keluar | 3 |
| Penghentian terbatas, dominasi, dan peluang pencapaian \(2/5\) | 4 |
| Identitas martingal kuadrat dan perhitungan \(\mathbb E\tau=6\) | 4 |
| Audit waktu henti satu sisi dan kegagalan keterintegralan seragam | 3 |

#### Petunjuk 1 {#assessment.o009.d30.cumulative.form-a.problem.03.hint.01}

Selama belum keluar, rantai berada di \(\{-1,0,1,2\}\). Dari setiap keadaan
itu ada peluang sekurang-kurangnya \(1/4\) untuk mencapai salah satu batas
dalam dua langkah berikutnya.

#### Petunjuk 2 {#assessment.o009.d30.cumulative.form-a.problem.03.hint.02}

Gunakan \(|S_{\tau\wedge n}|\le3\) dan
\(S_{\tau\wedge n}^2\le9\). Untuk waktu satu sisi, bandingkan
\(\mathbb E S_{\rho\wedge n}=0\) dengan limit hampir pasti
\(S_\rho=1\).

#### Jawaban ringkas {#assessment.o009.d30.cumulative.form-a.problem.03.answer}

Kedua proses yang diberikan adalah martingal dan \(\tau\) mempunyai ekor
geometrik, sehingga berhingga hampir pasti. Penghentian pada
\(\tau\wedge n\), diikuti konvergensi terdominasi, memberi
\(\mathbb ES_\tau=0\). Maka
\(\mathbb P(S_\tau=3)=2/5\). Martingal kuadrat memberi
\(\mathbb E\tau=\mathbb E S_\tau^2=6\).
Untuk \(\rho\), keterhinggaan hampir pasti tidak cukup:
\(\mathbb E S_{\rho\wedge n}=0\) tetapi \(S_{\rho\wedge n}\to1\) hampir
pasti, sehingga keluarga yang dihentikan tidak terintegralkan seragam.

#### Penyelesaian lengkap {#assessment.o009.d30.cumulative.form-a.problem.03.solution}

Karena \(\xi_{n+1}\) independen dari \(\mathcal F_n\), memiliki rataan nol, dan
\(\xi_{n+1}^2=1\),
\[
\mathbb E(S_{n+1}\mid\mathcal F_n)=S_n
\]
serta
\[
\begin{aligned}
\mathbb E(S_{n+1}^2-(n+1)\mid\mathcal F_n)
&=\mathbb E(S_n^2+2S_n\xi_{n+1}+\xi_{n+1}^2-n-1
             \mid\mathcal F_n)\\
&=S_n^2-n.
\end{aligned}
\]
Keterintegralan jelas karena setiap waktu deterministik mempunyai jumlah
berhingga suku terbatas.

Selanjutnya,
\[
S_{(n+1)\wedge\tau}-S_{n\wedge\tau}
=\xi_{n+1}\mathbf1_{\{\tau>n\}}.
\]
Kejadian \(\{\tau>n\}\) berada dalam \(\mathcal F_n\). Oleh karena itu,
\[
\mathbb E\!\left[
S_{(n+1)\wedge\tau}-S_{n\wedge\tau}
\mid\mathcal F_n
\right]
=\mathbf1_{\{\tau>n\}}
\mathbb E(\xi_{n+1}\mid\mathcal F_n)
=0.
\]
Jadi \((S_{n\wedge\tau})_{n\ge0}\) adalah martingal.

Sebelum \(\tau\), proses berada dalam \(\{-1,0,1,2\}\). Dari \(-1\) atau
\(2\), satu langkah ke arah batas cukup; dari \(0\) atau \(1\), dua langkah
berturut-turut ke batas terdekat cukup. Jadi, bersyarat pada
\(\{\tau>2k\}\), peluang keluar dalam dua langkah berikutnya paling sedikit
\(1/4\). Dengan induksi,
\[
\mathbb P(\tau>2k)\le(3/4)^k\longrightarrow0.
\]
Maka \(\tau<\infty\) hampir pasti; bahkan argumen ini menunjukkan ekor
geometrik.

Karena \(\tau\wedge n\) terbatas, penghentian opsional memberi
\[
\mathbb E S_{\tau\wedge n}=\mathbb E S_0=0.
\]
Selain itu, \(|S_{\tau\wedge n}|\le3\) dan
\(S_{\tau\wedge n}\to S_\tau\) hampir pasti. Teorema konvergensi terdominasi
memberi \(\mathbb ES_\tau=0\). Jika
\(p=\mathbb P(S_\tau=3)\), maka
\[
0=\mathbb ES_\tau=3p-2(1-p)=5p-2,
\]
sehingga \(p=2/5\).

Terapkan penghentian opsional pada martingal \(S_n^2-n\) di
\(\tau\wedge n\):
\[
\mathbb E[S_{\tau\wedge n}^2]-\mathbb E[\tau\wedge n]=0.
\]
Ruas pertama menuju \(\mathbb E S_\tau^2\) dengan konvergensi terdominasi,
karena \(S_{\tau\wedge n}^2\le9\). Ruas kedua menuju \(\mathbb E\tau\)
dengan konvergensi monoton. Jadi
\[
\mathbb E\tau=\mathbb E S_\tau^2
=9\cdot\frac25+4\cdot\frac35
=6.
\]

Untuk waktu satu sisi \(\rho\), setiap \(\rho\wedge n\) memang terbatas dan
\(\mathbb E S_{\rho\wedge n}=0\). Akan tetapi,
\(S_{\rho\wedge n}\to S_\rho=1\) hampir pasti. Jika keluarga
\((S_{\rho\wedge n})_n\) terintegralkan seragam, Vitali akan memberi
konvergensi \(L^1\), sehingga ekspektasinya harus menuju satu—bertentangan
dengan ekspektasi nol untuk setiap \(n\). Jadi keluarga itu tidak
terintegralkan seragam. Kesalahan pada penerapan naif bukan penghentian pada
\(\rho\wedge n\), melainkan pelewatan \(n\to\infty\) tanpa kendali ekor.

---

## Bagian III — Markov, CTMC, dan Poisson {#assessment.o009.d30.cumulative.form-a.section.06}

### Soal 4 — Periodisitas dan limit rantai diskret (12 poin) {#assessment.o009.d30.cumulative.form-a.problem.04}

Pada ruang keadaan \(E=\{0,1,2\}\), pertimbangkan rantai Markov homogen
dengan matriks transisi
\[
P=
\begin{pmatrix}
0&1&0\\
\tfrac12&0&\tfrac12\\
0&1&0
\end{pmatrix}.
\]

1. Hitung \(P^2\) dan gunakan graf transisi untuk menunjukkan bahwa rantai
   tak tereduksi. **(3 poin)**
2. Tentukan periode setiap keadaan. **(2 poin)**
3. Tentukan distribusi stasioner tunggal \(\pi\). **(3 poin)**
4. Jika \(X_0=0\), tentukan limit subsekuens hukum \(X_{2n}\) dan
   \(X_{2n+1}\), lalu hitung limit Cesàro
   \(N^{-1}\sum_{n=0}^{N-1}\mathcal L(X_n)\). Jelaskan mengapa
   ketunggalan \(\pi\) tidak menjamin \(\mathcal L(X_n)\to\pi\). **(4 poin)**

#### Rubrik Soal 4 {#assessment.o009.d30.cumulative.form-a.problem.04.rubric}

| Komponen | Poin |
|---|---:|
| \(P^2\) benar dan argumen komunikasi | 3 |
| Periode dua untuk seluruh kelas | 2 |
| Persamaan invarian dan normalisasi | 3 |
| Dua limit subsekuens, limit Cesàro, dan diagnosis aperiodisitas | 4 |

#### Petunjuk 1 {#assessment.o009.d30.cumulative.form-a.problem.04.hint.01}

Keadaan \(1\) selalu berpindah ke himpunan \(\{0,2\}\), sedangkan \(0\) dan
\(2\) selalu berpindah ke \(1\). Gunakan pembagian bipartit ini untuk
periodisitas.

#### Petunjuk 2 {#assessment.o009.d30.cumulative.form-a.problem.04.hint.02}

Mulai dari \(0\), setelah dua langkah hukumnya
\((1/2,0,1/2)\). Periksa bahwa hukum ini tetap sama setelah setiap dua
langkah berikutnya.

#### Jawaban ringkas {#assessment.o009.d30.cumulative.form-a.problem.04.answer}

\[
P^2=
\begin{pmatrix}
\tfrac12&0&\tfrac12\\
0&1&0\\
\tfrac12&0&\tfrac12
\end{pmatrix}.
\]
Rantai tak tereduksi dan semua keadaan berperiode dua. Distribusi
stasionernya
\(\pi=(1/4,1/2,1/4)\). Dari \(0\), hukum pada waktu ganjil adalah
\(\delta_1\), sedangkan pada waktu genap positif adalah
\((1/2,0,1/2)\). Jadi tidak ada limit waktu biasa, tetapi rata-rata Cesàro
menuju \(\pi\). Hipotesis yang hilang untuk konvergensi biasa ialah
aperiodisitas.

#### Penyelesaian lengkap {#assessment.o009.d30.cumulative.form-a.problem.04.solution}

Perkalian matriks memberi
\[
P^2=
\begin{pmatrix}
\tfrac12&0&\tfrac12\\
0&1&0\\
\tfrac12&0&\tfrac12
\end{pmatrix}.
\]
Dari \(0\) atau \(2\) rantai mencapai \(1\) dalam satu langkah; dari \(1\)
rantai mencapai \(0\) dan \(2\) masing-masing dengan peluang positif. Maka
setiap keadaan berkomunikasi dengan setiap keadaan lain dan rantai tak
tereduksi.

Grafnya bipartit dengan bagian \(\{1\}\) dan \(\{0,2\}\), sehingga waktu
kembali hanya mungkin genap. Kembali dalam dua langkah mempunyai peluang
positif bagi setiap keadaan. Jadi gcd waktu kembali adalah dua. Karena
periodisitas konstan pada kelas komunikasi, semua keadaan berperiode dua.

Tuliskan \(\pi=(\pi_0,\pi_1,\pi_2)\). Persamaan \(\pi P=\pi\) memberi
\[
\pi_0=\tfrac12\pi_1,\qquad
\pi_2=\tfrac12\pi_1,\qquad
\pi_1=\pi_0+\pi_2.
\]
Dengan \(\pi_0+\pi_1+\pi_2=1\), diperoleh
\[
\pi=(\tfrac14,\tfrac12,\tfrac14).
\]
Ketunggalan juga mengikuti dari keterhinggaan dan ketaktereduksian rantai.

Jika \(X_0=0\), maka \(\mathcal L(X_1)=\delta_1\) dan
\(\mathcal L(X_2)=(1/2,0,1/2)\). Matriks \(P^2\) menunjukkan kedua hukum
tersebut tetap pada kelas paritasnya. Jadi, untuk \(n\ge1\),
\[
\mathcal L(X_{2n})=(\tfrac12,0,\tfrac12),
\qquad
\mathcal L(X_{2n+1})=\delta_1.
\]
Keduanya berbeda, sehingga hukum waktu biasa tidak konvergen. Separuh waktu
asimtotik berada pada masing-masing subsekuens; akibatnya
\[
\frac1N\sum_{n=0}^{N-1}\mathcal L(X_n)
\longrightarrow
\tfrac12(\tfrac12,0,\tfrac12)+\tfrac12(0,1,0)
=(\tfrac14,\tfrac12,\tfrac14)=\pi.
\]
Distribusi stasioner yang unik menyatakan invariansi dan rata-rata okupasi,
tetapi tidak menghapus osilasi periodik. Pada rantai berhingga tak tereduksi,
aperiodisitas adalah syarat tambahan yang menghasilkan konvergensi waktu
biasa menuju \(\pi\).

### Soal 5 — Generator, semigrup CTMC, dan proses Poisson (13 poin) {#assessment.o009.d30.cumulative.form-a.problem.05}

Misalkan \(X=(X_t)_{t\ge0}\) adalah CTMC pada \(\{0,1\}\) dengan generator
\[
Q=
\begin{pmatrix}
-\lambda&\lambda\\
\mu&-\mu
\end{pmatrix},
\qquad \lambda,\mu>0.
\]
Tuliskan \(r=\lambda+\mu\).

1. Jelaskan makna entri \(Q\), tentukan hukum waktu tunggu di masing-masing
   keadaan, dan identifikasi rantai lompatan tertanam. **(3 poin)**
2. Hitung \(P_t=e^{tQ}\) secara eksplisit dan verifikasi
   \(P_0=I\) serta salah satu persamaan Kolmogorov. **(4 poin)**
3. Tentukan distribusi stasioner dan limit \(P_t\) ketika
   \(t\to\infty\). Jelaskan mengapa proses ini tidak meledak, serta mengapa
   argumen tersebut tidak boleh digeneralisasi ke setiap matriks intensitas
   berdimensi tak hingga tanpa syarat tambahan. **(3 poin)**
4. Sekarang pertimbangkan CTMC \(N_t\) pada \(\mathbb Z_+\) dengan
   \(q_{k,k+1}=\nu\), \(q_{k,k}=-\nu\), dan semua entri lain nol,
   dengan \(N_0=0\). Tentukan
   \(\mathbb P(N_t=j)\) dan jelaskan hubungan konstruksinya dengan proses
   Poisson berlaju \(\nu\). **(3 poin)**

#### Rubrik Soal 5 {#assessment.o009.d30.cumulative.form-a.problem.05.rubric}

| Komponen | Poin |
|---|---:|
| Interpretasi laju, waktu tunggu eksponensial, dan rantai tertanam | 3 |
| Semigrup eksplisit dan verifikasi persamaan Kolmogorov | 4 |
| Invariansi, limit, bukti tidak meledak, dan batas ruang tak hingga | 3 |
| Hukum Poisson dan konstruksi melalui waktu antar-lompatan | 3 |

#### Petunjuk 1 {#assessment.o009.d30.cumulative.form-a.problem.05.hint.01}

Matriks \(Q\) mempunyai nilai eigen \(0\) dan \(-r\). Setiap baris \(P_t\)
adalah campuran distribusi stasioner dan satu suku yang meluruh seperti
\(e^{-rt}\).

#### Petunjuk 2 {#assessment.o009.d30.cumulative.form-a.problem.05.hint.02}

Untuk rantai pada \(\mathbb Z_+\), waktu antar-lompatan semuanya i.i.d.
\(\operatorname{Exp}(\nu)\). Kejadian \(N_t=j\) ekuivalen dengan
\(T_j\le t<T_{j+1}\), dengan \(T_j\) jumlah \(j\) waktu eksponensial.

#### Jawaban ringkas {#assessment.o009.d30.cumulative.form-a.problem.05.answer}

Waktu tunggu di \(0\) dan \(1\) masing-masing
\(\operatorname{Exp}(\lambda)\) dan \(\operatorname{Exp}(\mu)\); rantai
tertanam berganti keadaan secara deterministik. Semigrupnya
\[
P_t=
\begin{pmatrix}
\dfrac{\mu}{r}+\dfrac{\lambda}{r}e^{-rt}
&
\dfrac{\lambda}{r}(1-e^{-rt})
\\[6pt]
\dfrac{\mu}{r}(1-e^{-rt})
&
\dfrac{\lambda}{r}+\dfrac{\mu}{r}e^{-rt}
\end{pmatrix}.
\]
Distribusi stasioner adalah
\((\mu/r,\lambda/r)\), dan setiap baris \(P_t\) menuju distribusi itu.
Laju yang terbatas menjamin tidak ada ledakan. Untuk rantai kelahiran murni
dengan laju konstan \(\nu\),
\[
\mathbb P(N_t=j)=e^{-\nu t}\frac{(\nu t)^j}{j!},
\]
dan waktu antar-kedatangannya i.i.d. eksponensial, yaitu konstruksi proses
Poisson.

#### Penyelesaian lengkap {#assessment.o009.d30.cumulative.form-a.problem.05.solution}

Entri luar diagonal \(q_{ij}\) adalah laju lompatan \(i\to j\), sedangkan
\(-q_{ii}=\sum_{j\ne i}q_{ij}\) adalah laju keluar total. Maka, ketika berada
di \(0\), proses menunggu waktu \(\operatorname{Exp}(\lambda)\) lalu
berpindah ke \(1\); ketika berada di \(1\), ia menunggu
\(\operatorname{Exp}(\mu)\) lalu berpindah ke \(0\). Jadi rantai lompatan
tertanam berganti \(0,1,0,1,\ldots\).

Karena nilai eigen \(Q\) adalah \(0\) dan \(-r\), atau dengan menyelesaikan
persamaan maju, diperoleh
\[
P_t=
\begin{pmatrix}
\dfrac{\mu}{r}+\dfrac{\lambda}{r}e^{-rt}
&
\dfrac{\lambda}{r}(1-e^{-rt})
\\[6pt]
\dfrac{\mu}{r}(1-e^{-rt})
&
\dfrac{\lambda}{r}+\dfrac{\mu}{r}e^{-rt}
\end{pmatrix}.
\]
Pada \(t=0\), suku eksponensial sama dengan satu dan \(P_0=I\). Sebagai
contoh verifikasi persamaan mundur, turunan entri \((0,1)\) adalah
\[
\frac{d}{dt}P_{01}(t)=\lambda e^{-rt}.
\]
Sementara itu,
\[
(QP_t)_{01}
=-\lambda P_{01}(t)+\lambda P_{11}(t)
=\lambda e^{-rt}.
\]
Perhitungan serupa berlaku untuk entri lain, sehingga
\(P_t'=QP_t\). Karena \(P_t=e^{tQ}\), juga berlaku \(P_t'=P_tQ\) dan
semigrup Chapman–Kolmogorov \(P_{s+t}=P_sP_t\).

Persamaan \(\pi Q=0\), \(\pi_0+\pi_1=1\), memberi
\[
\pi=(\mu/r,\lambda/r).
\]
Ketika \(t\to\infty\), \(e^{-rt}\to0\), sehingga setiap baris \(P_t\)
menuju \(\pi\). Kedua laju keluar dibatasi oleh
\(q_*=\max(\lambda,\mu)\). Melalui uniformisasi, jumlah lompatan sampai waktu
\(t\) didominasi oleh peubah Poisson berparameter \(q_*t\); karena itu jumlah
lompatan pada selang terbatas hampir pasti berhingga dan proses tidak
meledak. Pada ruang keadaan tak hingga, laju keluar dapat tak terbatas dan
akumulasi waktu tunggu dapat berhingga. Sebuah matriks formal dengan entri
luar diagonal nonnegatif dan jumlah baris nol belum dengan sendirinya
menjamin semigrup konservatif atau ketidakmeledakan; domain operator dan
kelas solusi juga dapat menjadi bagian hipotesis.

Untuk rantai kelahiran murni berlaju konstan, waktu antar-lompatan
\(E_1,E_2,\ldots\) i.i.d. \(\operatorname{Exp}(\nu)\). Jika
\(T_j=E_1+\cdots+E_j\), maka \(N_t=j\) tepat ketika
\(T_j\le t<T_{j+1}\). Jumlah kedatangan dari pembaruan eksponensial ini
mempunyai hukum
\[
\mathbb P(N_t=j)=e^{-\nu t}\frac{(\nu t)^j}{j!},
\qquad j\in\mathbb Z_+.
\]
Sifat tanpa ingatan eksponensial memberi inkremen stasioner dan independen:
sesudah suatu waktu, waktu tunggu residual memiliki lagi hukum
\(\operatorname{Exp}(\nu)\) dan bebas dari masa lalu. Jadi CTMC ini adalah
proses Poisson berlaju \(\nu\). Karena lajunya konstan dan terbatas, ia juga
tidak meledak.

### Soal 6 — Ukuran acak Poisson, pengondisian, dan penipisan (10 poin) {#assessment.o009.d30.cumulative.form-a.problem.06}

Misalkan \(N\) adalah ukuran acak Poisson pada ruang ukur σ-terhingga
\((S,\mathcal S,\mu)\). Artinya, untuk himpunan terukur berukuran hingga,
\(N(A)\sim\operatorname{Poisson}(\mu(A))\), dan hitungan pada himpunan saling
lepas independen. Ambil \(A,B\in\mathcal S\) saling lepas dengan
\(\mu(A)=a\), \(\mu(B)=b\), dan \(0<a+b<\infty\).

1. Hitung fungsi pembangkit peluang bersama
   \(\mathbb E[s^{N(A)}t^{N(B)}]\), serta
   \(\mathbb EN(A)\), \(\operatorname{Var}N(A)\), dan
   \(\operatorname{Cov}(N(A),N(B))\). **(3 poin)**
2. Turunkan hukum
   \(\mathcal L(N(A)\mid N(A\cup B)=n)\). **(3 poin)**
3. Setiap titik dari \(N\) diberi tanda merah secara independen dengan peluang
   \(p\in[0,1]\), dan biru selainnya. Buktikan, melalui fungsi pembangkit,
   bahwa ukuran merah dan biru adalah ukuran acak Poisson independen dengan
   intensitas \(p\mu\) dan \((1-p)\mu\). Selanjutnya, jika
   \(N_1,N_2\) adalah ukuran acak Poisson independen berintensitas
   \(\mu_1,\mu_2\), buktikan bahwa \(N_1+N_2\) berintensitas
   \(\mu_1+\mu_2\). **(3 poin)**
4. Jika \(\mu(C)=\infty\), apa nilai \(N(C)\) hampir pasti? Jelaskan singkat
   mengapa pernyataan “hingga secara lokal” masih memerlukan kelas lokal dan
   syarat pada \(\mu\). **(1 poin)**

#### Rubrik Soal 6 {#assessment.o009.d30.cumulative.form-a.problem.06.rubric}

| Komponen | Poin |
|---|---:|
| Fungsi pembangkit dan tiga momen | 3 |
| Penurunan hukum binomial bersyarat | 3 |
| Faktorisasi penipisan, identifikasi dua PRM, dan hukum superposisi | 3 |
| Hitungan intensitas tak hingga dan kualifikasi lokal | 1 |

#### Petunjuk 1 {#assessment.o009.d30.cumulative.form-a.problem.06.hint.01}

Gunakan independensi \(N(A)\) dan \(N(B)\). Untuk bagian bersyarat, bagi
peluang dua peubah Poisson dengan peluang bahwa jumlahnya Poisson
berparameter \(a+b\).

#### Petunjuk 2 {#assessment.o009.d30.cumulative.form-a.problem.06.hint.02}

Bersyarat pada \(N(C)=m\), pasangan hitungan merah-biru pada \(C\) bersifat
multinomial. Hilangkan pengondisian terhadap peubah
\(\operatorname{Poisson}(\mu(C))\), lalu periksa apakah fungsi pembangkit
bersama berfaktor. Untuk superposisi, kalikan fungsional Laplace dua ukuran
acak yang independen.

#### Jawaban ringkas {#assessment.o009.d30.cumulative.form-a.problem.06.answer}

\[
\mathbb E[s^{N(A)}t^{N(B)}]
=\exp\{a(s-1)+b(t-1)\}.
\]
Rataan dan varians \(N(A)\) sama dengan \(a\), sedangkan kovarians dua
hitungan itu nol. Bersyarat pada \(N(A\cup B)=n\),
\[
N(A)\sim\operatorname{Binomial}
\left(n,\frac{a}{a+b}\right).
\]
Penipisan menghasilkan dua ukuran acak Poisson independen dengan intensitas
\(p\mu\) dan \((1-p)\mu\), sedangkan superposisi dua ukuran acak Poisson
independen mempunyai intensitas jumlahnya. Jika \(\mu(C)=\infty\), maka
\(N(C)=\infty\) hampir pasti; keterhinggaan lokal hanya mengikuti bila
\(\mu\) hingga pada kelas himpunan lokal yang dinyatakan.

#### Penyelesaian lengkap {#assessment.o009.d30.cumulative.form-a.problem.06.solution}

Karena \(A\cap B=\varnothing\), hitungan \(N(A)\) dan \(N(B)\) independen.
Fungsi pembangkit peubah Poisson berparameter \(\alpha\) adalah
\(\exp\{\alpha(z-1)\}\). Maka
\[
\mathbb E[s^{N(A)}t^{N(B)}]
=\mathbb E[s^{N(A)}]\mathbb E[t^{N(B)}]
=\exp\{a(s-1)+b(t-1)\}.
\]
Sifat momen Poisson memberi
\[
\mathbb EN(A)=a,\qquad
\operatorname{Var}N(A)=a,
\qquad
\operatorname{Cov}(N(A),N(B))=0,
\]
dengan kovarians nol berasal dari independensi.

Untuk \(0\le k\le n\),
\[
\begin{aligned}
&\mathbb P(N(A)=k\mid N(A\cup B)=n)\\
&\quad=
\frac{
 e^{-a}a^k/k!\;e^{-b}b^{n-k}/(n-k)!
}{
 e^{-(a+b)}(a+b)^n/n!
}\\
&\quad=
\binom nk
\left(\frac a{a+b}\right)^k
\left(\frac b{a+b}\right)^{n-k}.
\end{aligned}
\]
Jadi hukum bersyaratnya binomial dengan parameter
\((n,a/(a+b))\). Secara lebih lengkap,
\((N(A),N(B))\) bersyarat pada jumlah \(n\) adalah multinomial dengan dua
sel.

Untuk sebuah \(C\) dengan \(\mu(C)<\infty\), tulis \(N_R(C)\) dan \(N_B(C)\)
untuk hitungan merah dan biru. Bersyarat pada \(N(C)=m\),
\[
\mathbb E[s^{N_R(C)}t^{N_B(C)}\mid N(C)=m]
=(ps+(1-p)t)^m.
\]
Mengambil ekspektasi terhadap \(N(C)\sim\operatorname{Poisson}(\mu(C))\)
memberi
\[
\begin{aligned}
\mathbb E[s^{N_R(C)}t^{N_B(C)}]
&=\exp\{\mu(C)(ps+(1-p)t-1)\}\\
&=\exp\{p\mu(C)(s-1)\}
  \exp\{(1-p)\mu(C)(t-1)\}.
\end{aligned}
\]
Faktorisasi menunjukkan bahwa dua hitungan itu independen dan masing-masing
Poisson dengan parameter \(p\mu(C)\) serta \((1-p)\mu(C)\). Menerapkan
argumen yang sama secara serentak pada keluarga berhingga himpunan saling
lepas membuktikan sifat inkremen independen dan hukum Poisson untuk kedua
ukuran acak, sekaligus independensi kedua ukuran tersebut. Jadi intensitasnya
adalah \(p\mu\) dan \((1-p)\mu\).

Untuk superposisi, ambil \(f\ge0\) terukur. Independensi \(N_1,N_2\) memberi
\[
\begin{aligned}
\mathbb E\exp\!\left\{-\int f\,d(N_1+N_2)\right\}
&=\prod_{i=1}^2
\mathbb E\exp\!\left\{-\int f\,dN_i\right\}\\
&=\exp\!\left\{
-\int(1-e^{-f})\,d(\mu_1+\mu_2)
\right\}.
\end{aligned}
\]
Ini adalah fungsional Laplace ukuran acak Poisson berintensitas
\(\mu_1+\mu_2\), sehingga \(N_1+N_2\) mempunyai hukum tersebut.

Jika \(\mu(C)=\infty\), sifat σ-terhingga menyediakan
\(C_m\uparrow C\) dengan \(\mu(C_m)<\infty\) dan
\(\mu(C_m)\uparrow\infty\). Untuk setiap bilangan bulat \(K\),
\[
\mathbb P(N(C)\le K)
\le \mathbb P(N(C_m)\le K)\longrightarrow0,
\]
karena parameter Poisson \(\mu(C_m)\) menuju tak hingga. Maka
\(N(C)=\infty\) hampir pasti. Pada ruang topologis, “lokal” harus berarti,
misalnya, himpunan relatif kompak atau himpunan terbatas. Keterhinggaan lokal
memerlukan \(\mu\) hingga pada kelas tersebut; sifat Poisson saja tidak
menentukannya.

---

## Bagian IV — Gerak Brown dan hukum lintasan {#assessment.o009.d30.cumulative.form-a.section.07}

### Soal 7 — Hukum Gaussian, martingal eksponensial, pencapaian, dan variasi kuadratik (14 poin) {#assessment.o009.d30.cumulative.form-a.problem.07}

Misalkan \(B=(B_t)_{t\ge0}\) gerak Brown standar dan
\[
X_t=\alpha t+\sigma B_t,\qquad \sigma>0.
\]
Ambil \(0<s<t\), \(\theta\in\mathbb R\), dan \(a>0\).

1. Tentukan vektor rataan dan matriks kovarians
   \((X_s,X_t)\), lalu turunkan hukum
   \(\mathcal L(X_t\mid X_s=x)\). **(4 poin)**
2. Buktikan bahwa
   \[
   M_t=\exp\!\left\{
   \theta(X_t-\alpha t)-\tfrac12\theta^2\sigma^2t
   \right\}
   \]
   adalah martingal terhadap filtrasi alami Brown yang dilengkapi dan
   kontinu kanan. **(3 poin)**
3. Dengan prinsip refleksi, hitung
   \(\mathbb P(\sup_{0\le u\le t}B_u\ge a)\), lalu turunkan fungsi kepadatan
   waktu pencapaian
   \(T_a=\inf\{u\ge0:B_u=a\}\). **(4 poin)**
4. Untuk partisi seragam \(t_k=kt/n\), definisikan
   \[
   V_n=\sum_{k=1}^n(B_{t_k}-B_{t_{k-1}})^2.
   \]
   Buktikan \(V_n\to t\) dalam \(L^2\). **(3 poin)**

#### Rubrik Soal 7 {#assessment.o009.d30.cumulative.form-a.problem.07.rubric}

| Komponen | Poin |
|---|---:|
| Hukum Gaussian bersama dan hukum bersyarat | 4 |
| Identitas ekspektasi bersyarat martingal eksponensial | 3 |
| Prinsip refleksi, fungsi distribusi, dan diferensiasi yang benar | 4 |
| Rataan dan varians variasi kuadratik serta kesimpulan \(L^2\) | 3 |

#### Petunjuk 1 {#assessment.o009.d30.cumulative.form-a.problem.07.hint.01}

Tuliskan
\(X_t=X_s+\alpha(t-s)+\sigma(B_t-B_s)\), dan gunakan bahwa inkremen terakhir
bebas dari \(\mathcal F_s\). Gunakan cara yang sama untuk rasio
\(M_t/M_s\).

#### Petunjuk 2 {#assessment.o009.d30.cumulative.form-a.problem.07.hint.02}

Prinsip refleksi memberi faktor dua di ekor normal. Untuk variasi kuadratik,
inkremen partisi independen dan berdistribusi
\(N(0,t/n)\); jika \(Z\sim N(0,v)\), maka
\(\operatorname{Var}(Z^2)=2v^2\).

#### Jawaban ringkas {#assessment.o009.d30.cumulative.form-a.problem.07.answer}

Vektor rataan \((X_s,X_t)\) adalah \((\alpha s,\alpha t)\), dengan matriks
kovarians
\[
\sigma^2
\begin{pmatrix}
s&s\\
s&t
\end{pmatrix}.
\]
Hukum bersyaratnya
\[
X_t\mid X_s=x\sim
N\!\left(x+\alpha(t-s),\,\sigma^2(t-s)\right).
\]
Proses \(M\) adalah martingal karena faktor inkremen eksponensialnya bebas
dari masa lalu dan memiliki rataan satu. Selain itu,
\[
\mathbb P(T_a\le t)
=2\!\left[1-\Phi\!\left(\frac a{\sqrt t}\right)\right],
\qquad
f_{T_a}(t)=
\frac{a}{\sqrt{2\pi}t^{3/2}}
e^{-a^2/(2t)}.
\]
Terakhir,
\(\mathbb EV_n=t\) dan
\(\operatorname{Var}(V_n)=2t^2/n\), sehingga \(V_n\to t\) dalam \(L^2\).

#### Penyelesaian lengkap {#assessment.o009.d30.cumulative.form-a.problem.07.solution}

Karena gerak Brown Gaussian, \((X_s,X_t)\) juga Gaussian. Rataannya adalah
\[
\mathbb E(X_s,X_t)=(\alpha s,\alpha t).
\]
Kovarians gerak Brown memenuhi
\(\operatorname{Cov}(B_s,B_t)=\min(s,t)=s\), sehingga
\[
\operatorname{Cov}(X_s,X_t)
=\sigma^2
\begin{pmatrix}
s&s\\
s&t
\end{pmatrix}.
\]
Lebih langsung,
\[
X_t=X_s+\alpha(t-s)+\sigma(B_t-B_s),
\]
dan \(B_t-B_s\sim N(0,t-s)\) bebas dari \(X_s\). Maka satu versi kernel
bersyarat Gaussian adalah
\[
X_t\mid X_s=x\sim
N\!\left(x+\alpha(t-s),\sigma^2(t-s)\right).
\]

Karena \(X_t-\alpha t=\sigma B_t\),
\[
M_t=\exp\{\theta\sigma B_t-\tfrac12\theta^2\sigma^2t\}.
\]
Untuk \(0\le s<t\),
\[
\frac{M_t}{M_s}
=\exp\!\left\{
\theta\sigma(B_t-B_s)
-\tfrac12\theta^2\sigma^2(t-s)
\right\}.
\]
Faktor ini bebas dari \(\mathcal F_s\). Fungsi pembangkit momen normal
memberi faktor tersebut rataan satu. Karena \(M_s\) terukur terhadap
\(\mathcal F_s\),
\[
\mathbb E(M_t\mid\mathcal F_s)
=M_s\,
\mathbb E(M_t/M_s\mid\mathcal F_s)
=M_s.
\]
Proses positif ini terintegralkan karena \(\mathbb EM_t=1\), jadi ia benar
martingal.

Kontinuitas lintasan memberi
\(\{T_a\le t\}=\{\sup_{0\le u\le t}B_u\ge a\}\). Prinsip refleksi memberi
\[
\mathbb P(T_a\le t)
=2\mathbb P(B_t\ge a)
=2\!\left[
1-\Phi\!\left(\frac a{\sqrt t}\right)
\right].
\]
Untuk \(t>0\), diferensiasi menghasilkan
\[
\begin{aligned}
f_{T_a}(t)
&=2\,
\phi\!\left(\frac a{\sqrt t}\right)
\frac{a}{2t^{3/2}}\\
&=\frac{a}{\sqrt{2\pi}t^{3/2}}
\exp\!\left(-\frac{a^2}{2t}\right).
\end{aligned}
\]
Fungsi distribusi menuju satu ketika \(t\to\infty\), konsisten dengan
\(T_a<\infty\) hampir pasti.

Tuliskan
\(\Delta_{k,n}=B_{kt/n}-B_{(k-1)t/n}\). Inkremen ini independen dan
\(\Delta_{k,n}\sim N(0,t/n)\). Maka
\[
\mathbb EV_n
=\sum_{k=1}^n\mathbb E\Delta_{k,n}^2
=n\frac tn=t.
\]
Independensi kuadrat serta
\(\operatorname{Var}(\Delta_{k,n}^2)=2(t/n)^2\) memberi
\[
\operatorname{Var}(V_n)
=n\,2\left(\frac tn\right)^2
=\frac{2t^2}{n}.
\]
Karena
\[
\mathbb E|V_n-t|^2
=\operatorname{Var}(V_n)
\longrightarrow0,
\]
diperoleh \(V_n\to t\) dalam \(L^2\), dan karena itu juga dalam
probabilitas. Untuk proses \(X\), perhitungan serupa memberi variasi
kuadratik \(\sigma^2t\); bagian hanyutan berhingga-variasi tidak
menyumbang pada limit kuadratik.

### Soal 8 — Jembatan Brown, versi bersyarat, dan syarat menuju teorema Donsker (10 poin) {#assessment.o009.d30.cumulative.form-a.problem.08}

Definisikan jembatan Brown
\[
\beta_t=B_t-tB_1,\qquad 0\le t\le1.
\]
Secara terpisah, ambil \(U\sim\operatorname{Unif}[0,1]\) dan proses kontinu
\[
Z_n(t)=\bigl(1-n|t-U|\bigr)_+,\qquad 0\le t\le1.
\]

1. Buktikan bahwa \(\beta\) adalah proses Gaussian terpusat dengan
   \[
   \operatorname{Cov}(\beta_s,\beta_t)=\min(s,t)-st.
   \]
   Buktikan pula bahwa setiap vektor berdimensi hingga dari \(\beta\) bebas
   dari \(B_1\). **(4 poin)**
2. Bangun satu kernel bersyarat untuk hukum lintasan
   \(B\mid B_1=y\), dan jelaskan status nilai kernel pada \(y=0\).
   **(2 poin)**
3. Buktikan bahwa semua distribusi berdimensi hingga \(Z_n\) konvergen ke
   proses nol, tetapi \(Z_n\) tidak konvergen lemah ke nol dalam
   \(C[0,1]\) dengan norma supremum. Identifikasi hipotesis yang hilang.
   **(3 poin)**
4. Jelaskan dalam satu pernyataan tepat mengapa CLT berdimensi hingga untuk
   gerak acak belum merupakan teorema Donsker. **(1 poin)**

#### Rubrik Soal 8 {#assessment.o009.d30.cumulative.form-a.problem.08.rubric}

| Komponen | Poin |
|---|---:|
| Gaussianitas, kovarians jembatan, dan independensi dari \(B_1\) | 4 |
| Kernel Gaussian pada ruang lintasan dan disiplin versi pada nol | 2 |
| Konvergensi FDD, saksi norma supremum, dan keketatan yang hilang | 3 |
| Perbedaan CLT/FDD dan Donsker beserta topologi lintasan | 1 |

#### Petunjuk 1 {#assessment.o009.d30.cumulative.form-a.problem.08.hint.01}

Hitung
\(\operatorname{Cov}(B_s-sB_1,B_t-tB_1)\) dan
\(\operatorname{Cov}(\beta_t,B_1)\). Untuk vektor Gaussian bersama,
kovarians silang nol menyiratkan independensi.

#### Petunjuk 2 {#assessment.o009.d30.cumulative.form-a.problem.08.hint.02}

Untuk waktu tetap \(t_1,\ldots,t_k\),
\[
\mathbb P\!\left(\max_jZ_n(t_j)>0\right)
\le\sum_{j=1}^k\mathbb P(|U-t_j|<1/n).
\]
Setelah itu, hitung \(\|Z_n\|_\infty\).

#### Jawaban ringkas {#assessment.o009.d30.cumulative.form-a.problem.08.answer}

Jembatan \(\beta\) Gaussian terpusat dengan kovarians
\(\min(s,t)-st\), dan bebas dari \(B_1\). Satu kernel bersyarat ialah hukum
proses \(t\mapsto ty+\beta_t\); pada \(y=0\) ini memberi hukum jembatan,
tetapi nilainya di titik pengondisian nol merupakan pilihan versi yang
dipilih secara kontinu.
Semua FDD \(Z_n\) menuju nol, namun \(\|Z_n\|_\infty=1\) hampir pasti, jadi
tidak ada konvergensi lemah ke nol dalam \(C[0,1]\). Keketatan hukum lintasan
hilang. Demikian pula, CLT/FDD untuk gerak acak harus dilengkapi keketatan
pada ruang dan topologi lintasan yang dinyatakan agar menjadi Donsker.

#### Penyelesaian lengkap {#assessment.o009.d30.cumulative.form-a.problem.08.solution}

Setiap vektor dari \(\beta\) merupakan transformasi linear vektor Gaussian
dari \(B\), jadi \(\beta\) Gaussian. Rataannya nol. Untuk
\(s,t\in[0,1]\),
\[
\begin{aligned}
\operatorname{Cov}(\beta_s,\beta_t)
&=\operatorname{Cov}(B_s-sB_1,B_t-tB_1)\\
&=\min(s,t)-t\,s-s\,t+st\\
&=\min(s,t)-st.
\end{aligned}
\]
Selain itu,
\[
\operatorname{Cov}(\beta_t,B_1)
=\operatorname{Cov}(B_t-tB_1,B_1)
=t-t=0.
\]
Untuk waktu \(t_1,\ldots,t_k\), vektor
\((\beta_{t_1},\ldots,\beta_{t_k},B_1)\) Gaussian bersama. Seluruh kovarians
silang antara bagian pertama dan \(B_1\) nol, sehingga vektor jembatan itu
bebas dari \(B_1\). Karena ini berlaku untuk setiap keluarga berhingga,
proses \(\beta\) bebas dari peubah \(B_1\) dalam arti aljabar-σ yang
dihasilkan koordinatnya.

Definisikan, untuk \(y\in\mathbb R\), ukuran peluang \(K(y,\cdot)\) pada
\(C[0,1]\) sebagai hukum lintasan
\[
t\longmapsto ty+\beta_t.
\]
Pemetaan \(y\mapsto K(y,\cdot)\) adalah kernel Borel; misalnya
\((y,f)\mapsto(t\mapsto ty+f(t))\) kontinu pada
\(\mathbb R\times C[0,1]\). Karena
\[
B_t=tB_1+\beta_t
\]
dan \(\beta\) bebas dari \(B_1\), kernel ini memenuhi disintegrasi dan
merupakan satu distribusi bersyarat reguler bagi hukum lintasan \(B\) diberi
\(B_1=y\). Pada \(y=0\), \(K(0,\cdot)\) adalah hukum \(\beta\). Namun
\(\mathbb P(B_1=0)=0\), sehingga hukum gabungan hanya menentukan kernel
\(\mathcal L(B_1)\)-hampir di mana-mana. Rumus Gaussian yang kontinu dalam
\(y\) memilih versi alami di nol; ia bukan nilai yang dipaksa secara
titik-demi-titik oleh definisi rasio probabilitas.

Untuk waktu tetap \(t_1,\ldots,t_k\),
\[
\begin{aligned}
\mathbb P\!\left(
(Z_n(t_1),\ldots,Z_n(t_k))\ne(0,\ldots,0)
\right)
&\le\sum_{j=1}^k\mathbb P(|U-t_j|<1/n)\\
&\le\frac{2k}{n}\longrightarrow0.
\end{aligned}
\]
Jadi setiap vektor berdimensi hingga konvergen dalam probabilitas, dan
karena itu dalam distribusi, ke vektor nol. Akan tetapi, setiap lintasan
mencapai puncak pada \(t=U\), sehingga
\[
\|Z_n\|_\infty=1
\quad\text{hampir pasti}.
\]
Jika \(Z_n\Rightarrow0\) dalam \(C[0,1]\), teorema pemetaan kontinu untuk
fungsi kontinu \(f\mapsto\|f\|_\infty\) akan memberi
\(\|Z_n\|_\infty\Rightarrow0\), suatu kontradiksi. Keluarga hukum ini tidak
ketat; puncaknya makin sempit tanpa menghilang dalam norma supremum.

Teorema Donsker adalah pernyataan konvergensi lemah pada ruang lintasan
tertentu—misalnya \(C[0,1]\) untuk interpolasi poligonal atau
\(D[0,1]\) dengan topologi Skorokhod untuk proses tangga. CLT pada satu atau
beberapa waktu hanya memberi konvergensi distribusi berdimensi hingga.
Untuk menaikkannya menjadi Donsker masih diperlukan keketatan pada topologi
yang disebut dan identifikasi setiap limit subsekuensial sebagai hukum gerak
Brown.

---

## Rekapitulasi nilai dan pemeriksaan kelengkapan {#assessment.o009.d30.cumulative.form-a.section.08}

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

Formulir mencakup seluruh domain wajib: landasan probabilitas
teoretis-ukuran; mode konvergensi dan pembacaan prasyarat LLN/CLT; nilai
harapan bersyarat dan kernel; martingal dan penghentian; rantai Markov
diskret, CTMC, proses serta ukuran acak Poisson; dan gerak Brown beserta
hukum lintasan. Setiap soal mempunyai ID, rubrik, dua petunjuk progresif,
jawaban ringkas, dan penyelesaian lengkap.

## Hak dan provenans {#assessment.o009.d30.cumulative.form-a.section.09}

Teks **Penilaian Kumulatif D30 — Formulir A**, termasuk soal, data numerik,
rubrik, petunjuk, jawaban, dan penyelesaian, merupakan materi asli berbahasa
Indonesia yang disusun untuk edisi ini. Sejauh hak baru timbul, materi ini
dilisensikan di bawah
[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
(CC BY 4.0). ID hak stabilnya adalah
<code>rights.o009.assessment.cumulative.form-a.cc-by-4.0</code>.

Penyusunan dibantu oleh **OpenAI Codex gpt-5.6-sol, Ultra.** atas arahan
pengguna. Provenans ruang
lingkup dan istilah hasil belajar berasal dari indeks kurikulum lokal D30 dan
registri hasil belajar O009/D30. Disiplin hipotesis—khususnya pembedaan
keterbatasan \(L^1\) dari keterintegralan seragam, versi kernel pada himpunan
nol, syarat penghentian opsional, periodisitas, ketidakmeledakan CTMC, serta
FDD versus hukum lintasan—diperiksa terhadap unit audit hipotesis lokal.
Seluruh formulasi penilaian dan penyelesaiannya ditulis baru; hasil-hasil
matematis standar disebut sebagai teorema, bukan sebagai salinan prosa donor.

Lisensi CC BY 4.0 ini hanya berlaku pada kontribusi baru dalam formulir ini.
Ia tidak melisensikan ulang materi Random, QuantEcon, Žitković, MathJax, atau
komponen lain dalam edisi gabungan, dan tidak menyiratkan dukungan atau
pengesahan dari penulis maupun lembaga sumber.
