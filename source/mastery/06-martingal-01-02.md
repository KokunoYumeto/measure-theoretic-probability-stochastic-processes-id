---
title: "Penguasaan martingal dan waktu henti 01–02"
lang: id-ID
author:
  - "Codex (penulisan materi asli atas arahan pengguna)"
authoring:
  course_id: "o009"
  unit_id: "unit.o009.original.mastery.martingales.01-02"
  target_locale: "id-ID"
  source_type: "original"
  rights_id: "rights.o009.original.mastery.martingales.01-02.cc-by-4.0"
  license: "CC-BY-4.0"
  model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."
bindings:
  prerequisites:
    - id: "prerequisite.o009.conditional-expectation"
      target: "../theory/expect/Conditional2.html"
    - id: "prerequisite.o009.martingales.definition"
      target: "../theory/martingales/Introduction.html"
    - id: "prerequisite.o009.martingales.optional-stopping"
      target: "../theory/martingales/Stop.html"
    - id: "prerequisite.o009.ctmc.generator"
      target: "../quantecon/lectures/generators.html"
  outcomes:
    - id: "outcome.o009.mastery.martingales.01.harmonic-stopping"
      description: "Membangun martingal harmonik untuk rantai kelahiran-kematian dan menghitung peluang absorpsi."
    - id: "outcome.o009.mastery.martingales.01.compensator"
      description: "Membangun martingal terkompensasi dan melewatkan penghentian terpotong ke limit secara sah."
    - id: "outcome.o009.mastery.martingales.02.counting-compensator"
      description: "Menurunkan kompensator proses hitung kelahiran murni dari generatornya dan menghentikannya secara sah."
    - id: "outcome.o009.mastery.martingales.02.laplace-stopping"
      description: "Membangun martingal ruang-waktu untuk menghitung transformasi Laplace waktu pencapaian."
---

::: {#unit.o009.original.mastery.martingales.01-02 .mastery-unit}

# Penguasaan martingal dan waktu henti 01–02

Dua masalah ini menguji dua pemakaian penghentian yang berbeda. Masalah pertama
mencari sendiri fungsi harmonik dan kompensator bagi rantai kelahiran-kematian
dengan peluang transisi bergantung keadaan. Masalah kedua bergerak ke waktu
kontinu: generator proses hitung kelahiran murni dipakai untuk membangun
kompensator dan martingal ruang-waktu.

::: {#unit.o009.original.mastery.martingales.01-02.bindings .mastery-bindings}

## Ikatan prasyarat dan capaian

| Masalah | Ikatan prasyarat | Ikatan capaian |
|---|---|---|
| 01 | `prerequisite.o009.conditional-expectation`, `prerequisite.o009.martingales.definition`, `prerequisite.o009.martingales.optional-stopping` | `outcome.o009.mastery.martingales.01.harmonic-stopping`, `outcome.o009.mastery.martingales.01.compensator` |
| 02 | `prerequisite.o009.conditional-expectation`, `prerequisite.o009.martingales.definition`, `prerequisite.o009.martingales.optional-stopping`, `prerequisite.o009.ctmc.generator` | `outcome.o009.mastery.martingales.02.counting-compensator`, `outcome.o009.mastery.martingales.02.laplace-stopping` |

Prasyarat yang dimaksud ialah kemampuan menghitung nilai harapan bersyarat,
memeriksa sifat martingal terhadap filtrasi alami, serta memakai penghentian
opsional pada waktu henti terbatas. Setelah menyelesaikan kedua masalah,
pembaca diharapkan mampu memilih fungsi uji yang harmonik, membangun
kompensator dari hanyutan lokal atau generator, dan melewatkan penghentian
terpotong ke waktu acak tanpa menghilangkan syarat keterintegralan.

:::

::: {#unit.o009.original.mastery.martingales.01 .mastery-sequence data-prerequisites="prerequisite.o009.conditional-expectation prerequisite.o009.martingales.definition prerequisite.o009.martingales.optional-stopping" data-outcomes="outcome.o009.mastery.martingales.01.harmonic-stopping outcome.o009.mastery.martingales.01.compensator"}

::: {#unit.o009.original.mastery.martingales.01.exercise .exercise}

## Masalah 01 — skala harmonik dan biaya sebelum absorpsi

Tetapkan bilangan bulat $N\ge2$. Rantai Markov $(X_n)_{n\ge0}$ mempunyai
ruang keadaan $\{0,1,\ldots,N\}$, keadaan $0$ dan $N$ menyerap, dan untuk
$1\le i\le N-1$ mempunyai peluang transisi

$$
\mathbb P(X_{n+1}=i+1\mid X_n=i)=\frac{i+1}{2i+1},
\qquad
\mathbb P(X_{n+1}=i-1\mid X_n=i)=\frac{i}{2i+1}.
$$

Ambil $X_0=r\in\{1,\ldots,N-1\}$, filtrasi alami
$\mathcal F_n=\sigma(X_0,\ldots,X_n)$, dan

$$
\tau=\inf\{n\ge0:X_n\in\{0,N\}\}.
$$

Tuliskan $H_0=0$ dan $H_i=\sum_{j=1}^i j^{-1}$ untuk $i\ge1$.

1. Buktikan bahwa $\tau$ merupakan waktu henti, $\tau<\infty$ hampir pasti,
   dan bahkan $\mathbb E_r\tau<\infty$.
2. Buktikan bahwa $(H_{X_{n\wedge\tau}})_{n\ge0}$ merupakan martingal.
   Gunakan fakta ini untuk menentukan
   $\mathbb P_r(X_\tau=N)$ secara eksak.
3. Bangun sebuah martingal terkompensasi dari proses koordinat $X_n$ dan
   hitung secara eksak

   $$
   \mathbb E_r\!\left[
     \sum_{k=0}^{\tau-1}\frac{1}{2X_k+1}
   \right].
   $$

4. Dari jawaban bagian 3, turunkan sebuah batas atas eksplisit bagi
   $\mathbb E_r\tau$.

:::

::: {#unit.o009.original.mastery.martingales.01.hint.01 .hint}

**Petunjuk 1.** Jika rantai masih berada di $i$, peluang mengikuti $i$ langkah
turun berturut-turut sampai $0$ adalah

$$
\prod_{j=1}^{i}\frac{j}{2j+1}.
$$

Bandingkan hasil kali ini dengan hasil kali yang sama sampai $N-1$, lalu
kelompokkan waktu ke dalam blok-blok sepanjang $N-1$.

:::

::: {#unit.o009.original.mastery.martingales.01.hint.02 .hint}

**Petunjuk 2.** Gunakan

$$
H_{i+1}-H_i=\frac1{i+1},
\qquad
H_i-H_{i-1}=\frac1i.
$$

Kedua suku hanyutan $H$ saling meniadakan setelah dikalikan dengan peluang
transisi. Karena $H_{X_{n\wedge\tau}}$ terbatas, pelewatan $n\to\infty$
dapat dilakukan dengan konvergensi terdominasi.

:::

::: {#unit.o009.original.mastery.martingales.01.hint.03 .hint}

**Petunjuk 3.** Pada keadaan interior $i$,

$$
\mathbb E[X_{n+1}-X_n\mid X_n=i]=\frac1{2i+1}.
$$

Kurangi jumlah hanyutan yang terakumulasi dari $X_{n\wedge\tau}$. Terapkan
identitas ekspektasi terlebih dahulu pada $n\wedge\tau$; untuk menuju $\tau$,
gunakan konvergensi monoton pada jumlah biaya dan konvergensi terdominasi pada
keadaan yang dihentikan.

:::

::: {#unit.o009.original.mastery.martingales.01.answer .answer}

**Jawaban ringkas.** Dengan
$\delta=\prod_{j=1}^{N-1}j/(2j+1)>0$ berlaku
$\mathbb P_r(\tau>m(N-1))\le(1-\delta)^m$, sehingga $\tau$ terintegralkan.
Fungsi $i\mapsto H_i$ harmonik pada keadaan interior, dan karena itu

$$
\mathbb P_r(X_\tau=N)=\frac{H_r}{H_N}.
$$

Martingal terkompensasinya adalah

$$
Y_n=X_{n\wedge\tau}
-\sum_{k=0}^{n-1}
 \frac{\mathbf1_{\{k<\tau\}}}{2X_k+1}.
$$

Akibatnya,

$$
\mathbb E_r\!\left[
\sum_{k=0}^{\tau-1}\frac1{2X_k+1}
\right]
=N\frac{H_r}{H_N}-r,
$$

dan

$$
\mathbb E_r\tau
\le(2N-1)\left(N\frac{H_r}{H_N}-r\right).
$$

:::

::: {#unit.o009.original.mastery.martingales.01.solution .solution}

**Penyelesaian lengkap.** Karena $X_n$ terukur terhadap $\mathcal F_n$,

$$
\{\tau\le n\}
=\bigcup_{k=0}^{n}\{X_k\in\{0,N\}\}
\in\mathcal F_n.
$$

Jadi $\tau$ merupakan waktu henti. Untuk membuktikan keterhinggaan, tetapkan

$$
\delta=\prod_{j=1}^{N-1}\frac{j}{2j+1}>0.
$$

Jika $X_s=i\in\{1,\ldots,N-1\}$, kejadian bahwa $i$ transisi berikutnya
semuanya bergerak turun membawa rantai ke $0$. Peluang bersyarat kejadian itu
adalah

$$
\prod_{j=1}^{i}\frac{j}{2j+1}\ge\delta,
$$

karena hasil kali di ruas kanan hanya menambahkan faktor-faktor dalam $(0,1)$.
Maka, pada kejadian $\{\tau>s\}$, peluang bersyarat untuk terserap dalam
paling banyak $N-1$ langkah berikutnya sekurang-kurangnya $\delta$. Dengan
induksi terhadap blok,

$$
\mathbb P_r\bigl(\tau>m(N-1)\bigr)
\le(1-\delta)^m,
\qquad m\ge0.
$$

Ruas kanan menuju nol, sehingga $\tau<\infty$ hampir pasti. Rumus jumlah ekor
untuk peubah acak bilangan bulat juga memberi

$$
\mathbb E_r\tau
=\sum_{n=0}^{\infty}\mathbb P_r(\tau>n)
\le (N-1)\sum_{m=0}^{\infty}(1-\delta)^m
=\frac{N-1}{\delta}<\infty.
$$

Sekarang ambil $1\le i\le N-1$. Dari relasi inkremen bilangan harmonik,

$$
\begin{aligned}
\mathbb E[H_{X_{n+1}}-H_{X_n}\mid X_n=i]
&=\frac{i+1}{2i+1}\frac1{i+1}
  -\frac{i}{2i+1}\frac1i\\
&=0.
\end{aligned}
$$

Pada keadaan menyerap, inkremennya juga nol. Sifat Markov lalu menghasilkan

$$
\mathbb E[H_{X_{(n+1)\wedge\tau}}\mid\mathcal F_n]
=H_{X_{n\wedge\tau}},
$$

jadi proses tersebut merupakan martingal. Ia dibatasi oleh $H_N$. Oleh sebab
itu, untuk setiap $n$,

$$
\mathbb E_r[H_{X_{n\wedge\tau}}]=H_r,
$$

dan, karena $\tau<\infty$ hampir pasti,
$X_{n\wedge\tau}\to X_\tau$. Konvergensi terdominasi memberi

$$
H_r=\mathbb E_r[H_{X_\tau}]
=H_N\mathbb P_r(X_\tau=N)+H_0\mathbb P_r(X_\tau=0).
$$

Karena $H_0=0$,

$$
\mathbb P_r(X_\tau=N)=\frac{H_r}{H_N}.
$$

Untuk bagian kompensator, pada $\{n<\tau\}$ kita mempunyai
$X_n\in\{1,\ldots,N-1\}$ dan

$$
\begin{aligned}
\mathbb E[X_{n+1}-X_n\mid\mathcal F_n]
&=\frac{X_n+1}{2X_n+1}-\frac{X_n}{2X_n+1}\\
&=\frac1{2X_n+1}.
\end{aligned}
$$

Pada $\{n\ge\tau\}$, proses yang dihentikan tidak berubah. Jadi

$$
\mathbb E[
X_{(n+1)\wedge\tau}-X_{n\wedge\tau}
\mid\mathcal F_n]
=\frac{\mathbf1_{\{n<\tau\}}}{2X_n+1}.
$$

Definisikan

$$
A_n=\sum_{k=0}^{n-1}
\frac{\mathbf1_{\{k<\tau\}}}{2X_k+1},
\qquad
Y_n=X_{n\wedge\tau}-A_n.
$$

Perhitungan terakhir menunjukkan bahwa $(Y_n)$ merupakan martingal. Semua
sukunya terintegralkan untuk $n$ tetap, sehingga

$$
\mathbb E_r[A_n]
=\mathbb E_r[X_{n\wedge\tau}]-r.
$$

Ketika $n\to\infty$, $A_n$ naik menuju

$$
A_\tau=\sum_{k=0}^{\tau-1}\frac1{2X_k+1},
$$

sedangkan $X_{n\wedge\tau}\to X_\tau$ dan
$0\le X_{n\wedge\tau}\le N$. Teorema konvergensi monoton pada ruas kiri dan
teorema konvergensi terdominasi pada ruas kanan memberikan

$$
\begin{aligned}
\mathbb E_r[A_\tau]
&=\mathbb E_r[X_\tau]-r\\
&=N\mathbb P_r(X_\tau=N)-r\\
&=N\frac{H_r}{H_N}-r.
\end{aligned}
$$

Argumen ini sekaligus membuktikan bahwa biaya total tersebut terintegralkan;
kita tidak mengasumsikannya sebelum melewatkan limit. Terakhir, selama
$k<\tau$ berlaku $1\le X_k\le N-1$, sehingga

$$
\frac1{2X_k+1}\ge\frac1{2N-1}.
$$

Dengan menjumlahkan sampai $\tau-1$,

$$
A_\tau\ge\frac{\tau}{2N-1}.
$$

Pengambilan ekspektasi menghasilkan batas eksplisit

$$
\mathbb E_r\tau
\le(2N-1)\left(N\frac{H_r}{H_N}-r\right).
$$

:::

:::

::: {#unit.o009.original.mastery.martingales.02 .mastery-sequence data-prerequisites="prerequisite.o009.conditional-expectation prerequisite.o009.martingales.definition prerequisite.o009.martingales.optional-stopping prerequisite.o009.ctmc.generator" data-outcomes="outcome.o009.mastery.martingales.02.counting-compensator outcome.o009.mastery.martingales.02.laplace-stopping"}

::: {#unit.o009.original.mastery.martingales.02.exercise .exercise}

## Masalah 02 — kompensator dan waktu kelahiran ke-$K$

Tetapkan $K\in\mathbb N_+$, $a>0$, dan $b\ge0$. Untuk
$j=0,\ldots,K-1$, tuliskan

$$
\lambda_j=a+bj.
$$

Ambil peubah acak independen
$E_j\sim\operatorname{Eksponensial}(\lambda_j)$ dan definisikan

$$
T_0=0,
\qquad
T_n=\sum_{j=0}^{n-1}E_j
\quad (1\le n\le K),
$$

$$
Z_t=\max\{n\in\{0,\ldots,K\}:T_n\le t\}.
$$

Jadi $(Z_t)_{t\ge0}$ adalah proses kelahiran murni yang meloncat
$j\to j+1$ dengan laju $\lambda_j$, dan $K$ menyerap. Gunakan filtrasi alami
yang dilengkapi dan dibuat kontinu kanan, serta tuliskan

$$
\tau_K=\inf\{t\ge0:Z_t=K\}=T_K.
$$

1. Turunkan generator

   $$
   (\mathcal Lf)(j)=
   \lambda_j\bigl(f(j+1)-f(j)\bigr)
   \quad (j<K),
   \qquad
   (\mathcal Lf)(K)=0,
   $$

   dan buktikan bahwa, untuk setiap fungsi
   $f:\{0,\ldots,K\}\to\mathbb R$,

   $$
   D_t^f
   =f(Z_t)-f(Z_0)-\int_0^t(\mathcal Lf)(Z_s)\,ds
   $$

   merupakan martingal.
2. Pilih $f(j)=j$ untuk mengidentifikasi kompensator proses hitung $Z$.
   Dengan penghentian terpotong dan limit yang dibenarkan, hitung

   $$
   \mathbb E\!\left[
   \int_0^{\tau_K}\lambda_{Z_s}\,ds
   \right].
   $$

3. Bangun fungsi $g$ sehingga
   $(g(Z_{t\wedge\tau_K})-t\wedge\tau_K)_{t\ge0}$ merupakan martingal,
   lalu tentukan $\mathbb E\tau_K$ secara eksak.
4. Untuk $s\ge0$, bangun martingal ruang-waktu terbatas yang menghasilkan
   transformasi Laplace $\mathbb E(e^{-s\tau_K})$.
5. Turunkan $\operatorname{Var}(\tau_K)$ dari transformasi tersebut.

:::

::: {#unit.o009.original.mastery.martingales.02.hint.01 .hint}

**Petunjuk 1.** Jika proses berada di $j<K$, maka dalam selang sepanjang $h$,

$$
\mathbb P_j(Z_h=j+1)=\lambda_jh+o(h),
\qquad
\mathbb P_j(Z_h=j)=1-\lambda_jh+o(h).
$$

Pada ruang keadaan hingga, identitas semigrup
$P_uf-f=\int_0^uP_v\mathcal Lf\,dv$ dapat dipadukan dengan sifat Markov
untuk membuktikan klaim martingal.

:::

::: {#unit.o009.original.mastery.martingales.02.hint.02 .hint}

**Petunjuk 2.** Untuk $f(j)=j$, generatornya sama dengan $\lambda_j$ sebelum
absorpsi. Untuk waktu pencapaian, coba

$$
g(0)=0,
\qquad
g(j)=\sum_{\ell=0}^{j-1}\frac1{\lambda_\ell}.
$$

Periksa bahwa $\mathcal Lg=1$ pada $\{0,\ldots,K-1\}$.

:::

::: {#unit.o009.original.mastery.martingales.02.hint.03 .hint}

**Petunjuk 3.** Untuk $s\ge0$, tetapkan $q_s(K)=1$ dan cari $q_s(j)$ mundur
dari persamaan $\mathcal Lq_s=sq_s$. Kemudian hentikan

$$
e^{-st}q_s(Z_t)
$$

pada $\tau_K$. Untuk momen, diferensiasikan logaritma hasil kali berhingga
yang diperoleh.

:::

::: {#unit.o009.original.mastery.martingales.02.answer .answer}

**Jawaban ringkas.** Kompensatornya ialah

$$
A_t=\int_0^{t\wedge\tau_K}\lambda_{Z_s}\,ds,
\qquad
Z_{t\wedge\tau_K}-A_t
\quad\text{martingal},
$$

dengan versi prediktabel yang sama
$A_t=\int_0^{t\wedge\tau_K}\lambda_{Z_{s-}}\,ds$. Selain itu,

$$
\mathbb E[A_{\tau_K}]=K.
$$

Dengan
$g(j)=\sum_{\ell=0}^{j-1}\lambda_\ell^{-1}$,

$$
\mathbb E\tau_K
=\sum_{j=0}^{K-1}\frac1{a+bj}.
$$

Untuk $s\ge0$,

$$
\mathbb E(e^{-s\tau_K})
=\prod_{j=0}^{K-1}\frac{a+bj}{a+bj+s},
$$

dan

$$
\operatorname{Var}(\tau_K)
=\sum_{j=0}^{K-1}\frac1{(a+bj)^2}.
$$

:::

::: {#unit.o009.original.mastery.martingales.02.solution .solution}

**Penyelesaian lengkap.** Karena $\tau_K=\sum_{j=0}^{K-1}E_j$ merupakan
jumlah berhingga peubah eksponensial yang berhingga hampir pasti,

$$
\tau_K<\infty
\quad\text{hampir pasti}.
$$

Untuk $j<K$, hanya satu lompatan yang mempunyai peluang orde $h$ pada selang
$[0,h]$; peluang dua atau lebih lompatan adalah $o(h)$ karena semua laju
dibatasi oleh $\lambda_{K-1}$. Jadi, untuk setiap fungsi $f$,

$$
\begin{aligned}
\mathbb E_j[f(Z_h)]-f(j)
&=\lambda_jh\bigl(f(j+1)-f(j)\bigr)+o(h).
\end{aligned}
$$

Pembagian dengan $h$ dan pelewatan $h\downarrow0$ memberi

$$
(\mathcal Lf)(j)
=\lambda_j\bigl(f(j+1)-f(j)\bigr),
\qquad j<K.
$$

Di keadaan menyerap $K$, generatornya nol.

Untuk membuktikan klaim martingal tanpa hanya mengutip nama teorema,
tuliskan $(P_u)_{u\ge0}$ untuk semigrup transisi. Karena ruang keadaan hingga
dan generator terbatas,

$$
P_uf-f=\int_0^uP_v\mathcal Lf\,dv.
$$

Jika $0\le r\le t$, sifat Markov dan Fubini memberi

$$
\begin{aligned}
\mathbb E[D_t^f-D_r^f\mid\mathcal F_r]
&=P_{t-r}f(Z_r)-f(Z_r)
  -\int_0^{t-r}P_v\mathcal Lf(Z_r)\,dv\\
&=0.
\end{aligned}
$$

Semua suku terbatas pada setiap selang waktu berhingga, sehingga
$(D_t^f)$ benar-benar merupakan martingal, bukan sekadar martingal lokal.

Ambil sekarang $f(j)=j$. Untuk $j<K$,

$$
(\mathcal Lf)(j)=\lambda_j,
$$

sedangkan $(\mathcal Lf)(K)=0$. Karena proses tetap di $K$ setelah
$\tau_K$, proses menaik kontinu

$$
A_t=\int_0^{t\wedge\tau_K}\lambda_{Z_{s-}}\,ds
$$

bersifat prediktabel. Lintasan $Z$ hanya mempunyai berhingga banyak titik
lompatan, sehingga integral Lebesgue yang sama dapat ditulis dengan
$Z_s$ sebagai pengganti $Z_{s-}$. Dengan demikian,

$$
M_t
=Z_{t\wedge\tau_K}
-\int_0^{t\wedge\tau_K}\lambda_{Z_s}\,ds
$$

merupakan martingal yang berawal dari nol. Maka

$$
\mathbb E\!\left[
\int_0^{t\wedge\tau_K}\lambda_{Z_s}\,ds
\right]
=\mathbb E[Z_{t\wedge\tau_K}].
$$

Ketika $t\to\infty$, integral di ruas kiri naik menuju integral sampai
$\tau_K$, sedangkan $Z_{t\wedge\tau_K}\to K$ dan dibatasi oleh $K$.
Teorema konvergensi monoton di ruas kiri dan konvergensi terdominasi di ruas
kanan menghasilkan

$$
\mathbb E\!\left[
\int_0^{\tau_K}\lambda_{Z_s}\,ds
\right]
=K.
$$

Perhatikan bahwa limit ini sekaligus membuktikan keterintegralan kompensator
yang dihentikan; keterintegralan itu tidak diasumsikan sebelumnya.

Untuk waktu pencapaian, definisikan

$$
g(0)=0,
\qquad
g(j)=\sum_{\ell=0}^{j-1}\frac1{\lambda_\ell},
\quad 1\le j\le K.
$$

Bagi $j<K$,

$$
(\mathcal Lg)(j)
=\lambda_j\bigl(g(j+1)-g(j)\bigr)
=\lambda_j\frac1{\lambda_j}
=1.
$$

Karena $\mathcal Lg(K)=0$, martingal Dynkin untuk $g$ adalah

$$
g(Z_{t\wedge\tau_K})-t\wedge\tau_K.
$$

Pengambilan ekspektasi memberi

$$
\mathbb E[t\wedge\tau_K]
=\mathbb E[g(Z_{t\wedge\tau_K})].
$$

Ruas kiri naik menuju $\mathbb E\tau_K$. Ruas kanan menuju $g(K)$ dengan
konvergensi terdominasi karena $g$ terbatas pada ruang keadaan hingga.
Akibatnya,

$$
\mathbb E\tau_K
=g(K)
=\sum_{j=0}^{K-1}\frac1{\lambda_j}
=\sum_{j=0}^{K-1}\frac1{a+bj}.
$$

Sekarang tetapkan $s\ge0$ dan definisikan

$$
q_s(K)=1,
\qquad
q_s(j)=\prod_{\ell=j}^{K-1}
\frac{\lambda_\ell}{\lambda_\ell+s},
\quad 0\le j<K.
$$

Relasi mundurnya ialah

$$
q_s(j)=\frac{\lambda_j}{\lambda_j+s}q_s(j+1).
$$

Dengan demikian,

$$
\begin{aligned}
(\mathcal Lq_s)(j)
&=\lambda_j\bigl(q_s(j+1)-q_s(j)\bigr)\\
&=s\,q_s(j),
\qquad j<K.
\end{aligned}
$$

Rumus Dynkin ruang-waktu, dihentikan pada $\tau_K$, sekarang menunjukkan bahwa

$$
R_t
=e^{-s(t\wedge\tau_K)}
 q_s(Z_{t\wedge\tau_K})
$$

merupakan martingal. Memang, sebelum absorpsi, hanyutannya adalah

$$
e^{-st}\bigl(-s q_s+\mathcal Lq_s\bigr)=0,
$$

dan setelah absorpsi proses yang dihentikan konstan. Selain itu,
$0<R_t\le1$, sehingga tidak ada persoalan martingal lokal atau
keterintegralan seragam. Karena $R_0=q_s(0)$,

$$
\mathbb E[R_t]=q_s(0).
$$

Ketika $t\to\infty$, berlaku
$R_t\to e^{-s\tau_K}q_s(K)=e^{-s\tau_K}$ hampir pasti. Konvergensi
terdominasi memberi

$$
\mathbb E(e^{-s\tau_K})
=q_s(0)
=\prod_{j=0}^{K-1}\frac{\lambda_j}{\lambda_j+s}
=\prod_{j=0}^{K-1}\frac{a+bj}{a+bj+s}.
$$

Terakhir, tuliskan $\phi(s)=\mathbb E(e^{-s\tau_K})$. Karena $\tau_K$
merupakan jumlah berhingga peubah eksponensial, momen keduanya berhingga dan
diferensiasi pada $s=0$ sah. Dari hasil kali berhingga di atas,

$$
\log\phi(s)
=-\sum_{j=0}^{K-1}\log\left(1+\frac{s}{\lambda_j}\right).
$$

Pada $s=0$,

$$
(\log\phi)'(0)
=-\sum_{j=0}^{K-1}\frac1{\lambda_j},
\qquad
(\log\phi)''(0)
=\sum_{j=0}^{K-1}\frac1{\lambda_j^2}.
$$

Karena $\phi(0)=1$,
$\phi'(0)=-\mathbb E\tau_K$ dan
$\phi''(0)=\mathbb E(\tau_K^2)$. Identitas
$\phi''/\phi=(\log\phi)''+((\log\phi)')^2$ menghasilkan

$$
\mathbb E(\tau_K^2)
=\left(\sum_{j=0}^{K-1}\frac1{\lambda_j}\right)^2
 +\sum_{j=0}^{K-1}\frac1{\lambda_j^2}.
$$

Oleh karena itu,

$$
\operatorname{Var}(\tau_K)
=\sum_{j=0}^{K-1}\frac1{\lambda_j^2}
=\sum_{j=0}^{K-1}\frac1{(a+bj)^2}.
$$

Untuk $b=0$, rumus-rumus ini mereduksi menjadi
$\mathbb E\tau_K=K/a$ dan
$\operatorname{Var}(\tau_K)=K/a^2$, sesuai dengan waktu tunggu Erlang.

:::

:::

::: {#unit.o009.original.mastery.martingales.01-02.rights .rights-provenance}

## Hak dan provenans

Unit **Penguasaan martingal dan waktu henti 01–02**, termasuk kedua masalah,
petunjuk, jawaban, dan penyelesaian, merupakan materi asli berbahasa Indonesia
yang disusun untuk edisi ini. Sejauh hak baru timbul, materi tersebut
dilisensikan di bawah
[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
ID hak komponennya ialah
`rights.o009.original.mastery.martingales.01-02.cc-by-4.0`.

Penyusunan dibantu oleh **OpenAI Codex gpt-5.6-sol, Ultra.** Identitas model
tidak menggantikan kredit sumber atau kontributor manusia. Masalah, parameter,
urutan pertanyaan, petunjuk, serta penyelesaiannya dirumuskan baru untuk unit
ini. Tautan prasyarat hanya menunjuk teori yang diperlukan; unit ini tidak
menyalin prosa, latihan, laboratorium, atau jembatan yang ditautkan dan tidak
mengubah lisensi komponen lain.

:::

:::
