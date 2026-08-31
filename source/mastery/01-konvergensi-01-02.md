---
title: "Penguasaan konvergensi: subbarisan dan pemetaan diskontinu"
lang: id-ID
author:
  - "Codex (penulisan materi asli atas arahan pengguna)"
authoring:
  course_id: "o009"
  unit_id: "unit.o009.mastery.convergence.01-02"
  target_locale: "id-ID"
  source_type: "original-mastery"
  root_ids:
    - "unit.o009.mastery.convergence.01"
    - "unit.o009.mastery.convergence.02"
  rights_ids:
    - "rights.o009.mastery.convergence.01.cc-by-4.0"
    - "rights.o009.mastery.convergence.02.cc-by-4.0"
  license: "CC-BY-4.0"
  model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."
---

::: {#unit.o009.mastery.convergence.01-02 .original-mastery-set}

# Penguasaan konvergensi: subbarisan dan pemetaan diskontinu

::: {#unit.o009.mastery.convergence.01 .mastery-sequence}

::: {#unit.o009.mastery.convergence.01.bindings .mastery-bindings}
**Ikatan prasyarat.**

- `prerequisite.o009.probability.convergence.modes`: definisi konvergensi
  hampir pasti dan dalam probabilitas pada [kekonvergenan peubah
  acak](../theory/prob/Convergence.html#lim).
- `prerequisite.o009.probability.borel-cantelli.first`: lemma Borel–Cantelli
  pertama dan kriteria jumlah peluang pada [pembahasan
  konvergensi](../theory/prob/Convergence.html#bcl).

**Ikatan hasil.**

- `outcome.o009.convergence.separate-probability-almost-sure`: membangun dan
  mengaudit contoh yang konvergen dalam probabilitas tetapi tidak hampir
  pasti.
- `outcome.o009.convergence.subsequence-characterization`: membuktikan
  karakterisasi konvergensi dalam probabilitas melalui subsubbarisan yang
  konvergen hampir pasti.
:::

::: {#unit.o009.mastery.convergence.01.exercise .exercise}
## Soal 1 — sapuan blok dan prinsip subbarisan

Pada ruang peluang

$$
(\Omega,\mathcal F,\mathbb P)
=\bigl((0,1],\mathcal B((0,1]),\lambda\bigr),
$$

untuk $m\ge 0$ dan $0\le j<2^m$ definisikan

$$
I_{m,j}=\bigl(j2^{-m},(j+1)2^{-m}\bigr].
$$

Setiap $n\ge1$ mempunyai representasi tunggal
$n=2^m+j$ dengan $m\ge0$ dan $0\le j<2^m$. Tetapkan

$$
X_n=\mathbf 1_{I_{m,j}}.
$$

1. Buktikan bahwa $X_n\to0$ dalam probabilitas.
2. Buktikan bahwa $X_n(\omega)$ tidak konvergen ke $0$ untuk satu pun
   $\omega\in(0,1]$. Jelaskan mengapa ini tidak bertentangan dengan bagian
   pertama.
3. Temukan subbarisan eksplisit yang konvergen ke $0$ di setiap titik
   $\omega\in(0,1]$.
4. Buktikan prinsip umum berikut untuk peubah acak bernilai real pada satu
   ruang peluang:

   $$
   Y_n\xrightarrow{\mathbb P}Y
   \quad\Longleftrightarrow\quad
   \text{setiap subbarisan $(Y_{n_k})$ memiliki subsubbarisan yang
   konvergen hampir pasti ke $Y$.}
   $$
:::

::: {#unit.o009.mastery.convergence.01.hint.01 .hint}
**Petunjuk 1.** Untuk $2^m\le n<2^{m+1}$, kejadian $\{X_n=1\}$
mempunyai peluang $2^{-m}$. Sebaliknya, pada setiap tingkat $m$, interval
$I_{m,0},\ldots,I_{m,2^m-1}$ membentuk partisi $(0,1]$. Untuk subbarisan
eksplisit, ikuti selalu sel pertama pada setiap tingkat.
:::

::: {#unit.o009.mastery.convergence.01.hint.02 .hint}
**Petunjuk 2.** Jika $Y_n\to Y$ dalam probabilitas, dari subbarisan sebarang
pilih indeks lebih lanjut sehingga

$$
\mathbb P\bigl(|Y_{n_{k_r}}-Y|>2^{-r}\bigr)\le2^{-r}.
$$

Jumlahkan peluang-peluang ini dan gunakan Borel–Cantelli. Untuk arah balik,
negasikan konvergensi dalam probabilitas dan ekstrak subbarisan yang peluang
penyimpangannya dibatasi dari bawah oleh satu konstanta positif.
:::

::: {#unit.o009.mastery.convergence.01.answer .answer}
**Jawaban ringkas.** Pada blok ke-$m$,
$\mathbb P(X_n=1)=2^{-m}\to0$, tetapi setiap $\omega$ berada dalam tepat satu
sel pada setiap blok, sehingga $X_n(\omega)=1$ tak hingga kali. Subbarisan
$X_{2^k}=\mathbf 1_{(0,2^{-k}]}$ konvergen ke $0$ di setiap titik. Secara
umum, pemilihan peluang yang dapat dijumlahkan dan Borel–Cantelli menghasilkan
subsubbarisan hampir pasti; negasi konvergensi dalam probabilitas memberi
subbarisan yang tidak mungkin memiliki subsubbarisan semacam itu.
:::

::: {#unit.o009.mastery.convergence.01.solution .solution}
**Penyelesaian lengkap.** Jika $2^m\le n<2^{m+1}$ dan $j=n-2^m$, maka
panjang $I_{m,j}$ adalah $2^{-m}$. Jadi, untuk $0<\varepsilon<1$,

$$
\mathbb P(|X_n|>\varepsilon)
=\mathbb P(X_n=1)=2^{-m}.
$$

Ketika $n\to\infty$, tingkat blok $m\to\infty$, sehingga ruas kanan menuju
nol. Untuk $\varepsilon\ge1$, peluang tersebut sudah sama dengan nol. Maka
$X_n\to0$ dalam probabilitas.

Untuk setiap $m$, keluarga
$\{I_{m,j}:0\le j<2^m\}$ merupakan partisi $(0,1]$; konvensi interval terbuka
di kiri dan tertutup di kanan memastikan titik batas pun masuk ke tepat satu
sel. Karena itu, bagi setiap $\omega\in(0,1]$ terdapat tepat satu indeks
$j_m$ sedemikian sehingga

$$
X_{2^m+j_m}(\omega)=1.
$$

Hal ini terjadi untuk setiap $m$, jadi $X_n(\omega)=1$ untuk tak hingga
banyak $n$. Akibatnya $X_n(\omega)$ tidak konvergen ke $0$ untuk satu pun
$\omega$. Tidak ada pertentangan: konvergensi dalam probabilitas mengendalikan
peluang penyimpangan pada setiap indeks secara terpisah, sedangkan konvergensi
hampir pasti mengendalikan seluruh ekor barisan pada lintasan yang sama.

Ambil $n_k=2^k$. Indeks ini selalu memilih $j=0$, sehingga

$$
X_{n_k}=\mathbf 1_{(0,2^{-k}]}.
$$

Jika $\omega>0$, maka $2^{-k}<\omega$ untuk semua $k$ yang cukup besar.
Jadi $X_{n_k}(\omega)=0$ akhirnya, dan subbarisan ini konvergen ke $0$ di
setiap titik.

Sekarang buktikan prinsip umum. Misalkan $Y_n\to Y$ dalam probabilitas dan
ambil subbarisan $(Y_{n_k})$. Subbarisan itu juga konvergen dalam probabilitas
ke $Y$. Secara rekursif pilih

$$
k_1<k_2<\cdots
$$

sedemikian sehingga

$$
\mathbb P(E_r)\le2^{-r},
\qquad
E_r=\{|Y_{n_{k_r}}-Y|>2^{-r}\}.
$$

Pemilihan ini mungkin karena, untuk setiap $r$ tetap, peluang penyimpangan
pada ambang $2^{-r}$ menuju nol. Karena
$\sum_r\mathbb P(E_r)\le\sum_r2^{-r}<\infty$, lemma Borel–Cantelli pertama
memberikan

$$
\mathbb P(E_r\text{ terjadi tak hingga kali})=0.
$$

Di luar kejadian nol itu, untuk semua $r$ yang cukup besar berlaku
$|Y_{n_{k_r}}-Y|\le2^{-r}$; maka
$Y_{n_{k_r}}\to Y$ hampir pasti.

Sebaliknya, andaikan sifat subsubbarisan berlaku tetapi
$Y_n\not\to Y$ dalam probabilitas. Maka ada $\varepsilon>0$, $\delta>0$,
dan subbarisan $(Y_{n_k})$ sehingga

$$
\mathbb P(|Y_{n_k}-Y|>\varepsilon)\ge\delta
\qquad\text{untuk setiap }k.
$$

Menurut sifat yang diasumsikan, subbarisan ini mempunyai subsubbarisan
$(Y_{n_{k_r}})$ yang konvergen hampir pasti ke $Y$. Konvergensi hampir pasti
menyiratkan konvergensi dalam probabilitas, sehingga

$$
\mathbb P(|Y_{n_{k_r}}-Y|>\varepsilon)\longrightarrow0,
$$

bertentangan dengan batas bawah $\delta$. Jadi sifat subsubbarisan juga
menyiratkan $Y_n\to Y$ dalam probabilitas, dan ekuivalensi terbukti.
:::

::: {#unit.o009.mastery.convergence.01.rights .rights-provenance}
**Hak dan provenans.** Soal, kedua petunjuk, jawaban ringkas, dan penyelesaian
lengkap pada akar `unit.o009.mastery.convergence.01` merupakan materi asli
yang ditulis untuk unit ini dan dilepas dengan lisensi
[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
di bawah pengenal
`rights.o009.mastery.convergence.01.cc-by-4.0`. Konsep prasyarat ditautkan
untuk orientasi kurikuler; tidak ada teks soal atau penyelesaian yang
diadaptasi dari sumber donor. Pengungkapan produksi: **OpenAI Codex
gpt-5.6-sol, Ultra**, atas arahan pengguna.
:::

:::

::: {#unit.o009.mastery.convergence.02 .mastery-sequence}

::: {#unit.o009.mastery.convergence.02.bindings .mastery-bindings}
**Ikatan prasyarat.**

- `prerequisite.o009.distribution.weak-convergence`: konvergensi lemah pada
  ruang Polish dalam [konvergensi dalam
  distribusi](../theory/dist/Convergence.html).
- `prerequisite.o009.distribution.skorohod-continuous-mapping`: representasi
  Skorohod dan pemetaan kontinu hampir di mana-mana pada [bagian ruang
  umum](../theory/dist/Convergence.html#sko).

**Ikatan hasil.**

- `outcome.o009.convergence.map-outside-null-discontinuities`: menerapkan
  teorema pemetaan ketika limit menghindari himpunan diskontinuitas.
- `outcome.o009.convergence.audit-discontinuous-transform`: menguji ketajaman
  hipotesis dengan limit degenerat yang terkonsentrasi pada himpunan
  diskontinuitas.
:::

::: {#unit.o009.mastery.convergence.02.exercise .exercise}
## Soal 2 — pemetaan diskontinu dan limit pada diagonal

Misalkan $S$ dan $T$ ruang metrik lengkap separabel, $g:S\to T$ terukur, dan
$D_g$ himpunan titik diskontinuitas $g$.

1. Dengan menggunakan teorema representasi Skorohod, buktikan bahwa

   $$
   Y_n\Rightarrow Y,
   \qquad \mathbb P(Y\in D_g)=0
   \quad\Longrightarrow\quad
   g(Y_n)\Rightarrow g(Y).
   $$

   Peubah-peubah $Y_n$ tidak perlu didefinisikan pada ruang peluang yang sama.
2. Ambil $Z,W$ saling bebas dengan distribusi $\mathcal N(0,1)$, definisikan

   $$
   Y_n=(Z+n^{-1},W),
   \qquad Y=(Z,W),
   \qquad
   g(x,y)=\mathbf 1_{\{x\le y\}}.
   $$

   Tentukan $D_g$, verifikasi hipotesis bagian pertama, dan tentukan limit
   distribusi $g(Y_n)$.
3. Tunjukkan bahwa syarat $\mathbb P(Y\in D_g)=0$ tidak boleh dihapus begitu
   saja. Untuk

   $$
   \widetilde Y_n=(Z,Z+n^{-1}W),
   \qquad \widetilde Y=(Z,Z),
   $$

   buktikan $\widetilde Y_n\to\widetilde Y$ dalam probabilitas, tetapi
   $g(\widetilde Y_n)$ tidak konvergen dalam distribusi ke
   $g(\widetilde Y)$.
:::

::: {#unit.o009.mastery.convergence.02.hint.01 .hint}
**Petunjuk 1.** Realisasikan hukum $Y_n$ dan $Y$ sebagai
$Y_n'$ dan $Y'$ pada satu ruang peluang dengan $Y_n'\to Y'$ hampir pasti.
Pada kejadian tempat $Y'\notin D_g$, gunakan definisi kekontinuan $g$ di
titik limit tersebut.
:::

::: {#unit.o009.mastery.convergence.02.hint.02 .hint}
**Petunjuk 2.** Untuk $g(x,y)=\mathbf 1_{\{x\le y\}}$, himpunan
diskontinuitasnya adalah diagonal $\Delta=\{(x,y):x=y\}$. Pada contoh kedua,
periksa $W-Z$; pada contoh ketiga, sederhanakan langsung ketaksamaan
$Z\le Z+n^{-1}W$.
:::

::: {#unit.o009.mastery.convergence.02.answer .answer}
**Jawaban ringkas.** Representasi Skorohod dan kekontinuan $g$ di luar
$D_g$ memberi konvergensi hampir pasti pada pasangan terkopel, sehingga
memberi konvergensi distribusi bagi hukum semula. Di aplikasi pertama,
$D_g=\Delta$, $\mathbb P(Z=W)=0$, dan
$g(Y_n)\Rightarrow\operatorname{Bernoulli}(1/2)$. Untuk limit degenerat,
$\widetilde Y_n\to(Z,Z)$ dalam probabilitas, tetapi
$g(\widetilde Y_n)=\mathbf 1_{\{W\ge0\}}$ berdistribusi
$\operatorname{Bernoulli}(1/2)$ untuk setiap $n$, sedangkan
$g(\widetilde Y)=1$ hampir pasti.
:::

::: {#unit.o009.mastery.convergence.02.solution .solution}
**Penyelesaian lengkap.** Karena $S$ Polish dan $Y_n\Rightarrow Y$, teorema
representasi Skorohod memberikan satu ruang peluang serta peubah acak
$Y_n',Y'$ pada ruang itu sedemikian sehingga

$$
\mathcal L(Y_n')=\mathcal L(Y_n),
\qquad
\mathcal L(Y')=\mathcal L(Y),
\qquad
Y_n'\longrightarrow Y'\quad\text{hampir pasti}.
$$

Karena hukum $Y'$ sama dengan hukum $Y$,

$$
\mathbb P(Y'\in D_g)=\mathbb P(Y\in D_g)=0.
$$

Pada kejadian berprobabilitas satu tempat $Y_n'\to Y'$ dan
$Y'\notin D_g$, fungsi $g$ kontinu di $Y'$. Definisi kekontinuan lalu memberi
$g(Y_n')\to g(Y')$ pada kejadian tersebut. Jadi
$g(Y_n')\to g(Y')$ hampir pasti, dan karenanya juga dalam distribusi. Karena
pemetaan terukur mempertahankan kesamaan hukum,

$$
\mathcal L(g(Y_n'))=\mathcal L(g(Y_n)),
\qquad
\mathcal L(g(Y'))=\mathcal L(g(Y)).
$$

Maka $g(Y_n)\Rightarrow g(Y)$, meskipun peubah semula tidak berada pada satu
ruang peluang.

Sekarang ambil $g(x,y)=\mathbf 1_{\{x\le y\}}$. Jika $x<y$ atau $x>y$,
ketaksamaan tersebut tetap mempunyai nilai kebenaran yang sama pada suatu
lingkungan cukup kecil dari $(x,y)$; jadi $g$ kontinu di luar diagonal.
Sebaliknya, setiap lingkungan titik $(x,x)$ memuat titik dengan koordinat
pertama lebih kecil dan titik dengan koordinat pertama lebih besar daripada
koordinat kedua. Nilai $g$ di kedua sisi itu berbeda. Dengan demikian,

$$
D_g=\Delta=\{(x,y)\in\mathbb R^2:x=y\}.
$$

Untuk $Y_n=(Z+n^{-1},W)$ berlaku

$$
\|Y_n-Y\|=n^{-1}\longrightarrow0,
$$

bahkan di setiap titik ruang sampel. Jadi $Y_n\to Y$ hampir pasti dan,
khususnya, $Y_n\Rightarrow Y$. Karena $W-Z\sim\mathcal N(0,2)$ mempunyai
distribusi kontinu,

$$
\mathbb P(Y\in D_g)=\mathbb P(Z=W)
=\mathbb P(W-Z=0)=0.
$$

Bagian pertama berlaku. Selain itu,

$$
\mathbb P(g(Y)=1)
=\mathbb P(Z\le W)
=\mathbb P(W-Z\ge0)=\frac12,
$$

karena distribusi normal berataan nol simetris. Oleh sebab itu,

$$
g(Y_n)\Rightarrow g(Y)
\sim\operatorname{Bernoulli}\!\left(\frac12\right).
$$

Terakhir,

$$
\|\widetilde Y_n-\widetilde Y\|
=n^{-1}|W|.
$$

Untuk setiap $\varepsilon>0$,

$$
\mathbb P\bigl(\|\widetilde Y_n-\widetilde Y\|>\varepsilon\bigr)
=\mathbb P(|W|>n\varepsilon)\longrightarrow0,
$$

karena kejadian $\{|W|>n\varepsilon\}$ turun menuju himpunan kosong. Jadi
$\widetilde Y_n\to\widetilde Y$ dalam probabilitas. Akan tetapi,

$$
g(\widetilde Y_n)
=\mathbf 1_{\{Z\le Z+n^{-1}W\}}
=\mathbf 1_{\{W\ge0\}}
\sim\operatorname{Bernoulli}\!\left(\frac12\right)
$$

untuk setiap $n$, sedangkan

$$
g(\widetilde Y)=\mathbf 1_{\{Z\le Z\}}=1
\quad\text{hampir pasti}.
$$

Kedua distribusi tidak dapat konvergen satu sama lain. Misalnya, pada titik
$t=1/2$, yang merupakan titik kekontinuan fungsi distribusi peubah konstan
$1$,

$$
\mathbb P(g(\widetilde Y_n)\le t)=\frac12
\not\longrightarrow
0=\mathbb P(g(\widetilde Y)\le t).
$$

Di sini $\mathbb P(\widetilde Y\in D_g)=1$, sehingga kegagalan tersebut tepat
menunjukkan peran hipotesis himpunan diskontinuitas bernilai nol.
:::

::: {#unit.o009.mastery.convergence.02.rights .rights-provenance}
**Hak dan provenans.** Soal, kedua petunjuk, jawaban ringkas, dan penyelesaian
lengkap pada akar `unit.o009.mastery.convergence.02` merupakan materi asli
yang ditulis untuk unit ini dan dilepas dengan lisensi
[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
di bawah pengenal
`rights.o009.mastery.convergence.02.cc-by-4.0`. Konsep prasyarat ditautkan
untuk orientasi kurikuler; tidak ada teks soal atau penyelesaian yang
diadaptasi dari sumber donor. Pengungkapan produksi: **OpenAI Codex
gpt-5.6-sol, Ultra**, atas arahan pengguna.
:::

:::

:::
