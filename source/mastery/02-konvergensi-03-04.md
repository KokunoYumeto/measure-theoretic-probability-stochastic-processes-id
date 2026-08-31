---
title: "Latihan penguasaan konvergensi dan teorema limit: butir 03–04"
lang: id-ID
author:
  - "Codex (penulisan materi asli atas arahan pengguna)"
authoring:
  course_id: "o009"
  unit_id: "unit.o009.mastery.convergence.03-04"
  category_id: "category.o009.mastery.convergence-limit-theorems"
  target_locale: "id-ID"
  source_type: "original-mastery"
  rights_ids:
    - "rights.o009.mastery.convergence.03.cc-by-4.0"
    - "rights.o009.mastery.convergence.04.cc-by-4.0"
  license: "CC-BY-4.0"
  model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."
provenans:
  created: "2026-08-30"
  format_exemplar: "../original/04-audit-hipotesis-proses-stokastik.md"
  statement_origin: "Dua soal dan seluruh penyelesaiannya disusun secara asli untuk unit penguasaan ini."
mastery_bindings:
  - root_id: "mastery.o009.convergence.03"
    prerequisite_ids:
      - "theory.o009.dist.convergence.fundamental-limit-theorems"
      - "theory.o009.prob.convergence.random-variables"
    outcome_ids:
      - "outcome.o009.convergence.03.second-order-delta-method"
  - root_id: "mastery.o009.convergence.04"
    prerequisite_ids:
      - "theory.o009.prob.convergence.random-variables"
      - "theory.o009.expect.uniform-integrability.convergence"
    outcome_ids:
      - "outcome.o009.convergence.04.rare-spike-phase-diagram"
---

# Latihan penguasaan konvergensi dan teorema limit: butir 03–04

::: {#mastery.o009.convergence.03 .mastery-item data-category-item="03" data-prerequisite-ids="theory.o009.dist.convergence.fundamental-limit-theorems theory.o009.prob.convergence.random-variables" data-outcome-ids="outcome.o009.convergence.03.second-order-delta-method" data-rights-id="rights.o009.mastery.convergence.03.cc-by-4.0"}

## 03. Metode delta orde kedua dan ketergantungan pada limit

**Ikatan prasyarat.**
[`theory.o009.dist.convergence.fundamental-limit-theorems`](../theory/dist/Convergence.html)
dan
[`theory.o009.prob.convergence.random-variables`](../theory/prob/Convergence.html#lim)
(teorema limit pusat, konvergensi dalam distribusi, pemetaan kontinu, dan
teorema Slutsky).

**Ikatan capaian.**
`outcome.o009.convergence.03.second-order-delta-method`: menerapkan ekspansi
Taylor stokastik pada titik dengan turunan pertama nol, memilih skala orde
kedua yang tepat, dan mengidentifikasi ketergantungan koordinat limit.

::: {#mastery.o009.convergence.03.exercise .mastery-exercise}

### Soal

Misalkan $X_1,X_2,\ldots$ iid dengan
$\mathbb E[X_1]=\mu$ dan
$\operatorname{Var}(X_1)=\sigma^2\in(0,\infty)$, serta tuliskan
$\overline X_n=n^{-1}\sum_{k=1}^nX_k$. Misalkan
$g:\mathbb R\to\mathbb R$ dua kali terdiferensialkan pada suatu lingkungan
terbuka dari $\mu$, dengan

$$
g'(\mu)=0
\qquad\text{dan}\qquad
g''(\mu)\ne0.
$$

Definisikan

$$
T_n=\sqrt n\,(\overline X_n-\mu),
\qquad
Q_n=n\{g(\overline X_n)-g(\mu)\}.
$$

1. Buktikan bahwa $T_n\Rightarrow\sigma Z$ untuk $Z\sim\mathcal N(0,1)$
   dan bahwa $(T_n)$ terbatas dalam probabilitas.
2. Buktikan limit gabungan metode delta orde kedua

   $$
   (T_n,Q_n)
   \ \xRightarrow[n\to\infty]{}\
   \left(\sigma Z,\frac{g''(\mu)\sigma^2}{2}Z^2\right).
   $$

3. Identifikasi hukum marginal koordinat kedua. Tunjukkan bahwa kedua
   koordinat limit memiliki kovarians nol tetapi tidak independen. Jelaskan
   pula mengapa skala $\sqrt n$ yang biasa pada metode delta orde pertama
   menghasilkan limit degenerat bagi $g(\overline X_n)-g(\mu)$, sedangkan
   skala $n$ menghasilkan limit tak degenerat.

:::

::: {#mastery.o009.convergence.03.hint.01 .mastery-hint}

### Petunjuk 01

Terapkan teorema limit pusat pada $T_n$. Ingat bahwa setiap barisan yang
konvergen dalam distribusi terbatas dalam probabilitas; akibatnya
$T_n=O_{\mathbb P}(1)$ dan $\overline X_n-\mu=T_n/\sqrt n\to0$ dalam
probabilitas.

:::

::: {#mastery.o009.convergence.03.hint.02 .mastery-hint}

### Petunjuk 02

Gunakan bentuk Peano dari ekspansi Taylor:

$$
g(\mu+h)-g(\mu)
=\frac{g''(\mu)}2h^2+h^2r(h),
\qquad r(h)\to0\quad(h\to0).
$$

Setelah mengambil $h=\overline X_n-\mu$, tunjukkan bahwa
$T_n^2r(\overline X_n-\mu)=o_{\mathbb P}(1)$.

:::

::: {#mastery.o009.convergence.03.hint.03 .mastery-hint}

### Petunjuk 03

Gunakan pemetaan kontinu pada $x\mapsto(x,g''(\mu)x^2/2)$ dan kemudian
Slutsky. Jika limit pertama dinotasikan $U=\sigma Z$, periksa identitas
$V=g''(\mu)U^2/2$ untuk limit kedua. Bandingkan identitas ini dengan
$\mathbb E[Z^3]=0$.

:::

::: {#mastery.o009.convergence.03.answer .mastery-answer}

### Jawaban singkat

Teorema limit pusat memberi $T_n\Rightarrow\sigma Z$ dan
$T_n=O_{\mathbb P}(1)$. Ekspansi Taylor orde kedua menghasilkan

$$
Q_n=\frac{g''(\mu)}2T_n^2+o_{\mathbb P}(1),
$$

sehingga

$$
(T_n,Q_n)\Rightarrow
\left(\sigma Z,\frac{g''(\mu)\sigma^2}{2}Z^2\right).
$$

Koordinat kedua berdistribusi
$\{g''(\mu)\sigma^2/2\}\chi_1^2$. Kedua koordinat limit berkovarians nol,
tetapi tidak independen karena koordinat kedua adalah fungsi kuadrat tak
konstan dari koordinat pertama. Pada skala $\sqrt n$ transformasi itu menuju
nol dalam probabilitas; skala $n$ mempertahankan suku kuadrat pertama yang
tidak lenyap.

:::

::: {#mastery.o009.convergence.03.solution .mastery-solution}

### Penyelesaian

Karena $X_k$ iid dengan rataan $\mu$ dan varians hingga positif, teorema
limit pusat memberi

$$
T_n=\frac{\sum_{k=1}^n(X_k-\mu)}{\sqrt n}
\Rightarrow\sigma Z,
\qquad Z\sim\mathcal N(0,1).
$$

Konvergensi dalam distribusi menyiratkan keterbatasan dalam probabilitas,
jadi $T_n=O_{\mathbb P}(1)$. Karena $n^{-1/2}\to0$, diperoleh

$$
\overline X_n-\mu=\frac{T_n}{\sqrt n}
\longrightarrow0
\quad\text{dalam probabilitas}.
$$

Asumsi diferensiabilitas orde dua di $\mu$ dan $g'(\mu)=0$ memberikan
ekspansi Taylor dalam bentuk Peano

$$
g(\mu+h)-g(\mu)
=\frac{g''(\mu)}2h^2+h^2r(h),
\qquad r(h)\longrightarrow0
\quad(h\to0).
$$

Dengan $h=\overline X_n-\mu$, kalikan kedua ruas dengan $n$ untuk memperoleh

$$
Q_n
=\frac{g''(\mu)}2T_n^2
+T_n^2r(\overline X_n-\mu).
$$

Karena $\overline X_n-\mu\to0$ dalam probabilitas dan $r(h)\to0$, pemetaan
kontinu lokal memberi
$r(\overline X_n-\mu)=o_{\mathbb P}(1)$. Selanjutnya
$T_n^2=O_{\mathbb P}(1)$, dan hasil kali suatu $O_{\mathbb P}(1)$ dengan
suatu $o_{\mathbb P}(1)$ adalah $o_{\mathbb P}(1)$. Dengan demikian,

$$
Q_n=\frac{g''(\mu)}2T_n^2+o_{\mathbb P}(1).
$$

Teorema pemetaan kontinu memberi

$$
\left(T_n,\frac{g''(\mu)}2T_n^2\right)
\Rightarrow
\left(\sigma Z,\frac{g''(\mu)\sigma^2}{2}Z^2\right).
$$

Menambahkan sisa $o_{\mathbb P}(1)$ pada koordinat kedua dan menerapkan
Slutsky membuktikan limit gabungan yang diminta.

Tuliskan

$$
U=\sigma Z,
\qquad
V=\frac{g''(\mu)\sigma^2}{2}Z^2.
$$

Karena $Z^2\sim\chi_1^2$, diperoleh
$V\overset d=\{g''(\mu)\sigma^2/2\}\chi_1^2$; bila $g''(\mu)<0$, ini adalah
kelipatan negatif dari peubah khi-kuadrat. Selain itu,

$$
\operatorname{Cov}(U,V)
=\mathbb E[UV]-\mathbb E[U]\mathbb E[V]
=\frac{g''(\mu)\sigma^3}{2}\mathbb E[Z^3]
=0.
$$

Namun, $V=g''(\mu)U^2/2$. Jadi $V$ adalah fungsi terukur tak konstan dari
$U$ dan bersifat nondegenerat karena $g''(\mu)\ne0$ dan $\sigma>0$. Jika
$U$ dan $V$ independen, maka $V$, yang terukur terhadap $U$, harus independen
dari dirinya sendiri dan karenanya degenerat; ini kontradiksi. Jadi kovarians
nol di sini tidak menyiratkan independensi.

Akhirnya, dari representasi $Q_n=O_{\mathbb P}(1)$ diperoleh

$$
\sqrt n\{g(\overline X_n)-g(\mu)\}
=\frac{Q_n}{\sqrt n}
\longrightarrow0
\quad\text{dalam probabilitas}.
$$

Skala metode delta orde pertama menjadi degenerat karena koefisien linear
$g'(\mu)$ nol. Skala $n$ justru mempertahankan suku kuadrat, yang berlimit
pada kelipatan tak nol dari $Z^2$.

:::

**Hak dan provenans.** `rights.o009.mastery.convergence.03.cc-by-4.0`:
soal, petunjuk, jawaban, dan penyelesaian ini merupakan materi asli, bukan
salinan atau adaptasi latihan pada halaman teori yang diikat. Atribusi:
“Codex (penulisan materi asli atas arahan pengguna), 2026”. Materi dilisensikan
di bawah [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

:::

::: {#mastery.o009.convergence.04 .mastery-item data-category-item="04" data-prerequisite-ids="theory.o009.prob.convergence.random-variables theory.o009.expect.uniform-integrability.convergence" data-outcome-ids="outcome.o009.convergence.04.rare-spike-phase-diagram" data-rights-id="rights.o009.mastery.convergence.04.cc-by-4.0"}

## 04. Diagram fase lonjakan langka dan konvergensi momen

**Ikatan prasyarat.**
[`theory.o009.prob.convergence.random-variables`](../theory/prob/Convergence.html#lim)
dan
[`theory.o009.expect.uniform-integrability.convergence`](../theory/expect/Uniform.html#con)
(konvergensi hampir pasti, dalam probabilitas, dan keterintegralan seragam).

**Ikatan capaian.**
`outcome.o009.convergence.04.rare-spike-phase-diagram`: menentukan ambang
eksak bagi konvergensi $L^p$, keterbatasan momen, dan keterintegralan seragam,
serta mendiagnosis kegagalan pertukaran limit dengan ekspektasi.

::: {#mastery.o009.convergence.04.exercise .mastery-exercise}

### Soal

Pada ruang probabilitas yang memuat $U\sim\operatorname{Unif}(0,1)$, ambil
$\alpha,\beta>0$ dan definisikan

$$
X_n=n^\alpha\mathbf 1_{\{U\le n^{-\beta}\}},
\qquad n\ge1.
$$

Untuk suatu $p>0$ yang tetap:

1. buktikan bahwa $X_n\to0$ hampir pasti, dan simpulkan konvergensi dalam
   probabilitas serta dalam distribusi;
2. tentukan syarat perlu dan cukup pada $(\alpha,\beta,p)$ untuk
   $X_n\to0$ dalam $L^p$;
3. tentukan syarat perlu dan cukup agar
   $\sup_n\mathbb E|X_n|^p<\infty$;
4. tentukan syarat perlu dan cukup agar keluarga
   $(|X_n|^p)_{n\ge1}$ terintegralkan seragam.

Terakhir, jelaskan apa yang terjadi pada garis batas $\alpha p=\beta$ dan
mengapa kasus itu menghalangi penarikan kesimpulan konvergensi momen hanya dari
konvergensi hampir pasti dan keterbatasan momen.

:::

::: {#mastery.o009.convergence.04.hint.01 .mastery-hint}

### Petunjuk 01

Untuk setiap $U>0$, ketaksamaan $U\le n^{-\beta}$ akhirnya gagal. Di sisi
lain, hitung tepat

$$
\mathbb P(X_n\ne0)
\quad\text{dan}\quad
\mathbb E|X_n|^p.
$$

Pangkat tunggal $\alpha p-\beta$ membagi seluruh ruang parameter menjadi tiga
rezim.

:::

::: {#mastery.o009.convergence.04.hint.02 .mastery-hint}

### Petunjuk 02

Tuliskan $W_n=|X_n|^p$. Untuk $K>0$, tidak diperlukan suatu teorema abstrak;
ekor keterintegralan seragam dapat dihitung persis:

$$
\mathbb E[W_n\mathbf1_{\{W_n>K\}}]
=n^{\alpha p-\beta}\mathbf1_{\{n^{\alpha p}>K\}}.
$$

Ambil supremum terhadap $n$, lalu biarkan $K\to\infty$.

:::

::: {#mastery.o009.convergence.04.answer .mastery-answer}

### Jawaban singkat

Selalu berlaku $X_n\to0$ hampir pasti, dalam probabilitas, dan dalam
distribusi. Selanjutnya,

$$
X_n\to0\text{ dalam }L^p
\iff \alpha p<\beta,
$$

$$
\sup_n\mathbb E|X_n|^p<\infty
\iff \alpha p\le\beta,
$$

dan

$$
(|X_n|^p)_{n\ge1}\text{ terintegralkan seragam}
\iff \alpha p<\beta.
$$

Pada batas $\alpha p=\beta$, momen ke-$p$ selalu sama dengan $1$, tetapi
$X_n\to0$ hampir pasti; keluarga momen itu terbatas namun tidak terintegralkan
seragam.

:::

::: {#mastery.o009.convergence.04.solution .mastery-solution}

### Penyelesaian

Jika $U>0$, pilih $n_0$ sedemikian sehingga $n^{-\beta}<U$ untuk semua
$n\ge n_0$. Maka $X_n=0$ untuk semua $n\ge n_0$. Karena
$\mathbb P(U>0)=1$, diperoleh $X_n\to0$ hampir pasti. Konvergensi hampir pasti
menyiratkan konvergensi dalam probabilitas, kemudian konvergensi dalam
distribusi. Secara langsung, untuk setiap $\varepsilon>0$ dan semua $n$ yang
cukup besar sehingga $n^\alpha>\varepsilon$,

$$
\mathbb P(|X_n|>\varepsilon)
=\mathbb P(U\le n^{-\beta})
=n^{-\beta}\longrightarrow0.
$$

Untuk momen ke-$p$ diperoleh identitas eksak

$$
\mathbb E|X_n|^p
=n^{\alpha p}\mathbb P(U\le n^{-\beta})
=n^{\alpha p-\beta}.
$$

Karena limitnya nol tepat ketika $\alpha p-\beta<0$, maka
$X_n\to0$ dalam $L^p$ tepat ketika $\alpha p<\beta$. Barisan momen tersebut
terbatas tepat ketika eksponennya tidak positif, yakni ketika
$\alpha p\le\beta$.

Tinggal memeriksa keterintegralan seragam. Tetapkan
$W_n=|X_n|^p=n^{\alpha p}\mathbf1_{\{U\le n^{-\beta}\}}$. Untuk setiap
$K>0$,

$$
\mathbb E[W_n\mathbf1_{\{W_n>K\}}]
=n^{\alpha p-\beta}\mathbf1_{\{n^{\alpha p}>K\}}.
$$

Tuliskan $\delta=\alpha p-\beta$. Jika $\delta<0$, maka

$$
\sup_{n\ge1}\mathbb E[W_n\mathbf1_{\{W_n>K\}}]
=\sup_{n>K^{1/(\alpha p)}}n^\delta
\longrightarrow0
\qquad (K\to\infty),
$$

karena untuk pangkat negatif supremum dicapai pada bilangan bulat terkecil di
atas ambang, yang menuju tak hingga bersama $K$. Jadi $(W_n)$ terintegralkan
seragam.

Jika $\delta=0$, untuk setiap $K$ dapat dipilih $n$ dengan
$n^{\alpha p}>K$, dan ekspektasi ekornya sama dengan $1$. Jika $\delta>0$,
ekspektasi ekor bahkan tak terbatas ketika $n\to\infty$. Dengan demikian,
$(|X_n|^p)$ terintegralkan seragam tepat ketika $\alpha p<\beta$.

Pada garis batas $\alpha p=\beta$, lonjakan setinggi $n^\alpha$ terjadi pada
kejadian berpeluang $n^{-\beta}$. Peluang itu menghilang, tetapi tinggi dan
kelangkaannya berimbang sehingga
$\mathbb E|X_n|^p=1$ untuk setiap $n$. Inilah mekanisme hilangnya massa ke
ekor: konvergensi hampir pasti dan keterbatasan momen ke-$p$ tidak cukup untuk
menukar limit dengan ekspektasi. Keterintegralan seragam adalah kendali ekor
yang hilang pada batas tersebut.

:::

**Hak dan provenans.** `rights.o009.mastery.convergence.04.cc-by-4.0`:
soal, petunjuk, jawaban, dan penyelesaian ini merupakan materi asli, bukan
salinan atau adaptasi latihan pada halaman teori yang diikat. Atribusi:
“Codex (penulisan materi asli atas arahan pengguna), 2026”. Materi dilisensikan
di bawah [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

:::
