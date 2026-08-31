---
title: "Penguasaan gerak Brown 02 — spektrum kovarians dan aproksimasi Karhunen–Loève"
lang: id-ID
author:
  - "Codex (materi asli, atas arahan pengguna)"
authoring:
  course_id: "o009"
  unit_id: "unit.o009.mastery.brown.02"
  mastery_id: "unit.o009.mastery.brown.02"
  sequence_index: 2
  sequence_total: 7
  target_locale: "id-ID"
  source_type: "original-mastery"
  source_alias: "Random:brown/Standard.html"
  source_authority: "authority/random/RANDOM_AUTHORITY_RECEIPT.json"
  source_authority_sha256: "ea3786a05f3a1ccf444818f17516ce85065c76759bfc8071d43fd8a98c643eb4"
  source_page_sha256: "brown/Standard.html=3693677d4d4c75e7888f806a027fa25020babeb80c720bbb77ad6fd0c639276b"
  source_relation: "latihan spektral baru yang hanya memakai definisi dan kovarians gerak Brown standar dari sumber; tidak menyalin prosa, kode, latihan, atau aset sumber"
  rights_id: "rights.o009.mastery.brown.02.cc-by-4.0"
  license: "CC-BY-4.0"
  model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."
---

::: {#unit.o009.mastery.brown.02 .mastery-sequence}

# Penguasaan gerak Brown 02 — spektrum kovarians dan aproksimasi Karhunen–Loève

::: {#unit.o009.mastery.brown.02.prerequisites .prerequisites}

## Prasyarat

Gunakan gerak Brown standar $B=(B_t)_{0\le t\le1}$, sehingga
$\mathbb E B_t=0$ dan

$$
\mathbb E(B_sB_t)=\min\{s,t\}.
$$

Pembaca diasumsikan menguasai ruang Hilbert $L^2[0,1]$, proyeksi ortogonal,
ketaksamaan Bessel, identitas Parseval, Fubini--Tonelli, serta fakta bahwa
vektor Gaussian yang komponen-komponennya tidak berkorelasi mempunyai
komponen independen. Boleh digunakan kelengkapan basis sinus biasa pada
$L^2(0,2)$ dan identitas Basel
$\sum_{k=1}^{\infty}k^{-2}=\pi^2/6$.

:::

::: {#unit.o009.mastery.brown.02.outcomes .outcomes}

## Capaian

Setelah menyelesaikan soal, pembaca dapat menurunkan spektrum operator
kovarians Brown dari masalah batas diferensial, membangun ekspansi
Karhunen--Loève dengan peubah normal yang independen, menyatakan tepat mode
konvergensinya, menghitung galat pemotongan eksak, dan membuktikan optimalitas
subruang aproksimasi tanpa sekadar mengutip nama sebuah teorema spektral.

:::

::: {#unit.o009.mastery.brown.02.exercise .exercise}

## Soal

Tuliskan $H=L^2[0,1]$ dengan hasil kali dalam
$\langle f,g\rangle=\int_0^1 f(t)g(t)\,dt$. Karena lintasan Brown kontinu
hampir pasti, $B$ dapat dipandang sebagai peubah acak bernilai $H$. Definisikan
operator kovarians $K:H\to H$ melalui

$$
(Kf)(t)=\int_0^1\min\{s,t\}f(s)\,ds.
$$

Kerjakan semua bagian berikut.

1. Untuk $g=Kf$, buktikan bahwa

   $$
   g(0)=0,\qquad g'(1)=0,\qquad g''=-f
   $$

   dengan turunan kedua dipahami hampir di mana-mana. Buktikan pula bahwa
   $K$ swadamping dan positif definit.
2. Tentukan seluruh pasangan eigen ternormalisasi $(\lambda_n,e_n)$ dari
   $K$, urut menurun menurut nilai eigennya. Buktikan bahwa $(e_n)_{n\ge1}$
   lengkap dalam $H$, bukan hanya ortonormal.
3. Definisikan

   $$
   \xi_n=\lambda_n^{-1/2}\langle B,e_n\rangle_H.
   $$

   Buktikan bahwa $(\xi_n)_{n\ge1}$ merupakan peubah acak
   $N(0,1)$ yang saling independen dan bahwa

   $$
   B^{(N)}=\sum_{n=1}^N\sqrt{\lambda_n}\,\xi_n e_n
   $$

   konvergen ke $B$ dalam $L^2(\Omega;H)$. Jangan menyimpulkan konvergensi
   seragam lintasan dari hasil ini.
4. Hitung tepat

   $$
   \mathbb E\lVert B-B^{(N)}\rVert_H^2
   $$

   untuk setiap $N$, lalu berikan nilai eksak dan nilai desimalnya ketika
   $N=2$.
5. Misalkan $V\subset H$ sembarang subruang deterministik berdimensi $N$ dan
   $P_V$ proyeksi ortogonal ke $V$. Buktikan langsung bahwa

   $$
   \mathbb E\lVert B-P_VB\rVert_H^2
   \ge
   \mathbb E\lVert B-B^{(N)}\rVert_H^2,
   $$

   dan tentukan kapan kesamaan berlaku.

:::

::: {#unit.o009.mastery.brown.02.hint.01 .hint}

**Petunjuk 1.** Pisahkan integral pada $s=t$:

$$
(Kf)(t)=\int_0^t s f(s)\,ds+t\int_t^1 f(s)\,ds.
$$

Jika $Ke=\lambda e$, diferensiasi mengubah persamaan integral menjadi
$e''+\lambda^{-1}e=0$ dengan satu syarat batas pada $0$ dan satu pada $1$.

:::

::: {#unit.o009.mastery.brown.02.hint.02 .hint}

**Petunjuk 2.** Frekuensi yang memenuhi syarat batas adalah
$\alpha_n=(n-\tfrac12)\pi$. Untuk membuktikan kelengkapan, refleksikan fungsi
$f\in L^2(0,1)$ secara genap terhadap $t=1$ menjadi fungsi pada $(0,2)$.
Koefisien sinus berindeks genap hilang karena simetri, sedangkan koefisien
berindeks ganjil adalah dua kali hasil kali dalam $f$ dengan
$\sin(\alpha_n t)$.

:::

::: {#unit.o009.mastery.brown.02.hint.03 .hint}

**Petunjuk 3.** Untuk basis ortonormal $\phi_1,\ldots,\phi_N$ dari $V$,
tetapkan

$$
a_n=\sum_{j=1}^N|\langle\phi_j,e_n\rangle|^2.
$$

Gunakan $0\le a_n\le1$, $\sum_n a_n=N$, dan urutan ketat
$\lambda_1>\lambda_2>\cdots$ untuk membandingkan
$\sum_n\lambda_na_n$ dengan $\sum_{n=1}^N\lambda_n$.

:::

::: {#unit.o009.mastery.brown.02.answer .answer}

## Jawaban ringkas

Dengan

$$
\alpha_n=(n-\tfrac12)\pi,
\qquad
e_n(t)=\sqrt2\sin(\alpha_nt),
\qquad
\lambda_n=\alpha_n^{-2},
$$

keluarga $(e_n)$ adalah basis ortonormal $L^2[0,1]$. Koefisien
$\xi_n=\alpha_n\langle B,e_n\rangle$ adalah i.i.d. $N(0,1)$ dan

$$
B^{(N)}(t)
=\sum_{n=1}^N\frac{\sqrt2}{\alpha_n}\xi_n\sin(\alpha_nt)
\longrightarrow B
$$

dalam $L^2(\Omega;L^2[0,1])$. Galatnya ialah

$$
\mathbb E\lVert B-B^{(N)}\rVert_2^2
=\sum_{n>N}\frac1{(n-\tfrac12)^2\pi^2}
=\frac12-\frac1{\pi^2}
  \sum_{n=1}^N\frac1{(n-\tfrac12)^2}.
$$

Untuk $N=2$, nilainya
$\frac12-\frac{40}{9\pi^2}=0{,}049683628256\ldots$. Di antara semua
subruang deterministik berdimensi $N$, galat ini minimal secara unik pada
$V=\operatorname{span}\{e_1,\ldots,e_N\}$.

:::

::: {#unit.o009.mastery.brown.02.solution .solution}

## Penyelesaian lengkap

### 1. Struktur operator kovarians

Karena kernel $(s,t)\mapsto\min\{s,t\}$ berada dalam
$L^2([0,1]^2)$, ketaksamaan Cauchy--Schwarz menunjukkan bahwa $K$ adalah
operator terbatas (bahkan Hilbert--Schmidt) dari $H$ ke $H$.

Untuk $f\in H$, tulis

$$
g(t)=(Kf)(t)
=\int_0^t s f(s)\,ds+t\int_t^1f(s)\,ds.
$$

Teorema dasar kalkulus bagi integral Lebesgue memberi

$$
g'(t)=t f(t)+\int_t^1f(s)\,ds-t f(t)
=\int_t^1f(s)\,ds
$$

hampir di mana-mana. Jadi $g(0)=0$, $g'(1)=0$, dan
$g''(t)=-f(t)$ hampir di mana-mana.

Kernel $\min\{s,t\}$ simetris, sehingga Fubini memberi
$\langle Kf,h\rangle=\langle f,Kh\rangle$. Untuk positivitas, gunakan

$$
\min\{s,t\}=\int_0^1
\mathbf1_{\{u\le s\}}\mathbf1_{\{u\le t\}}\,du.
$$

Tonelli menghasilkan

$$
\langle Kf,f\rangle
=\int_0^1\left(\int_u^1f(t)\,dt\right)^2du\ge0.
$$

Jika ruas kanan nol, fungsi kontinu absolut
$F(u)=\int_u^1f(t)\,dt$ sama dengan nol hampir di mana-mana, maka sama dengan
nol di mana-mana. Karena $F'=-f$ hampir di mana-mana, diperoleh $f=0$ dalam
$H$. Jadi $K$ positif definit; khususnya, setiap nilai eigen bernilai positif.

### 2. Nilai eigen, fungsi eigen, dan kelengkapan

Andaikan $Ke=\lambda e$ dengan $e\ne0$. Positivitas definit memberi
$\lambda>0$. Hasil bagian pertama menunjukkan bahwa $e$ mempunyai wakil yang
memenuhi

$$
e''+\lambda^{-1}e=0,
\qquad e(0)=0,
\qquad e'(1)=0.
$$

Dengan $\alpha=\lambda^{-1/2}$, solusi tak nolnya berbentuk
$e(t)=c\sin(\alpha t)$. Syarat $e'(1)=0$ memberi $\cos\alpha=0$, jadi

$$
\alpha_n=(n-\tfrac12)\pi,
\qquad
\lambda_n=\frac1{\alpha_n^2},
\qquad n\ge1.
$$

Karena $\int_0^1\sin^2(\alpha_nt)\,dt=1/2$, normalisasi memberi

$$
e_n(t)=\sqrt2\sin(\alpha_nt).
$$

Sebaliknya, setiap $e_n$ memenuhi persamaan diferensial dan kedua syarat
batas. Jika $h=Ke_n-\lambda_ne_n$, maka $h''=0$, $h(0)=0$, dan $h'(1)=0$;
jadi $h=0$. Dengan demikian, daftar pasangan eigen di atas lengkap sebagai
daftar solusi masalah batas.

Masih harus dibuktikan bahwa rentang linear fungsi-fungsi itu rapat. Misalkan
$f\in L^2(0,1)$ ortogonal terhadap setiap $e_n$. Bentuk refleksi genap terhadap
$1$,

$$
F(t)=
\begin{cases}
f(t),&0<t<1,\\
f(2-t),&1<t<2.
\end{cases}
$$

Untuk basis sinus $\sin(k\pi t/2)$ pada $L^2(0,2)$, simetri
$F(2-t)=F(t)$ membuat semua koefisien dengan $k$ genap sama dengan nol.
Untuk $k=2n-1$, substitusi $t\mapsto2-t$ pada setengah interval kedua memberi

$$
\int_0^2F(t)\sin\!\left(\frac{(2n-1)\pi t}{2}\right)dt
=2\int_0^1f(t)\sin(\alpha_nt)\,dt=0.
$$

Jadi semua koefisien sinus $F$ nol. Kelengkapan basis sinus pada $(0,2)$
memberi $F=0$, sehingga $f=0$. Maka $(e_n)$ lengkap dalam $H$.

### 3. Koefisien Gaussian dan mode konvergensi

Setiap koleksi hingga integral $\langle B,e_n\rangle$ adalah Gaussian:
integral tersebut merupakan limit dalam $L^2(\Omega)$ dari kombinasi linear
hingga nilai-nilai proses Gaussian. Kovariansnya adalah

$$
\begin{aligned}
\mathbb E[\langle B,e_m\rangle\langle B,e_n\rangle]
&=\int_0^1\int_0^1
e_m(s)\min\{s,t\}e_n(t)\,ds\,dt\\
&=\langle Ke_m,e_n\rangle
=\lambda_m\,\mathbf1_{\{m=n\}}.
\end{aligned}
$$

Karena itu, setiap vektor hingga $(\xi_1,\ldots,\xi_r)$ adalah Gaussian
standar dengan matriks kovarians identitas. Jadi $(\xi_n)$ i.i.d. $N(0,1)$.
Selain itu,

$$
\sqrt{\lambda_n}\,\xi_n=\langle B,e_n\rangle,
$$

sehingga $B^{(N)}$ tepat proyeksi ortogonal lintasan $B$ ke
$\operatorname{span}\{e_1,\ldots,e_N\}$. Kelengkapan basis memberi
$B^{(N)}\to B$ dalam $H$ untuk hampir setiap lintasan. Lebih khusus,

$$
0\le\lVert B-B^{(N)}\rVert_H^2\le\lVert B\rVert_H^2,
\qquad
\mathbb E\lVert B\rVert_H^2
=\int_0^1\mathbb E(B_t^2)\,dt
=\frac12.
$$

Konvergensi terdominasi lalu memberi konvergensi dalam
$L^2(\Omega;H)$. Pernyataan ini tidak dengan sendirinya memberi konvergensi
dalam norma supremum pada $C[0,1]$.

### 4. Galat pemotongan eksak

Parseval dan ortogonalitas memberi

$$
\mathbb E\lVert B-B^{(N)}\rVert_H^2
=\sum_{n>N}\mathbb E|\langle B,e_n\rangle|^2
=\sum_{n>N}\lambda_n.
$$

Karena

$$
\sum_{n=1}^{\infty}\frac1{(n-\tfrac12)^2}
=4\sum_{n=1}^{\infty}\frac1{(2n-1)^2}
=4\left(\frac{\pi^2}{6}-\frac14\frac{\pi^2}{6}\right)
=\frac{\pi^2}{2},
$$

diperoleh rumus eksak

$$
\boxed{
\mathbb E\lVert B-B^{(N)}\rVert_H^2
=\frac12-\frac1{\pi^2}
\sum_{n=1}^N\frac1{(n-\tfrac12)^2}}
.
$$

Untuk $N=2$,

$$
\lambda_1+\lambda_2
=\frac4{\pi^2}+\frac4{9\pi^2}
=\frac{40}{9\pi^2},
$$

sehingga

$$
\boxed{
\mathbb E\lVert B-B^{(2)}\rVert_H^2
=\frac12-\frac{40}{9\pi^2}
=0{,}049683628256\ldots}
.
$$

### 5. Optimalitas di antara semua subruang berdimensi $N$

Ambil basis ortonormal $\phi_1,\ldots,\phi_N$ bagi $V$. Teorema Pythagoras
dan definisi operator kovarians memberi

$$
\begin{aligned}
\mathbb E\lVert B-P_VB\rVert_H^2
&=\mathbb E\lVert B\rVert_H^2
-\sum_{j=1}^N\mathbb E|\langle B,\phi_j\rangle|^2\\
&=\frac12-\sum_{j=1}^N\langle K\phi_j,\phi_j\rangle.
\end{aligned}
$$

Ekspansikan setiap $\phi_j$ dalam basis $(e_n)$ dan tetapkan

$$
a_n=\sum_{j=1}^N|\langle\phi_j,e_n\rangle|^2.
$$

Ketaksamaan Bessel memberi $0\le a_n\le1$, sedangkan Parseval dan jumlah
hingga terhadap $j$ memberi $\sum_{n\ge1}a_n=N$. Karena itu,

$$
\sum_{j=1}^N\langle K\phi_j,\phi_j\rangle
=\sum_{n\ge1}\lambda_na_n.
$$

Jika $d=\sum_{n=1}^N(1-a_n)$, maka
$d=\sum_{n>N}a_n$. Karena $\lambda_n$ menurun ketat,

$$
\begin{aligned}
\sum_{n=1}^N\lambda_n-\sum_{n\ge1}\lambda_na_n
&=\sum_{n=1}^N\lambda_n(1-a_n)
-\sum_{n>N}\lambda_na_n\\
&\ge \lambda_Nd-\lambda_{N+1}d\\
&=(\lambda_N-\lambda_{N+1})d\ge0.
\end{aligned}
$$

Jadi energi rata-rata yang ditangkap oleh $V$ paling besar
$\sum_{n=1}^N\lambda_n$, dan galat rata-rata kuadratnya paling kecil sebesar
$\sum_{n>N}\lambda_n$. Jika terjadi kesamaan, ketatnya penurunan nilai eigen
memaksa $d=0$. Maka $a_n=1$ untuk $n\le N$, yaitu setiap $e_n$ dengan
$n\le N$ berada di $V$. Karena dimensi $V$ adalah $N$,

$$
V=\operatorname{span}\{e_1,\ldots,e_N\}.
$$

Sebaliknya, subruang ini jelas mencapai kesamaan. Jadi subruang Karhunen--
Loève pertama adalah peminimum unik di antara semua subruang deterministik
berdimensi $N$.

:::

::: {#unit.o009.mastery.brown.02.rights .rights}

## Hak dan provenans

Soal, petunjuk, jawaban, dan penyelesaian pada unit ini adalah materi baru
berbahasa Indonesia yang disusun untuk edisi ini. Fakta awal bahwa gerak Brown
standar merupakan proses Gaussian dengan kovarians $\min\{s,t\}$ mengikuti
konteks teori [Gerak Brown Standar](../theory/brown/Standard.html); unit ini
tidak menyalin prosa, kode, latihan, atau aset dari halaman tersebut. Saksi
otoritas dan hash halaman sumber dicatat pada metadata.

Seluruh materi baru dalam unit ini dilisensikan di bawah
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), sejauh hak baru
timbul, dengan ID hak
`rights.o009.mastery.brown.02.cc-by-4.0`. Lisensi sumber yang sudah ada tetap
melekat pada sumbernya dan tidak diganti oleh lisensi unit ini. Penyusunan
materi dibantu oleh **OpenAI Codex gpt-5.6-sol, Ultra.**, atas arahan pengguna.
Unit independen ini tidak didukung atau disahkan oleh Kyle Siegrist, Random,
atau penulis sumber.

:::

:::
