---
title: "Penguasaan 03.05: limit gabungan pada waktu Poisson"
lang: id-ID
license: "CC BY 4.0"
authoring:
  course_id: "o009"
  unit_id: "o009-unit-convergence-modes"
  mastery_id: "o009-mastery-convergence-05"
  matched_theory_id: "o009-theory-random-prob-convergence"
  source_alias: "original-synthesis: poissonized-random-sum-joint-limit"
  provenance: "Materi asli yang disusun oleh OpenAI Codex atas arahan pengguna; tidak mengadaptasi soal donor."
  prerequisite_ids:
    - "prerequisite.o009.convergence.characteristic-functions"
    - "prerequisite.o009.convergence.poisson-generating-functions"
    - "prerequisite.o009.convergence.slutsky-continuous-mapping"
  outcome_ids:
    - "outcome.o009.convergence.random-sum-joint-limit"
    - "outcome.o009.convergence.asymptotic-independence"
    - "outcome.o009.convergence.random-versus-deterministic-centering"
  model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."
---

::: {#o009-mastery-convergence-05 .mastery .original-addition}

> **Hak dan provenans.** Soal, petunjuk, jawaban, dan penyelesaian ini adalah
> materi asli berbahasa Indonesia (id-ID), disusun oleh OpenAI Codex atas
> arahan pengguna, dan dilisensikan dengan
> [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Tidak ada soal
> donor yang disalin atau diadaptasi.

## Prasyarat

- fungsi karakteristik dan teorema kontinuitas Lévy;
- fungsi pembangkit peluang distribusi Poisson;
- hukum probabilitas total, independensi, dan ekspektasi bersyarat;
- konvergensi dalam peluang, teorema pemetaan kontinu, dan teorema Slutsky;
- ekspansi fungsi karakteristik sampai orde dua untuk peubah acak bermomen
  kedua hingga.

## Hasil belajar

Setelah menyelesaikan soal ini, pembaca dapat menurunkan limit normal gabungan
untuk jumlah dengan banyak suku acak, membuktikan independensi asimtotik (bukan
sekadar kovarians nol), serta membedakan ragam limit akibat pemusatan acak dan
pemusatan deterministik.

::: {#o009-exercise-convergence-05 .exercise}

Misalkan $X_1,X_2,\ldots$ iid dengan
$\mathbb E X_1=\mu$ dan $\operatorname{Var}(X_1)=\sigma^2\in(0,\infty)$.
Untuk setiap $n\geq 1$, misalkan $N_n\sim\operatorname{Poisson}(n)$ dan
$N_n$ independen dari seluruh barisan $(X_k)_{k\geq1}$. Definisikan
$S_m=\sum_{k=1}^m X_k$, dengan $S_0=0$, serta

$$
A_n=\frac{S_{N_n}-\mu N_n}{\sqrt n},
\qquad
B_n=\frac{N_n-n}{\sqrt n}.
$$

1. Buktikan bahwa $\operatorname{Cov}(A_n,B_n)=0$ untuk setiap $n$, lalu
   jelaskan mengapa fakta ini saja belum membuktikan independensi asimtotik.
2. Buktikan limit gabungan
   $$
   (A_n,B_n)\ \Rightarrow\ (\sigma Z_1,Z_2),
   $$
   dengan $Z_1,Z_2$ normal baku yang independen.
3. Deduksikan kedua limit berikut:
   $$
   \frac{S_{N_n}-\mu n}{\sqrt n}
   \Rightarrow N(0,\sigma^2+\mu^2),
   \qquad
   \frac{S_{N_n}-\mu N_n}{\sqrt{N_n}}
   \Rightarrow N(0,\sigma^2),
   $$
   dengan pecahan kedua didefinisikan bernilai $0$ pada kejadian $N_n=0$.
   Terangkan secara singkat asal suku tambahan $\mu^2$ pada limit pertama.

:::

::: {#o009-hint-convergence-05-1 .hint}

**Petunjuk 1.** Tetapkan $Y_k=X_k-\mu$. Dengan mengondisikan pada $N_n$,
periksa bahwa
$\mathbb E[S_{N_n}-\mu N_n\mid N_n]=0$. Ini menyelesaikan perhitungan
kovarians, tetapi belum menentukan hukum gabungan.

:::

::: {#o009-hint-convergence-05-2 .hint}

**Petunjuk 2.** Jika $\varphi(u)=\mathbb E e^{iuY_1}$, maka untuk $t,s\in
\mathbb R$ fungsi karakteristik gabungan dapat ditulis tepat sebagai

$$
\mathbb E e^{i(tA_n+sB_n)}
=\exp\!\left\{n\left(e^{is/\sqrt n}\varphi(t/\sqrt n)
-1-\frac{is}{\sqrt n}\right)\right\}.
$$

Gunakan $\varphi(u)=1-\sigma^2u^2/2+o(u^2)$.

:::

::: {#o009-hint-convergence-05-3 .hint}

**Petunjuk 3.** Untuk deduksi pertama, gunakan identitas
$S_{N_n}-\mu n=(S_{N_n}-\mu N_n)+\mu(N_n-n)$. Untuk deduksi kedua,
buktikan dahulu $N_n/n\to 1$ dalam peluang dan terapkan Slutsky; kejadian
$N_n=0$ mempunyai peluang $e^{-n}$.

:::

::: {#o009-answer-convergence-05 .answer}

**Jawaban ringkas.** Untuk setiap $n$,
$\operatorname{Cov}(A_n,B_n)=0$. Fungsi karakteristik gabungan
$(A_n,B_n)$ menuju

$$
\exp\!\left(-\frac{\sigma^2t^2+s^2}{2}\right),
$$

yakni fungsi karakteristik $(\sigma Z_1,Z_2)$ dengan komponen independen.
Karena $(S_{N_n}-\mu n)/\sqrt n=A_n+\mu B_n$, limitnya adalah
$N(0,\sigma^2+\mu^2)$. Selain itu $N_n/n\to1$ dalam peluang, sehingga
$(S_{N_n}-\mu N_n)/\sqrt{N_n}\Rightarrow N(0,\sigma^2)$.

:::

::: {#o009-solution-convergence-05 .solution}

**Penyelesaian lengkap.** Tuliskan $Y_k=X_k-\mu$. Maka
$\mathbb E Y_k=0$, $\mathbb E Y_k^2=\sigma^2$, dan
$S_{N_n}-\mu N_n=\sum_{k=1}^{N_n}Y_k$. Dengan mengondisikan pada $N_n$,

$$
\mathbb E\!\left[S_{N_n}-\mu N_n\mid N_n\right]=0.
$$

Karena $\mathbb E B_n=0$, diperoleh

$$
\operatorname{Cov}(A_n,B_n)
=\mathbb E[A_nB_n]
=\frac1n\mathbb E\!\left[(N_n-n)
  \mathbb E[S_{N_n}-\mu N_n\mid N_n]\right]=0.
$$

Kovarians nol hanya mengukur hubungan linear; untuk peubah yang tidak
diketahui normal gabungan, ia tidak menyiratkan independensi. Karena itu,
independensi pada limit harus dibuktikan dari hukum gabungannya.

Ambil $t,s\in\mathbb R$ tetap dan definisikan
$\varphi(u)=\mathbb E e^{iuY_1}$. Bersyarat pada $N_n=m$, independensi
memberikan

$$
\mathbb E\!\left[e^{itA_n}\mid N_n=m\right]
=\varphi(t/\sqrt n)^m.
$$

Rumus $\mathbb E[z^{N_n}]=\exp\{n(z-1)\}$, yang juga berlaku untuk
$z\in\mathbb C$, kemudian menghasilkan

$$
\begin{aligned}
\Phi_n(t,s)
&=\mathbb E e^{i(tA_n+sB_n)}\\
&=e^{-is\sqrt n}
  \mathbb E\!\left[
    \{e^{is/\sqrt n}\varphi(t/\sqrt n)\}^{N_n}
  \right]\\
&=\exp\!\left\{n\left(e^{is/\sqrt n}\varphi(t/\sqrt n)
  -1-\frac{is}{\sqrt n}\right)\right\}.
\end{aligned}
$$

Momen kedua yang hingga dan $\mathbb E Y_1=0$ menjamin ekspansi

$$
\varphi(u)=1-\frac{\sigma^2u^2}{2}+o(u^2).
$$

Sebagai justifikasi, bagi
$e^{iuY_1}-1-iuY_1$ dengan $u^2$ dan gunakan konvergensi terdominasi;
ketaksamaan $|e^{ix}-1-ix|\le x^2/2$ menyediakan dominator
$Y_1^2/2$. Di sisi lain,

$$
e^{is/\sqrt n}
=1+\frac{is}{\sqrt n}-\frac{s^2}{2n}+o(n^{-1}).
$$

Mengalikan kedua ekspansi memberi

$$
e^{is/\sqrt n}\varphi(t/\sqrt n)
=1+\frac{is}{\sqrt n}
-\frac{s^2+\sigma^2t^2}{2n}+o(n^{-1}).
$$

Karena itu

$$
\Phi_n(t,s)\longrightarrow
\exp\!\left(-\frac{s^2+\sigma^2t^2}{2}\right)
=e^{-\sigma^2t^2/2}e^{-s^2/2}.
$$

Fungsi terakhir kontinu di asal dan merupakan hasil kali fungsi
karakteristik $N(0,\sigma^2)$ dan $N(0,1)$. Teorema kontinuitas Lévy
menyimpulkan
$(A_n,B_n)\Rightarrow(\sigma Z_1,Z_2)$, dan faktorisasi tersebut membuktikan
bahwa $Z_1$ dan $Z_2$ independen.

Selanjutnya, identitas

$$
\frac{S_{N_n}-\mu n}{\sqrt n}=A_n+\mu B_n
$$

serta teorema pemetaan kontinu memberikan limit
$\sigma Z_1+\mu Z_2$. Independensi kedua normal itu menghasilkan ragam
$\sigma^2+\mu^2$. Suku $\mu^2$ berasal dari fluktuasi Poisson pada banyaknya
suku: mengganti pusat acak $\mu N_n$ dengan pusat tetap $\mu n$ menyisakan
$\mu(N_n-n)$ pada skala $\sqrt n$.

Terakhir, $\mathbb E N_n=n$ dan $\operatorname{Var}(N_n)=n$, sehingga untuk
setiap $\varepsilon>0$, ketaksamaan Chebyshev memberi

$$
\mathbb P\!\left(\left|\frac{N_n}{n}-1\right|>\varepsilon\right)
\le \frac{1}{n\varepsilon^2}\longrightarrow0.
$$

Jadi $N_n/n\to1$ dalam peluang. Pada $\{N_n>0\}$,

$$
\frac{S_{N_n}-\mu N_n}{\sqrt{N_n}}
=\frac{A_n}{\sqrt{N_n/n}}.
$$

Karena $\mathbb P(N_n=0)=e^{-n}\to0$, definisi bernilai nol pada kejadian
itu tidak memengaruhi limit. Teorema Slutsky akhirnya memberikan
$A_n/\sqrt{N_n/n}\Rightarrow\sigma Z_1$, yaitu $N(0,\sigma^2)$.

:::

:::
