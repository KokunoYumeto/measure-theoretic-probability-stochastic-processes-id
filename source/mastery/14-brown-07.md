---
title: "Maksimum gerak Brown bersyarat pada titik akhir"
lang: id-ID
author:
  - "Codex (penulisan materi asli atas arahan pengguna)"
authoring:
  course_id: "o009"
  unit_id: "unit.o009.original.mastery.brown.07"
  target_locale: "id-ID"
  source_type: "original"
  rights_id: "rights.o009.original.mastery.brown.07.cc-by-4.0"
  license: "CC-BY-4.0"
  model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."
---

::: {#unit.o009.original.mastery.brown.07 .original-mastery .mastery-sequence}

# Maksimum gerak Brown bersyarat pada titik akhir

::: {#unit.o009.original.mastery.brown.07.prerequisites .prerequisites}

## Prasyarat

Pembaca diharapkan telah mengenal gerak Brown standar, kekontinuan
lintasannya, kerapatan normal standar, prinsip refleksi pada waktu pencapaian
pertama, serta cara memperoleh peluang bersyarat dari kerapatan bersama.
Untuk bagian terakhir diperlukan rumus integral ekor bagi peubah acak
nonnegatif dan fungsi galat komplementer

$$
\operatorname{erfc}(z)=\frac{2}{\sqrt{\pi}}
\int_z^\infty e^{-u^2}\,du.
$$

:::

::: {#unit.o009.original.mastery.brown.07.outcomes .learning-outcomes}

## Capaian pembelajaran

Setelah menyelesaikan latihan ini, pembaca mampu:

1. memakai refleksi lintasan untuk memperoleh kerapatan bersama maksimum dan
   titik akhir gerak Brown;
2. menafsirkan pengondisian pada kejadian nol seperti $B_1=x$ melalui
   probabilitas bersyarat reguler;
3. menurunkan fungsi distribusi, kerapatan, dan rataan maksimum bersyarat
   secara eksak; dan
4. mengenali kasus $B_1=0$ sebagai maksimum jembatan Brown standar.

:::

::: {#unit.o009.original.mastery.brown.07.exercise .exercise}

## Latihan 07 — maksimum yang diketahui titik akhirnya

Misalkan $B=(B_t)_{0\le t\le1}$ adalah gerak Brown standar dan

$$
M=\max_{0\le s\le1}B_s,
\qquad
\varphi(y)=\frac{1}{\sqrt{2\pi}}e^{-y^2/2}.
$$

Untuk $x\in\mathbb R$, notasi
$\mathbb P(\,\cdot\mid B_1=x)$ harus ditafsirkan sebagai sebuah versi
probabilitas bersyarat reguler, bukan sebagai rasio peluang dua kejadian.

1. Untuk $a>0$, gunakan refleksi lintasan setelah waktu pertama mencapai
   $a$ untuk membuktikan bahwa, pada daerah $x<a$, subkerapatan titik akhir
   lintasan yang telah mencapai $a$ adalah

   $$
   \mathbb P(M\ge a,\ B_1\in dx)=\varphi(2a-x)\,dx.
   $$

2. Tetapkan $\ell(x)=\max\{0,x\}$. Turunkan fungsi distribusi bersyarat
   $F_x(m)=\mathbb P(M\le m\mid B_1=x)$ untuk seluruh $m\in\mathbb R$, lalu
   tentukan kerapatan bersyarat $f_x$.
3. Hitung $\mathbb E[M\mid B_1=x]$ secara tertutup dalam $x$ dan
   $\operatorname{erfc}$.
4. Khususkan hasilnya pada $x=0$. Berikan fungsi distribusi, kerapatan,
   rataan, dan median maksimum jembatan Brown standar.

:::

::: {#unit.o009.original.mastery.brown.07.hint.01 .hint}

**Petunjuk 1.** Ambil
$\tau_a=\inf\{t\ge0:B_t=a\}$. Pada $\{\tau_a\le1\}$, gantilah bagian
lintasan setelah $\tau_a$ dengan $2a-B_t$. Jika lintasan semula berakhir di
$x<a$, di manakah lintasan hasil refleksi berakhir?

:::

::: {#unit.o009.original.mastery.brown.07.hint.02 .hint}

**Petunjuk 2.** Untuk $m>\ell(x)$, bagi subkerapatan pada Petunjuk 1 dengan
kerapatan marginal $\varphi(x)$ dan sederhanakan

$$
\frac{\varphi(2m-x)}{\varphi(x)}.
$$

Ingat pula bahwa $M\ge0$ dan, di bawah pengondisian, $M\ge x$.

:::

::: {#unit.o009.original.mastery.brown.07.hint.03 .hint}

**Petunjuk 3.** Gunakan

$$
\mathbb E[M\mid B_1=x]
=\ell(x)+\int_{\ell(x)}^\infty
\mathbb P(M>m\mid B_1=x)\,dm
$$

dan lengkapkan kuadrat:

$$
-2m(m-x)=\frac{x^2}{2}-2\left(m-\frac{x}{2}\right)^2.
$$

Perhatikan bahwa $\ell(x)-x/2=|x|/2$.

:::

::: {#unit.o009.original.mastery.brown.07.answer .answer}

## Jawaban ringkas

Untuk $a>0$ dan $x<a$, refleksi memberi subkerapatan
$\varphi(2a-x)$. Karena $B_1$ mempunyai kerapatan $\varphi$, sebuah versi
kontinu dari hukum bersyarat maksimum ialah

$$
F_x(m)=
\begin{cases}
0, & m<\ell(x),\\[3pt]
1-e^{-2m(m-x)}, & m\ge\ell(x),
\end{cases}
\qquad \ell(x)=\max\{0,x\}.
$$

Hukum ini tidak mempunyai atom, dan kerapatannya adalah

$$
f_x(m)=2(2m-x)e^{-2m(m-x)}
\mathbf 1_{(\ell(x),\infty)}(m).
$$

Rataannya ialah

$$
\mathbb E[M\mid B_1=x]
=\ell(x)+\frac{\sqrt\pi}{2\sqrt2}
e^{x^2/2}\operatorname{erfc}\!\left(\frac{|x|}{\sqrt2}\right).
$$

Untuk $x=0$, berlaku

$$
F_0(m)=1-e^{-2m^2},\qquad
f_0(m)=4m e^{-2m^2}\quad(m\ge0),
$$

sedangkan rataannya $\sqrt{\pi/8}$ dan mediannya
$\sqrt{(\log2)/2}$.

:::

::: {#unit.o009.original.mastery.brown.07.solution .solution}

## Penyelesaian lengkap

### 1. Refleksi dan subkerapatan bersama

Tetapkan $a>0$ dan definisikan waktu pencapaian pertama

$$
\tau_a=\inf\{t\ge0:B_t=a\}.
$$

Berkat kekontinuan lintasan, kejadian $\{M\ge a\}$ sama dengan
$\{\tau_a\le1\}$. Pada kejadian ini, definisikan lintasan terefleksi

$$
\widetilde B_t=
\begin{cases}
B_t, & 0\le t\le\tau_a,\\
2a-B_t, & \tau_a<t\le1.
\end{cases}
$$

Prinsip refleksi menyatakan bahwa transformasi ini mempertahankan ukuran
Wiener dan bersifat involutif: merefleksikan lintasan yang sama sekali lagi
menghasilkan lintasan semula. Jika $B_1=x<a$, maka
$\widetilde B_1=2a-x>a$.

Karena itu, untuk setiap himpunan Borel $A\subset(-\infty,a)$, refleksi
memberi bijeksi yang mempertahankan peluang dan menghasilkan

$$
\begin{aligned}
\mathbb P(M\ge a,\ B_1\in A)
&=\mathbb P(B_1\in 2a-A)\\
&=\int_{2a-A}\varphi(y)\,dy\\
&=\int_A\varphi(2a-x)\,dx,
\end{aligned}
$$

dengan $2a-A=\{2a-x:x\in A\}$. Jadi, pada $x<a$,

$$
\mathbb P(M\ge a,\ B_1\in dx)=\varphi(2a-x)\,dx.
$$

Secara ekuivalen, bagian lintasan yang tetap di bawah $a$ mempunyai
subkerapatan

$$
\mathbb P(M<a,\ B_1\in dx)
=\bigl[\varphi(x)-\varphi(2a-x)\bigr]\,dx,
\qquad x<a.
$$

### 2. Hukum dan kerapatan bersyarat

Karena $\varphi(x)>0$ untuk setiap $x\in\mathbb R$, disintegrasi kerapatan
pada hasil di atas memberi, mula-mula untuk hampir setiap $x<a$,

$$
\begin{aligned}
\mathbb P(M\ge a\mid B_1=x)
&=\frac{\varphi(2a-x)}{\varphi(x)}\\
&=\exp\!\left(
-\frac{(2a-x)^2-x^2}{2}
\right)\\
&=e^{-2a(a-x)}.
\end{aligned}
$$

Ruas terakhir kontinu dalam $(a,x)$ pada $x<a$. Karena hukum bersyarat hanya
ditentukan hampir di mana-mana terhadap hukum $B_1$, rumus kontinu ini
memilih satu versi untuk setiap $x$.

Selalu berlaku $M\ge B_0=0$, dan di bawah pengondisian $B_1=x$ juga berlaku
$M\ge x$. Jadi $M\ge\ell(x)=\max\{0,x\}$ hampir pasti menurut hukum
bersyarat. Untuk $m>\ell(x)$, rumus refleksi dapat dipakai dengan $a=m$ dan
memberi

$$
\mathbb P(M>m\mid B_1=x)=e^{-2m(m-x)}.
$$

Oleh sebab itu,

$$
F_x(m)=
\begin{cases}
0, & m<\ell(x),\\[3pt]
1-e^{-2m(m-x)}, & m\ge\ell(x).
\end{cases}
$$

Pada $m=\ell(x)$, rumus baris kedua juga bernilai nol: jika $x\ge0$, maka
$m=x$; jika $x<0$, maka $m=0$. Selain itu, $F_x(m)\to1$ ketika
$m\to\infty$. Jadi rumus tersebut memang fungsi distribusi dan tidak
mempunyai lompatan pada batas penyangganya.

Mendiferensiasikan pada $m>\ell(x)$ menghasilkan

$$
f_x(m)
=2(2m-x)e^{-2m(m-x)}.
$$

Pada daerah ini $2m-x>0$, sehingga kerapatan nonnegatif. Karena $F_x$ naik
dari nol ke satu, integral $f_x$ pada $(\ell(x),\infty)$ sama dengan satu.

### 3. Rataan bersyarat

Karena $M\ge\ell(x)$, rumus integral ekor memberi

$$
\mathbb E[M\mid B_1=x]
=\ell(x)+\int_{\ell(x)}^\infty e^{-2m(m-x)}\,dm.
$$

Lengkapi kuadrat pada eksponen:

$$
-2m(m-x)
=\frac{x^2}{2}-2\left(m-\frac{x}{2}\right)^2.
$$

Dengan substitusi $u=\sqrt2(m-x/2)$ dan identitas
$\ell(x)-x/2=|x|/2$, integral tersebut menjadi

$$
\begin{aligned}
\int_{\ell(x)}^\infty e^{-2m(m-x)}\,dm
&=\frac{e^{x^2/2}}{\sqrt2}
\int_{|x|/\sqrt2}^\infty e^{-u^2}\,du\\
&=\frac{\sqrt\pi}{2\sqrt2}e^{x^2/2}
\operatorname{erfc}\!\left(\frac{|x|}{\sqrt2}\right).
\end{aligned}
$$

Maka

$$
\boxed{
\mathbb E[M\mid B_1=x]
=\max\{0,x\}
+\frac{\sqrt\pi}{2\sqrt2}e^{x^2/2}
\operatorname{erfc}\!\left(\frac{|x|}{\sqrt2}\right)
}.
$$

### 4. Kasus jembatan Brown standar

Hukum proses $B$ dengan syarat $B_1=0$ adalah hukum jembatan Brown standar
pada $[0,1]$. Memasukkan $x=0$ ke rumus sebelumnya memberi, untuk $m\ge0$,

$$
\mathbb P(M\le m\mid B_1=0)=1-e^{-2m^2},
\qquad
f_0(m)=4m e^{-2m^2}.
$$

Rataan diperoleh baik dari rumus umum maupun langsung dari integral ekor:

$$
\mathbb E[M\mid B_1=0]
=\int_0^\infty e^{-2m^2}\,dm
=\frac{\sqrt\pi}{2\sqrt2}
=\sqrt{\frac{\pi}{8}}.
$$

Jika $q_{1/2}$ menyatakan median, maka

$$
1-e^{-2q_{1/2}^2}=\frac12,
$$

sehingga

$$
\boxed{q_{1/2}=\sqrt{\frac{\log2}{2}}}.
$$

Perhitungan ini juga menunjukkan mengapa pengondisian pada $B_1=0$ tidak
boleh diperlakukan sebagai pembagian dengan $\mathbb P(B_1=0)$, yang bernilai
nol. Yang dipakai adalah rasio kerapatan, lalu versi kontinu dari kernel
bersyarat.

:::

::: {#unit.o009.original.mastery.brown.07.rights-provenance .rights-provenance}

## Hak dan provenans

Latihan **Maksimum gerak Brown bersyarat pada titik akhir**, termasuk seluruh
petunjuk, jawaban, dan penyelesaiannya, merupakan materi asli berbahasa
Indonesia yang disusun untuk edisi ini. Materi baru tersebut dilisensikan di
bawah [Creative Commons Attribution 4.0 International
(CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/), sejauh hak baru
timbul. ID hak komponennya ialah
`rights.o009.original.mastery.brown.07.cc-by-4.0`.

Penyusunan materi ini dibantu oleh **OpenAI Codex gpt-5.6-sol, Ultra.** Materi
ini memakai teori umum gerak Brown, kerapatan Gaussian, dan prinsip refleksi
yang dibahas dalam unit [Gerak Brown Standar](../theory/brown/Standard.html)
sebagai prasyarat. Rumusan soal, urutan derivasi, penghitungan rataan
bersyarat melalui $\operatorname{erfc}$, dan penyajian pedagogis di sini
ditulis khusus untuk latihan ini; prosa sumber tidak direproduksi secara
substansial.

Lisensi CC BY 4.0 di atas hanya mencakup kontribusi baru pada berkas ini dan
tidak melisensikan ulang Random Services, MathJax, perangkat lunak, atau
komponen pihak ketiga lainnya. Materi ini independen dan tidak didukung atau
disahkan oleh penulis maupun lembaga sumber.

:::

:::
