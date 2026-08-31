---
title: "Konstruksi ukuran acak Poisson pada ruang ukuran umum"
lang: id-ID
author:
  - "Codex (penulisan materi asli atas arahan pengguna)"
authoring:
  course_id: "o009"
  unit_id: "unit.o009.original.mastery.poisson-construction.01"
  target_locale: "id-ID"
  source_type: "original"
  rights_id: "rights.o009.original.mastery.poisson-construction.01.cc-by-4.0"
  license: "CC-BY-4.0"
  model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."
---

::: {#unit.o009.original.mastery.poisson-construction.01 .mastery-sequence}

# Konstruksi ukuran acak Poisson pada ruang ukuran umum

::: {#unit.o009.original.mastery.poisson-construction.01.prerequisites-outcomes .mastery-context}

## Prasyarat dan hasil belajar

Prasyarat latihan ini ialah ukuran sigma-hingga, ukuran produk terhitung,
keluarga peubah acak independen, distribusi Poisson beserta fungsi
pembangkitnya, integral terhadap ukuran pencacahan, serta teorema konvergensi
monoton. Definisi proses Poisson pada ruang ukuran umum dapat ditinjau di
[Proses Poisson pada Ruang Umum](../theory/poisson/General.html).

Setelah menyelesaikan latihan ini, pembaca mampu:

1. membangun ukuran acak Poisson secara eksplisit dari cacah Poisson dan titik
   acak yang saling bebas pada partisi sigma-hingga;
2. membuktikan keterukuran, aditivitas terhitung, dan keterhinggaan hampir
   pasti pada setiap himpunan berintensitas hingga;
3. menurunkan fungsional Laplace, hukum cacah Poisson, serta inkremen bebas;
   dan
4. membuktikan bahwa hasil konstruksi tidak bergantung dalam hukum pada
   partisi sigma-hingga yang dipilih.

Konstruksi di sini sengaja langsung: ruang peluang dibentuk sebagai produk
terhitung dan ukuran acaknya berupa jumlah eksplisit ukuran Dirac. Latihan ini
tidak meminta perluasan dari hukum-hukum berdimensi hingga dan tidak memakai
teorema perluasan Kolmogorov.

:::

::: {#unit.o009.original.mastery.poisson-construction.01.exercise .exercise}

## Latihan 9 — membangun ukuran acak Poisson dari partisi sigma-hingga

Misalkan $(S,\mathcal S,\nu)$ adalah ruang ukuran sigma-hingga. Ukuran
$\nu$ boleh beratom dan tidak diasumsikan memiliki topologi. Tuliskan
$\overline{\mathbb N}_0=\mathbb N_0\cup\{\infty\}$, dan lengkapi himpunan
semua ukuran pencacahan pada $(S,\mathcal S)$ dengan sigma-aljabar evaluasi

$$
\mathcal E
=\sigma\{m\mapsto m(A):A\in\mathcal S\}.
$$

1. Mulailah dari penutup sigma-hingga $S=\bigcup_{n\ge1}B_n$ dengan
   $\nu(B_n)<\infty$. Bentuk partisi terukur $(E_n)_{n\ge1}$ atas $S$ dengan
   $\nu(E_n)<\infty$. Untuk setiap indeks
   $j$ dengan $\lambda_j:=\nu(E_j)>0$, definisikan
   $q_j(A)=\nu(A\cap E_j)/\lambda_j$. Pada satu ruang produk terhitung,
   ambil seluruh peubah koordinat berikut secara bersama-sama independen:

   $$
   K_j\sim\operatorname{Pois}(\lambda_j),
   \qquad
   X_{j,1},X_{j,2},\ldots\ \overset{\mathrm{iid}}{\sim}q_j.
   $$

   Definisikan, untuk $A\in\mathcal S$,

   $$
   N(A)
   =\sum_{j:\lambda_j>0}\sum_{m=1}^{K_j}\mathbf 1_A(X_{j,m}).
   \tag{1}
   $$

   Buktikan bahwa untuk setiap hasil dasar, $A\mapsto N(A)$ adalah ukuran
   pencacahan, dan bahwa $N$ merupakan peta terukur menuju ruang ukuran
   pencacahan dengan sigma-aljabar $\mathcal E$.

2. Buktikan bahwa $\mathbb E[N(A)]=\nu(A)$ dalam arti nilai diperluas. Tarik
   kesimpulan bahwa $N(A)<\infty$ hampir pasti apabila $\nu(A)<\infty$.

3. Untuk setiap fungsi terukur $f:S\to[0,\infty]$, buktikan fungsional
   Laplace

   $$
   \mathbb E\!\left[
     \exp\!\left(-\int_S f\,\mathrm dN\right)
   \right]
   =\exp\!\left(
     -\int_S(1-e^{-f})\,\mathrm d\nu
   \right).
   \tag{2}
   $$

4. Deduksikan dari (2) bahwa
   $N(A)\sim\operatorname{Pois}(\nu(A))$ jika $\nu(A)<\infty$, bahwa
   $N(A)=\infty$ hampir pasti jika $\nu(A)=\infty$, dan bahwa cacah pada
   setiap keluarga terhitung himpunan saling lepas adalah independen.

5. Misalkan konstruksi yang sama diulang dengan penutup sigma-hingga lain.
   Buktikan bahwa kedua ukuran acak yang dihasilkan memiliki hukum yang sama
   pada sigma-aljabar evaluasi $\mathcal E$.

Apabila materi dasar memakai parameter kerapatan $r>0$ pada
$(S,\mathcal S,\mu)$, ambil saja $\nu=r\mu$.

:::

::: {#unit.o009.original.mastery.poisson-construction.01.hint.01 .hint}

**Petunjuk 1.** Ganti $(B_n)$ dengan himpunan naik
$C_n=\bigcup_{k\le n}B_k$, lalu ambil $E_n=C_n\setminus C_{n-1}$. Untuk
keterukuran evaluasi, tulis suku dalam (1) sebagai

$$
\sum_{m\ge1}\mathbf 1_{\{m\le K_j\}}\mathbf 1_A(X_{j,m}).
$$

Untuk aditivitas terhitung lintasan demi lintasan, tukarkan hanya deret-deret
tak negatif.

:::

::: {#unit.o009.original.mastery.poisson-construction.01.hint.02 .hint}

**Petunjuk 2.** Bersyarat pada $K_j=k$, kontribusi sel $E_j$ terhadap
$\int f\,\mathrm dN$ adalah jumlah $k$ peubah iid. Jika
$a_j=\int e^{-f}\,\mathrm dq_j$, fungsi pembangkit Poisson memberi

$$
\mathbb E[a_j^{K_j}]
=\exp\{-\lambda_j(1-a_j)\}.
$$

Kalikan identitas ini untuk sejumlah hingga sel, kemudian lewatkan banyaknya
sel ke tak hingga.

:::

::: {#unit.o009.original.mastery.poisson-construction.01.hint.03 .hint}

**Petunjuk 3.** Dalam (2), pakai $f=t\mathbf 1_A$ untuk memperoleh hukum satu
cacah dan pakai
$f=\sum_{i=1}^rt_i\mathbf 1_{A_i}$ untuk himpunan-himpunan saling lepas.
Untuk keunikan hukum, uraikan sembarang keluarga hingga
$A_1,\ldots,A_r$ menjadi atom-atom keanggotaan yang saling lepas, lalu
gunakan sistem-$\pi$ silinder pada ruang ukuran pencacahan.

:::

::: {#unit.o009.original.mastery.poisson-construction.01.answer .answer}

## Jawaban ringkas

Partisi dapat dipilih terukur, saling lepas, menutupi $S$, dan memiliki
ukuran hingga. Pada produk koordinat
$\operatorname{Pois}(\lambda_j)\otimes q_j^{\otimes\mathbb N}$, rumus (1)
adalah jumlah terhitung ukuran Dirac, sehingga merupakan ukuran pencacahan;
setiap evaluasinya adalah jumlah peubah acak tak negatif yang terukur. Lebih
lanjut,

$$
\mathbb E[N(A)]
=\sum_j\lambda_jq_j(A)
=\sum_j\nu(A\cap E_j)
=\nu(A).
$$

Perhitungan bersyarat per sel dan independensi antarsel menghasilkan

$$
\mathbb E e^{-\int f\,\mathrm dN}
=\prod_j
  \exp\!\left[-\int_{E_j}(1-e^{-f})\,\mathrm d\nu\right]
=\exp\!\left[-\int_S(1-e^{-f})\,\mathrm d\nu\right].
$$

Pemilihan $f=t\mathbf 1_A$ memberi hukum Poisson, sedangkan pemilihan fungsi
tangga pada himpunan saling lepas memfaktorkan transformasi Laplace bersama
dan memberi independensi. Semua distribusi evaluasi berdimensi hingga dengan
demikian hanya ditentukan oleh $\nu$; argumen sistem-$\pi$--$\lambda$
memberi keunikan hukum pada $\mathcal E$.

:::

::: {#unit.o009.original.mastery.poisson-construction.01.solution .solution}

## Penyelesaian lengkap

### 1. Partisi, ruang produk, dan sifat ukuran acak

Ambil $C_0=\varnothing$ dan

$$
C_n=\bigcup_{k=1}^nB_k,
\qquad
E_n=C_n\setminus C_{n-1}.
$$

Maka $(E_n)_{n\ge1}$ terukur, saling lepas, menutupi $S$, dan
$\nu(E_n)\le\nu(C_n)<\infty$. Tuliskan

$$
J_+=\{j\ge1:\lambda_j:=\nu(E_j)>0\}.
$$

Untuk $j\in J_+$, $q_j$ adalah ukuran peluang pada $(S,\mathcal S)$ dan
terkonsentrasi pada $E_j$. Ambil ruang peluang produk

$$
(\Omega,\mathcal F,\mathbb P)
=\bigotimes_{j\in J_+}
\left[
  (\mathbb N_0,\mathcal P(\mathbb N_0),
       \operatorname{Pois}(\lambda_j))
  \otimes
  (S^{\mathbb N},\mathcal S^{\otimes\mathbb N},
       q_j^{\otimes\mathbb N})
\right].
\tag{3}
$$

Jika $J_+=\varnothing$, ambil ruang peluang satu titik dan $N=0$. Proyeksi
koordinat pada (3) memberikan $K_j$ serta $X_{j,m}$ dengan seluruh sifat
independensi yang diminta.

Untuk $\omega\in\Omega$, definisikan ukuran

$$
N_\omega
=\sum_{j\in J_+}\sum_{m\ge1}
  \mathbf 1_{\{m\le K_j(\omega)\}}\,\delta_{X_{j,m}(\omega)}.
\tag{4}
$$

Ini adalah jumlah terhitung ukuran positif. Secara eksplisit, jika
$(A_\ell)_{\ell\ge1}$ saling lepas, maka Tonelli untuk deret tak negatif
memberi

$$
\begin{aligned}
N_\omega\!\left(\bigcup_{\ell\ge1}A_\ell\right)
&=\sum_{j,m}\mathbf 1_{\{m\le K_j(\omega)\}}
  \mathbf 1_{\cup_\ell A_\ell}(X_{j,m}(\omega))\\
&=\sum_{j,m}\sum_{\ell\ge1}
  \mathbf 1_{\{m\le K_j(\omega)\}}
  \mathbf 1_{A_\ell}(X_{j,m}(\omega))\\
&=\sum_{\ell\ge1}N_\omega(A_\ell).
\end{aligned}
$$

Nilainya selalu berada dalam $\overline{\mathbb N}_0$, dan
$N_\omega(\varnothing)=0$. Jadi $N_\omega$ adalah ukuran pencacahan. Untuk
$A\in\mathcal S$ tetap,

$$
N(A)
=\sum_{j\in J_+}\sum_{m\ge1}
  \mathbf 1_{\{m\le K_j\}}\mathbf 1_A(X_{j,m})
$$

adalah limit naik jumlah parsial fungsi terukur. Karena itu $N(A)$ terukur.
Sigma-aljabar $\mathcal E$ dibangkitkan tepat oleh seluruh peta evaluasi,
sehingga $\omega\mapsto N_\omega$ terukur menuju ruang ukuran pencacahan.

### 2. Intensitas dan keterhinggaan pada himpunan berukuran hingga

Independensi $K_j$ dan $(X_{j,m})_{m\ge1}$ serta Tonelli memberi

$$
\begin{aligned}
\mathbb E\!\left[
  \sum_{m\ge1}\mathbf 1_{\{m\le K_j\}}
                    \mathbf 1_A(X_{j,m})
\right]
&=\sum_{m\ge1}\mathbb P(K_j\ge m)q_j(A)\\
&=q_j(A)\mathbb E[K_j]\\
&=\lambda_jq_j(A)\\
&=\nu(A\cap E_j).
\end{aligned}
$$

Menjumlahkan lagi dan memakai bahwa $(E_j)$ mempartisi $S$ menghasilkan

$$
\mathbb E[N(A)]
=\sum_{j\in J_+}\nu(A\cap E_j)
=\nu(A).
\tag{5}
$$

Kesamaan ini sah juga ketika kedua ruas bernilai tak hingga. Jika
$\nu(A)<\infty$, (5) memaksa $N(A)<\infty$ hampir pasti: peubah acak tak
negatif yang bernilai $\infty$ pada kejadian berpeluang positif tidak mungkin
memiliki ekspektasi hingga.

### 3. Fungsional Laplace

Tetapkan $f:S\to[0,\infty]$ terukur. Untuk $j\in J_+$, tulis

$$
a_j=\int_S e^{-f(x)}\,q_j(\mathrm dx)\in[0,1].
$$

Bersyarat pada $K_j=k$, titik-titik dalam sel itu iid, sehingga

$$
\mathbb E\!\left[
  \left.
  \exp\!\left(-\sum_{m=1}^{K_j}f(X_{j,m})\right)
  \right|K_j=k
\right]
=a_j^k.
$$

Dengan fungsi pembangkit distribusi Poisson,

$$
\begin{aligned}
\mathbb E\!\left[
  \exp\!\left(-\sum_{m=1}^{K_j}f(X_{j,m})\right)
\right]
&=e^{-\lambda_j}\sum_{k=0}^{\infty}
  \frac{(\lambda_ja_j)^k}{k!}\\
&=\exp[-\lambda_j(1-a_j)]\\
&=\exp\!\left[-\int_{E_j}(1-e^{-f})\,\mathrm d\nu\right].
\end{aligned}
\tag{6}
$$

Biarkan $N^{(n)}$ hanya menjumlahkan sel-sel $E_j$ dengan $j\le n$ dan
$j\in J_+$. Independensi antarsel serta (6) memberikan

$$
\mathbb E\!\left[e^{-\int f\,\mathrm dN^{(n)}}\right]
=\exp\!\left[
  -\int_{\cup_{j\le n}E_j}(1-e^{-f})\,\mathrm d\nu
\right].
\tag{7}
$$

Karena $N^{(n)}\uparrow N$ sebagai ukuran,
$\int f\,\mathrm dN^{(n)}\uparrow\int f\,\mathrm dN$. Ruas kiri di dalam
ekspektasi pada (7) turun dan dibatasi oleh $1$, jadi konvergensi terbatas
berlaku. Pada ruas kanan, konvergensi monoton untuk
$(1-e^{-f})\mathbf 1_{\cup_{j\le n}E_j}$ memberi integral pada seluruh $S$.
Melewatkan $n\to\infty$ dalam (7) membuktikan (2), termasuk kasus ketika
integral pada eksponen bernilai $\infty$.

### 4. Hukum Poisson dan inkremen bebas

Ambil $f=t\mathbf 1_A$ dengan $t\ge0$. Dari (2),

$$
\mathbb E[e^{-tN(A)}]
=\exp\!\left[-\int_A(1-e^{-t})\,\mathrm d\nu\right].
\tag{8}
$$

Untuk $t=0$, kedua ruas pada (8) sama dengan $1$. Untuk $t>0$, integral
tersebut sama dengan $(1-e^{-t})\nu(A)$ dalam arti nilai diperluas, sehingga
ruas kanan dapat ditulis $\exp[-\nu(A)(1-e^{-t})]$ tanpa membentuk hasil kali
tak terdefinisi $0\cdot\infty$.

Jika $\nu(A)<\infty$, ruas kanan adalah transformasi Laplace—atau fungsi
pembangkit pada $z=e^{-t}$—dari distribusi
$\operatorname{Pois}(\nu(A))$. Keunikan fungsi pembangkit pada
$\mathbb N_0$ dan keterhinggaan hampir pasti dari langkah 2 memberi

$$
N(A)\sim\operatorname{Pois}(\nu(A)).
$$

Khusus $\nu(A)=0$, ini adalah distribusi degenerat di nol. Jika
$\nu(A)=\infty$, maka untuk setiap $t>0$ ruas kanan (8) sama dengan nol.
Karena $e^{-tN(A)}>0$ tepat pada kejadian $\{N(A)<\infty\}$, diperoleh
$N(A)=\infty$ hampir pasti.

Sekarang ambil $A_1,\ldots,A_r$ saling lepas dengan
$\nu(A_i)<\infty$ untuk semua $i$, serta $t_1,\ldots,t_r\ge0$.
Untuk $f=\sum_{i=1}^rt_i\mathbf 1_{A_i}$, karena himpunan-himpunan itu
saling lepas, diperoleh

$$
1-e^{-f}
=\sum_{i=1}^r(1-e^{-t_i})\mathbf 1_{A_i}.
$$

Karena itu (2) menjadi

$$
\begin{aligned}
\mathbb E\!\left[
  e^{-\sum_{i=1}^rt_iN(A_i)}
\right]
&=\exp\!\left[-\sum_{i=1}^r
  \nu(A_i)(1-e^{-t_i})\right]\\
&=\prod_{i=1}^r\mathbb E[e^{-t_iN(A_i)}].
\end{aligned}
\tag{9}
$$

Keunikan transformasi Laplace bersama
menunjukkan bahwa cacah-cacahnya independen. Komponen dengan ukuran tak
hingga sama dengan $\infty$ hampir pasti dan karenanya merupakan peubah acak
konstan; menambah komponen semacam itu tidak merusak independensi. Jadi setiap
subkeluarga hingga dari keluarga cacah pada himpunan-himpunan saling lepas
adalah independen. Berdasarkan definisi independensi keluarga terhitung,
seluruh keluarga tersebut independen.

### 5. Ketaktergantungan pada partisi dan keunikan hukum

Misalkan $N$ dan $\widetilde N$ diperoleh dari dua partisi sigma-hingga yang
berbeda. Langkah 4 menunjukkan bahwa keduanya mempunyai hukum Poisson dengan
parameter $\nu(D)$ pada setiap $D\in\mathcal S$, dan mempunyai cacah
independen pada himpunan-himpunan saling lepas.

Ambil $A_1,\ldots,A_r\in\mathcal S$. Untuk setiap himpunan indeks tak kosong
$I\subseteq\{1,\ldots,r\}$, bentuk atom keanggotaan

$$
D_I
=\left(\bigcap_{i\in I}A_i\right)
 \setminus\left(\bigcup_{k\notin I}A_k\right).
\tag{10}
$$

Atom-atom tak kosong pada (10) saling lepas, dan

$$
N(A_i)=\sum_{I:\,i\in I}N(D_I).
\tag{11}
$$

Jika semua $A_i$ berukuran hingga, maka setiap $D_I$ juga berukuran hingga.
Vektor $(N(D_I))_I$ terdiri dari peubah Poisson independen dengan parameter
$(\nu(D_I))_I$; hal yang sama berlaku bagi $\widetilde N$. Rumus (11)
menentukan hukum bersama
$(N(A_1),\ldots,N(A_r))$, sehingga hukum itu sama untuk kedua konstruksi.
Jika beberapa $A_i$ berukuran tak hingga, koordinat yang bersangkutan sama
dengan $\infty$ hampir pasti, sedangkan argumen tadi diterapkan pada semua
koordinat yang berukuran hingga. Jadi seluruh distribusi evaluasi berdimensi
hingga tetap sama.

Terakhir, silinder evaluasi

$$
\left\{
  m:(m(A_1),\ldots,m(A_r))\in H
\right\},
\qquad
H\subseteq\overline{\mathbb N}_0^{\,r},
\tag{12}
$$

membentuk sistem-$\pi$ yang membangkitkan $\mathcal E$. Hukum $N$ dan
$\widetilde N$ sepakat pada setiap silinder (12), karena semua distribusi
evaluasi berdimensi hingganya sama. Teorema sistem-$\pi$--$\lambda$ kemudian
memberikan

$$
\mathcal L(N)=\mathcal L(\widetilde N)
\qquad\text{pada }\mathcal E.
$$

Dengan demikian (1) benar-benar membangun ukuran acak Poisson berintensitas
$\nu$ pada ruang ukuran umum, dan pilihan partisi hanyalah perangkat
konstruksi, bukan bagian dari hukumnya.

:::

::: {#unit.o009.original.mastery.poisson-construction.01.rights-provenance .rights-provenance}

## Hak dan provenans

Soal, tiga petunjuk progresif, jawaban ringkas, dan penyelesaian lengkap pada
berkas ini merupakan materi asli yang ditulis untuk edisi id-ID ini atas
arahan pengguna. Seluruh materi tersebut dilepas dengan lisensi
[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
di bawah pengenal hak
`rights.o009.original.mastery.poisson-construction.01.cc-by-4.0`.

Keterkaitan kurikulernya adalah definisi ukuran acak Poisson dan hukum titik
bersyarat dalam
[Proses Poisson pada Ruang Umum](../theory/poisson/General.html). Berkas ini
tidak menyalin soal atau penyelesaian dari sumber tersebut: konstruksi produk
sigma-hingga, pembuktian fungsional Laplace, dan argumen keunikan pada
sigma-aljabar evaluasi disusun khusus sebagai latihan penguasaan baru. Lisensi
sumber donor tetap terpisah dan tidak diubah.

Pengungkapan produksi: **OpenAI Codex gpt-5.6-sol, Ultra.** Penyebutan sumber
hanya menunjukkan hubungan kurikuler dan provenans intelektual; sumber donor
tidak mendukung, mengesahkan, atau mensponsori materi asli ini.

:::

:::
