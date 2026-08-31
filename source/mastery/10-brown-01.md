---
title: "Penguasaan 10.01: gerak Brown dengan luas lintasan yang ditambatkan"
lang: id-ID
license: "CC BY 4.0"
authoring:
  course_id: "o009"
  unit_id: "o009-unit-brownian-motion"
  mastery_id: "o009-mastery-brown-01"
  mastery_item: "01-of-07"
  matched_theory_id: "o009-theory-random-brown-standard"
  source_alias: "original-synthesis: area-conditioned-brownian-gaussian-regression"
  provenance: "Materi asli yang disusun oleh OpenAI Codex atas arahan pengguna; tidak menyalin atau mengadaptasi soal donor."
  model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."
---

::: {#o009-mastery-brown-01 .mastery .original-addition}

> **Hak dan provenans.** Soal, petunjuk, jawaban, dan penyelesaian ini adalah
> materi asli berbahasa Indonesia (id-ID), disusun oleh OpenAI Codex atas
> arahan pengguna, dan dilisensikan dengan
> [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Tidak ada soal
> donor yang disalin atau diadaptasi. Konteks gerak Brown mengikuti unit teori
> yang dipasangkan dan laboratorium Brown pada kursus ini, tetapi masalah
> observasi luas lintasan serta seluruh derivasi di bawah ditulis baru.

## Prasyarat

- definisi gerak Brown standar dan rumus
  $\operatorname{Cov}(B_s,B_t)=\min(s,t)$;
- vektor Gaussian, fungsi kovarians, dan fakta bahwa komponen suatu vektor
  Gaussian yang tidak berkorelasi saling independen;
- integral Riemann lintasan kontinu, konvergensi dalam $L^2$, serta teorema
  Fubini untuk ekspektasi;
- rumus regresi Gaussian dan pengertian distribusi bersyarat reguler.

## Hasil belajar

Setelah menyelesaikan soal ini, pembaca dapat membuktikan bahwa fungsional
linear lintasan Brown bersifat Gaussian, menghitung hukum bersyarat seluruh
proses dari satu observasi linear, membangun proses residu yang independen,
dan menafsirkan pengondisian pada kejadian bernilai peluang nol secara tepat.

::: {#o009-exercise-brown-01 .exercise}

Misalkan $B=(B_t)_{0\leq t\leq1}$ adalah gerak Brown standar dan definisikan
luas bertanda di bawah lintasannya dengan integral Riemann lintasan demi
lintasan

$$
A=\int_0^1 B_u\,du.
$$

Untuk $t\in[0,1]$, tuliskan $g(t)=t-t^2/2$, dan untuk $a\in\mathbb R$
tafsirkan ``hukum $B$ bersyarat pada $A=a$'' sebagai suatu versi distribusi
bersyarat reguler.

1. Buktikan bahwa untuk setiap $0\leq t_1<\cdots<t_m\leq1$, vektor
   $(B_{t_1},\ldots,B_{t_m},A)$ adalah Gaussian berpusat. Hitung
   $\operatorname{Cov}(B_t,A)$ dan $\operatorname{Var}(A)$ secara eksak.
2. Definisikan
   $$
   R_t=B_t-3g(t)A.
   $$
   Buktikan bahwa proses kontinu $R$ independen dari $A$. Gunakan hasil ini
   untuk menentukan fungsi rataan dan fungsi kovarians hukum bersyarat
   seluruh lintasan $(B_t)_{0\leq t\leq1}$ dengan syarat $A=a$.
3. Berikan realisasi eksplisit proses yang mempunyai hukum bersyarat tersebut,
   buktikan bahwa luas lintasannya sama dengan $a$ hampir pasti, lalu hitung
   $$
   \mathbb P(B_{1/2}>0\mid A=a)
   $$
   pada versi bersyarat reguler yang Anda peroleh. Nyatakan jawaban dengan
   fungsi distribusi normal baku $\Phi$.

:::

::: {#o009-hint-brown-01-1 .hint}

**Petunjuk 1.** Aproksimasi $A$ dengan jumlah Riemann
$A_n=n^{-1}\sum_{k=1}^n B_{(k-1)/n}$. Gunakan
$\lVert B_u-B_v\rVert_2=|u-v|^{1/2}$ untuk memperoleh $A_n\to A$ dalam
$L^2$. Untuk kovarians, integralkan $\min(t,u)$ pada $u\in[0,1]$.

:::

::: {#o009-hint-brown-01-2 .hint}

**Petunjuk 2.** Koefisien regresi Gaussian untuk memprediksi $B_t$ dari $A$
adalah

$$
\frac{\operatorname{Cov}(B_t,A)}{\operatorname{Var}(A)}=3g(t).
$$

Periksa $\operatorname{Cov}(R_t,A)=0$. Untuk mengangkat independensi
berdimensi hingga menjadi independensi proses, gunakan kontinuitas lintasan:
sigma-aljabar Borel pada $C[0,1]$ dibangkitkan oleh evaluasi pada waktu
rasional.

:::

::: {#o009-hint-brown-01-3 .hint}

**Petunjuk 3.** Ambil $X_t^{(a)}=R_t+3g(t)a$. Identitas
$\int_0^1g(t)\,dt=1/3$ menunjukkan bahwa
$\int_0^1X_t^{(a)}\,dt=a$. Pada $t=1/2$, hitung
$g(1/2)=3/8$ sebelum menstandarkan normal bersyarat.

:::

::: {#o009-answer-brown-01 .answer}

**Jawaban ringkas.** Vektor $(B_{t_1},\ldots,B_{t_m},A)$ adalah Gaussian
berpusat, dan

$$
\operatorname{Cov}(B_t,A)=g(t)=t-\frac{t^2}{2},
\qquad
\operatorname{Var}(A)=\frac13.
$$

Proses $R_t=B_t-3g(t)A$ independen dari $A$. Suatu versi hukum bersyarat
$B\mid A=a$ ialah hukum proses
$X_t^{(a)}=R_t+3g(t)a$, yang mempunyai

$$
\mathbb E[X_t^{(a)}]=3g(t)a,
\qquad
\operatorname{Cov}(X_s^{(a)},X_t^{(a)})
=\min(s,t)-3g(s)g(t).
$$

Selain itu, $\int_0^1X_t^{(a)}\,dt=a$ hampir pasti dan

$$
\mathbb P(B_{1/2}>0\mid A=a)=\Phi\!\left(\frac{9a}{\sqrt5}\right).
$$

:::

::: {#o009-solution-brown-01 .solution}

**Penyelesaian lengkap.** Karena lintasan Brown kontinu hampir pasti, integral
$A$ ada sebagai integral Riemann. Untuk menunjukkan sifat Gaussian yang juga
diperlukan dalam perhitungan bersyarat, ambil

$$
A_n=\frac1n\sum_{k=1}^n B_{(k-1)/n}.
$$

Jika $\pi_n(u)=(k-1)/n$ untuk $u\in[(k-1)/n,k/n)$, ketaksamaan Minkowski
dan sifat inkremen Brown memberi

$$
\begin{aligned}
\lVert A-A_n\rVert_2
&\leq \int_0^1\lVert B_u-B_{\pi_n(u)}\rVert_2\,du\\
&=\int_0^1|u-\pi_n(u)|^{1/2}\,du
\leq n^{-1/2}\longrightarrow0.
\end{aligned}
$$

Untuk setiap $n$, vektor
$(B_{t_1},\ldots,B_{t_m},A_n)$ adalah transformasi linear dari suatu vektor
Gaussian berdimensi hingga. Setiap kombinasi linearnya adalah normal
berpusat. Kombinasi tersebut konvergen dalam $L^2$ ketika $A_n$ diganti oleh
$A$, sehingga ragamnya juga konvergen; limitnya tetap normal, mungkin
degenerat. Kriteria kombinasi linear untuk vektor Gaussian menyimpulkan bahwa
$(B_{t_1},\ldots,B_{t_m},A)$ Gaussian berpusat.

Fubini dan $\mathbb E[B_tB_u]=\min(t,u)$ menghasilkan

$$
\begin{aligned}
\operatorname{Cov}(B_t,A)
&=\int_0^1\min(t,u)\,du\\
&=\int_0^t u\,du+\int_t^1t\,du
=t-\frac{t^2}{2}=g(t).
\end{aligned}
$$

Dengan mengintegralkan sekali lagi,

$$
\operatorname{Var}(A)
=\int_0^1\operatorname{Cov}(B_t,A)\,dt
=\int_0^1\left(t-\frac{t^2}{2}\right)dt
=\frac13.
$$

Sekarang definisikan $R_t=B_t-3g(t)A$. Proses ini kontinu dan Gaussian, serta

$$
\operatorname{Cov}(R_t,A)
=g(t)-3g(t)\operatorname{Var}(A)=0.
$$

Untuk setiap kumpulan waktu hingga, vektor nilai-nilai $R$ bersama $A$
bersifat Gaussian. Kovarians silang nol karena itu membuat vektor nilai-nilai
$R$ independen dari $A$. Evaluasi pada waktu rasional membangkitkan
sigma-aljabar Borel $C[0,1]$; kontinuitas $R$ lalu menunjukkan bahwa proses
$R$, sebagai peubah acak bernilai $C[0,1]$, independen dari $A$.

Identitas $B_t=R_t+3g(t)A$ sekarang memberi versi hukum bersyarat yang konkret.
Untuk setiap $a\in\mathbb R$, tetapkan

$$
X_t^{(a)}=R_t+3g(t)a.
$$

Karena $R$ independen dari $A$, kernel
$a\mapsto\mathcal L(X^{(a)})$ memenuhi identitas disintegrasi dan merupakan
distribusi bersyarat reguler $\mathcal L(B\mid A=a)$. Bahkan kernel ini
terdefinisi untuk setiap $a$, sehingga rumusnya memberi versi kontinu yang
jelas meskipun kejadian tunggal $\{A=a\}$ berpeluang nol.

Rataannya adalah $3g(t)a$. Fungsi kovariansnya sama dengan kovarians $R$;
untuk $s,t\in[0,1]$,

$$
\begin{aligned}
\operatorname{Cov}(R_s,R_t)
&=\min(s,t)-3g(t)g(s)-3g(s)g(t)
  +9g(s)g(t)\operatorname{Var}(A)\\
&=\min(s,t)-3g(s)g(t).
\end{aligned}
$$

Selanjutnya, $\int_0^1g(t)\,dt=1/3$, sehingga

$$
\int_0^1R_t\,dt
=A-3A\int_0^1g(t)\,dt=0
$$

hampir pasti. Akibatnya,

$$
\int_0^1X_t^{(a)}\,dt
=0+3a\int_0^1g(t)\,dt=a
$$

hampir pasti, sebagaimana seharusnya untuk lintasan yang luasnya ditambatkan.

Terakhir, $g(1/2)=3/8$. Di bawah hukum bersyarat,

$$
B_{1/2}\mid A=a
\sim N\!\left(
3\frac38a,
\frac12-3\left(\frac38\right)^2
\right)
=N\!\left(\frac{9a}{8},\frac{5}{64}\right).
$$

Karena simpangan bakunya $\sqrt5/8$ dan simetri normal memberi
$1-\Phi(-x)=\Phi(x)$,

$$
\mathbb P(B_{1/2}>0\mid A=a)
=\Phi\!\left(
\frac{9a/8}{\sqrt5/8}
\right)
=\Phi\!\left(\frac{9a}{\sqrt5}\right).
$$

:::

:::
