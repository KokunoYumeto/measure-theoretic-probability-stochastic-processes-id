---
title: "Penguasaan bersyarat–kernel 05.03: pembaruan Beta melalui komposisi kernel"
lang: id-ID
author:
  - "Codex (penulisan materi asli atas arahan pengguna)"
authoring:
  course_id: "o009"
  unit_id: "unit.o009.mastery.conditional-kernel.03"
  target_locale: "id-ID"
  source_type: "original"
  rights_id: "rights.o009.mastery.conditional-kernel.03.cc-by-4.0"
  license: "CC-BY-4.0"
  model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."
---

::: {#unit.o009.mastery.conditional-kernel.03 .mastery-sequence}

# Penguasaan 05.03 — Komposisi kernel, posterior, dan sifat menara

::: {#unit.o009.mastery.conditional-kernel.03.prerequisites .prerequisites}
**Prasyarat.** Pembaca telah mengenal kernel probabilitas, operator
$Kf(x)=\int f(y)K(x,dy)$, komposisi kernel, karakterisasi integral nilai
harapan bersyarat, sifat menara, dan momen dasar distribusi Beta. Rujukan
konseptualnya ialah unit [nilai harapan bersyarat](../expect/Conditional2.html)
dan [kernel serta operator](../expect/Kernels.html).
:::

::: {#unit.o009.mastery.conditional-kernel.03.outcomes .learning-outcomes}
**Capaian.** Setelah menyelesaikan masalah ini, pembaca mampu memverifikasi
keterukuran kernel berparameter, memperoleh kernel posterior dari identitas
Bayes antarkernel, membuktikan representasi nilai harapan bersyarat dengan
uji integral, menurunkan sifat menara sebagai identitas operator titik demi
titik, serta menghitung perbaikan risiko kuadrat secara eksak.
:::

::: {#unit.o009.mastery.conditional-kernel.03.exercise .exercise}
## Soal — satu pengamatan Bernoulli terhadap keadaan Beta berparameter

Ambil ruang Borel

$$
S=[0,1],\qquad T=(0,1),\qquad E=\{0,1\},
$$

dan biarkan $\pi$ menjadi ukuran Lebesgue yang dibatasi pada $S$ (jadi
$\pi(S)=1$). Untuk $x\in S$, tulis

$$
a_x=1+x,\qquad b_x=2-x,
$$

sehingga $a_x+b_x=3$. Dengan

$$
B(a,b)=\int_0^1 y^{a-1}(1-y)^{b-1}\,dy,
$$

definisikan kernel $K:S\rightsquigarrow T$ dan
$L:T\rightsquigarrow E$ melalui

$$
K(x,dy)
=\frac{y^{a_x-1}(1-y)^{b_x-1}}{B(a_x,b_x)}\,dy,
\qquad
L(y,\{z\})=y^z(1-y)^{1-z}.
$$

Pada $\Omega=S\times T\times E$, definisikan hukum peluang

$$
\mathbb P(F)
=\int_S\pi(dx)\int_TK(x,dy)
  \sum_{z\in E}\mathbf 1_F(x,y,z)L(y,\{z\}),
$$

dan nyatakan proyeksi koordinatnya dengan $(X,Y,Z)$. Jadi, setelah $X=x$
dipilih, $Y$ mempunyai hukum $\operatorname{Beta}(1+x,2-x)$, lalu
$Z$ merupakan satu pengamatan Bernoulli dengan parameter $Y$.

1. Buktikan bahwa $K$ dan $L$ adalah kernel probabilitas. Hitung kernel
   komposisi $M=KL:S\rightsquigarrow E$ secara eksplisit.
2. Bangun kernel $R:(S\times E)\rightsquigarrow T$ yang memenuhi identitas
   Bayes antarkernel
   $$
   M(x,\{z\})R((x,z),dy)=L(y,\{z\})K(x,dy)
   \tag{1}
   $$
   untuk setiap $(x,z)$. Verifikasi bahwa $R$ benar-benar kernel
   probabilitas, termasuk keterukuran terhadap $(x,z)$.
3. Untuk setiap fungsi Borel terbatas $h:T\to\mathbb R$, buktikan langsung
   dari karakterisasi integral bahwa
   $$
   Rh(X,Z)
   \quad\text{adalah versi dari}\quad
   \mathbb E[h(Y)\mid\sigma(X,Z)].
   $$
   Selanjutnya buktikan identitas operator titik demi titik
   $$
   \sum_{z\in E}M(x,\{z\})Rh(x,z)=Kh(x),
   \qquad x\in S,
   \tag{2}
   $$
   dan jelaskan bagaimana (2) menghasilkan sifat menara.
4. Hitung secara eksplisit
   $\mathbb E[Y\mid X]$, $\mathbb E[Y\mid X,Z]$,
   $\mathbb E[Y^2\mid X]$, dan $\mathbb E[Y^2\mid X,Z]$. Periksa (2) untuk
   $h(y)=y^2$ tanpa hanya mengutip sifat menara.
5. Di bawah kerugian kuadrat, bandingkan prediktor Bayes
   $$
   A_0=\mathbb E[Y\mid X],\qquad
   A_1=\mathbb E[Y\mid X,Z].
   $$
   Buktikan optimalitas keduanya pada kelas informasi masing-masing, lalu
   hitung tepat $\mathbb E[(Y-A_0)^2]$,
   $\mathbb E[(Y-A_1)^2]$, dan penurunan risikonya.
:::

::: {#unit.o009.mastery.conditional-kernel.03.hint.01 .hint}
**Petunjuk 1.** Gunakan
$B(a+1,b)/B(a,b)=a/(a+b)$ dan
$B(a,b+1)/B(a,b)=b/(a+b)$. Untuk keterukuran $K(x,C)$, pandang rapatannya
sebagai fungsi Borel bersama dari $(x,y)$, lalu integralkan terhadap $y$.
:::

::: {#unit.o009.mastery.conditional-kernel.03.hint.02 .hint}
**Petunjuk 2.** Perkalian dengan likelihood
$y^z(1-y)^{1-z}$ menaikkan parameter Beta pertama sebesar $z$ dan parameter
kedua sebesar $1-z$. Konstanta yang hilang persis $M(x,\{z\})$.
:::

::: {#unit.o009.mastery.conditional-kernel.03.hint.03 .hint}
**Petunjuk 3.** Uji kandidat nilai harapan bersyarat pada kejadian
$\{X\in A,Z=z\}$; kejadian-kejadian ini membangkitkan $\sigma(X,Z)$. Untuk
risiko, gunakan dekomposisi ortogonal

$$
\mathbb E[(Y-A)^2]
=\mathbb E[(Y-\mathbb E[Y\mid\mathcal G])^2]
 +\mathbb E[(A-\mathbb E[Y\mid\mathcal G])^2]
$$

bagi setiap $A$ yang terukur-$\mathcal G$ dan berkuadrat integrabel.
:::

::: {#unit.o009.mastery.conditional-kernel.03.answer .answer}
## Jawaban ringkas

Komposisinya adalah

$$
M(x,\{1\})=\frac{1+x}{3},
\qquad
M(x,\{0\})=\frac{2-x}{3}.
$$

Kernel posteriornya ialah

$$
R((x,z),dy)
=\frac{y^{x+z}(1-y)^{2-x-z}}
       {B(1+x+z,3-x-z)}\,dy,
$$

yakni $\operatorname{Beta}(1+x+z,3-x-z)$. Identitas (1) memberi sekaligus
karakterisasi integral nilai harapan bersyarat dan, setelah dijumlahkan
terhadap $z$, identitas menara (2). Momen yang diminta adalah

$$
\mathbb E[Y\mid X=x]=\frac{1+x}{3},
\qquad
\mathbb E[Y\mid X=x,Z=z]=\frac{1+x+z}{4},
$$

$$
\mathbb E[Y^2\mid X=x]=\frac{(1+x)(2+x)}{12},
\qquad
\mathbb E[Y^2\mid X=x,Z=z]
=\frac{(1+x+z)(2+x+z)}{20}.
$$

Kedua prediktor adalah proyeksi kuadrat pada informasi masing-masing, dan

$$
\mathbb E[(Y-A_0)^2]=\frac{13}{216},
\qquad
\mathbb E[(Y-A_1)^2]=\frac{13}{288}.
$$

Satu pengamatan $Z$ menurunkan risiko sebesar $13/864$, atau seperempat dari
risiko semula.
:::

::: {#unit.o009.mastery.conditional-kernel.03.solution .solution}
## Penyelesaian lengkap

### 1. Kernel awal dan komposisinya

Untuk $x\in[0,1]$, kedua parameter $a_x$ dan $b_x$ berada dalam $[1,2]$.
Karena itu rapatan $K(x,\cdot)$ taknegatif dan integralnya satu berdasarkan
definisi fungsi Beta. Fungsi

$$
(x,y)\longmapsto
\frac{y^x(1-y)^{1-x}}{B(1+x,2-x)}
$$

bersifat Borel pada $S\times T$: pembilangnya kontinu dan penyebutnya positif
serta kontinu terhadap $x$. Maka, untuk setiap $C\in\mathcal B(T)$, teorema
keterukuran integral berparameter memberi keterukuran
$x\mapsto K(x,C)$. Jadi $K$ adalah kernel probabilitas.

Untuk setiap $y$, dua nilai $L$ adalah $L(y,\{1\})=y$ dan
$L(y,\{0\})=1-y$. Keduanya Borel, taknegatif, dan berjumlah satu. Pada ruang
hingga $E$, fakta-fakta ini cukup untuk menyimpulkan bahwa $L$ adalah kernel
probabilitas.

Komposisi $M=KL$ memenuhi

$$
\begin{aligned}
M(x,\{1\})
&=\int_0^1 y\,K(x,dy)
  =\frac{a_x}{a_x+b_x}=\frac{1+x}{3},\\
M(x,\{0\})
&=\int_0^1(1-y)\,K(x,dy)
  =\frac{b_x}{a_x+b_x}=\frac{2-x}{3}.
\end{aligned}
$$

Kedua nilai berada di $[1/3,2/3]$, sehingga tidak ada penyebut posterior yang
nol dalam soal ini.

### 2. Kernel posterior dan identitas Bayes

Untuk $(x,z)\in S\times E$, definisikan

$$
R((x,z),dy)
=\frac{y^{a_x+z-1}(1-y)^{b_x+1-z-1}}
       {B(a_x+z,b_x+1-z)}\,dy.
\tag{3}
$$

Parameter pada (3) berada dalam $[1,3]$ dan jumlahnya empat. Jadi setiap
baris $R((x,z),\cdot)$ adalah ukuran peluang Beta. Untuk $C$ Borel,
$R((x,z),C)$ terukur terhadap $(x,z)$ dengan argumen integral berparameter
yang sama seperti untuk $K$; koordinat $z$ hanya mengambil dua nilai. Dengan
demikian, $R$ adalah kernel probabilitas.

Tuliskan $m_z(x)=M(x,\{z\})$. Identitas rasio Beta memberi

$$
m_z(x)=\frac{B(a_x+z,b_x+1-z)}{B(a_x,b_x)}.
\tag{4}
$$

Memperkalikan rapatan (3) dengan (4) menghasilkan

$$
\begin{aligned}
m_z(x)R((x,z),dy)
&=\frac{y^{a_x+z-1}(1-y)^{b_x+1-z-1}}
        {B(a_x,b_x)}\,dy\\
&=y^z(1-y)^{1-z}K(x,dy)\\
&=L(y,\{z\})K(x,dy),
\end{aligned}
$$

yang membuktikan (1) sebagai identitas ukuran hingga pada $T$.

### 3. Karakterisasi bersyarat dan sifat menara

Ambil fungsi Borel terbatas $h$. Kernel integral $Rh$ terukur pada
$S\times E$ dan terbatas oleh $\lVert h\rVert_\infty$. Untuk
$A\in\mathcal B(S)$ dan $z\in E$, definisi hukum gabungan serta (1) memberi

$$
\begin{aligned}
\mathbb E[\mathbf1_{\{X\in A,Z=z\}}h(Y)]
&=\int_A\pi(dx)\int_T h(y)L(y,\{z\})K(x,dy)\\
&=\int_A m_z(x)Rh(x,z)\,\pi(dx)\\
&=\mathbb E[\mathbf1_{\{X\in A,Z=z\}}Rh(X,Z)].
\end{aligned}
\tag{5}
$$

Kelas kejadian $\{X\in A,Z=z\}$, setelah ditutup terhadap gabungan hingga,
membentuk suatu aljabar yang membangkitkan $\sigma(X,Z)$. Dari (5), argumen
kelas monoton memperluas kesamaan integral ke seluruh kejadian dalam
$\sigma(X,Z)$. Karena $Rh(X,Z)$ juga terukur terhadap sigma-aljabar itu,

$$
Rh(X,Z)=\mathbb E[h(Y)\mid\sigma(X,Z)]
\quad\text{hampir pasti}.
\tag{6}
$$

Dengan cara yang lebih sederhana, menguji pada $\{X\in A\}$ menunjukkan
bahwa $Kh(X)$ merupakan versi dari
$\mathbb E[h(Y)\mid\sigma(X)]$.

Sekarang (1) dapat dijumlahkan terhadap kedua nilai $z$. Untuk setiap
$x\in S$,

$$
\begin{aligned}
\sum_{z\in E}m_z(x)Rh(x,z)
&=\sum_{z\in E}\int_T h(y)L(y,\{z\})K(x,dy)\\
&=\int_T h(y)\left[\sum_{z\in E}L(y,\{z\})\right]K(x,dy)\\
&=Kh(x).
\end{aligned}
$$

Ini membuktikan (2) bahkan titik demi titik. Bersyarat pada $X=x$, hukum
$Z$ adalah $M(x,\cdot)$; karena itu ruas kiri adalah satu versi dari
$\mathbb E[Rh(X,Z)\mid\sigma(X)]$. Bersama (6), identitas tersebut menjadi

$$
\mathbb E\!\left[
  \mathbb E[h(Y)\mid\sigma(X,Z)]\mid\sigma(X)
\right]
=\mathbb E[h(Y)\mid\sigma(X)],
$$

yaitu sifat menara untuk $\sigma(X)\subseteq\sigma(X,Z)$.

### 4. Momen pertama dan kedua

Jika $U\sim\operatorname{Beta}(a,b)$ dan $s=a+b$, maka

$$
\mathbb E[U]=\frac a s,
\qquad
\mathbb E[U^2]=\frac{a(a+1)}{s(s+1)}.
$$

Untuk $K$, ambil $a=1+x$ dan $s=3$; untuk $R$, ambil
$a'=1+x+z$ dan $s'=4$. Jadi

$$
\mathbb E[Y\mid X=x]=\frac{1+x}{3},
\qquad
\mathbb E[Y\mid X=x,Z=z]=\frac{1+x+z}{4},
\tag{7}
$$

serta

$$
\mathbb E[Y^2\mid X=x]=\frac{(1+x)(2+x)}{12},
\qquad
\mathbb E[Y^2\mid X=x,Z=z]
=\frac{(1+x+z)(2+x+z)}{20}.
\tag{8}
$$

Untuk memeriksa (2) pada $h(y)=y^2$, gunakan (8) dan bobot $M$:

$$
\begin{aligned}
&\frac{1+x}{3}\frac{(2+x)(3+x)}{20}
 +\frac{2-x}{3}\frac{(1+x)(2+x)}{20}\\
&\quad=\frac{(1+x)(2+x)}{60}
  \bigl[(3+x)+(2-x)\bigr]\\
&\quad=\frac{(1+x)(2+x)}{12},
\end{aligned}
$$

tepat sama dengan $Kh(x)$.

### 5. Optimalitas kuadrat dan nilai risiko

Misalkan $\mathcal G$ adalah $\sigma(X)$ atau $\sigma(X,Z)$ dan
$m=\mathbb E[Y\mid\mathcal G]$. Untuk setiap peubah acak
$A\in L^2(\mathcal G)$,

$$
(Y-A)^2=(Y-m)^2+(m-A)^2+2(Y-m)(m-A).
$$

Suku silang mempunyai nilai harapan nol karena $m-A$ terukur-$\mathcal G$
dan $\mathbb E[Y-m\mid\mathcal G]=0$. Maka

$$
\mathbb E[(Y-A)^2]
=\mathbb E[(Y-m)^2]+\mathbb E[(m-A)^2].
\tag{9}
$$

Jadi $m$ meminimumkan risiko, dan kesamaan hanya terjadi bila $A=m$ hampir
pasti. Rumus (9) membuktikan optimalitas $A_0$ dan $A_1$ pada kelas informasi
masing-masing.

Varians Beta memberi

$$
\operatorname{Var}(Y\mid X=x)
=\frac{(1+x)(2-x)}{36}.
$$

Karena $X$ seragam pada $[0,1]$,

$$
\begin{aligned}
\mathbb E[(Y-A_0)^2]
&=\int_0^1\frac{(1+x)(2-x)}{36}\,dx\\
&=\frac1{36}\int_0^1(2+x-x^2)\,dx
=\frac{13}{216}.
\end{aligned}
\tag{10}
$$

Setelah $Z=z$ diamati, varians posteriornya adalah

$$
\operatorname{Var}(Y\mid X=x,Z=z)
=\frac{(1+x+z)(3-x-z)}{80}.
$$

Merata-ratakan dahulu terhadap $Z$ bersyarat pada $X=x$ menghasilkan

$$
\begin{aligned}
&\sum_{z\in E}M(x,\{z\})
  \operatorname{Var}(Y\mid X=x,Z=z)\\
&\quad=\frac{1+x}{3}\frac{(2+x)(2-x)}{80}
 +\frac{2-x}{3}\frac{(1+x)(3-x)}{80}\\
&\quad=\frac{2+x-x^2}{48}.
\end{aligned}
$$

Oleh karena itu,

$$
\mathbb E[(Y-A_1)^2]
=\frac1{48}\int_0^1(2+x-x^2)\,dx
=\frac{13}{288}.
\tag{11}
$$

Dari (10)–(11), penurunan absolutnya ialah

$$
\frac{13}{216}-\frac{13}{288}=\frac{13}{864}.
$$

Karena $13/288=(3/4)(13/216)$, satu pengamatan Bernoulli menurunkan risiko
Bayes sebesar seperempat. Nilai ini diperoleh dari hukum gabungan dan
komposisi kernel, bukan dari klaim bahwa satu pengamatan menentukan keadaan
laten $Y$.
:::

::: {#unit.o009.mastery.conditional-kernel.03.rights-provenance .rights-provenance}
## Hak dan provenans

Soal, petunjuk bertahap, jawaban, dan penyelesaian dalam unit ini merupakan
materi asli berbahasa Indonesia yang disusun untuk edisi ini. Sejauh hak baru
timbul, materi tersebut dilisensikan di bawah
[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
dengan ID hak
`rights.o009.mastery.conditional-kernel.03.cc-by-4.0`.

Penyusunan materi dibantu oleh **OpenAI Codex gpt-5.6-sol, Ultra.** Masalah
Beta–Bernoulli, susunan pembuktian antarkernel, dan perhitungan risiko di sini
ditulis khusus untuk unit ini; tidak ada prosa contoh donor yang disalin.
Definisi dan hasil baku yang dirujuk dari unit teori tetap tunduk pada hak dan
provenans sumbernya masing-masing. Lisensi unit ini hanya mencakup kontribusi
asli pada berkas ini dan tidak melisensikan ulang Random Services, QuantEcon,
MathJax, atau materi pihak lain.
:::

:::
