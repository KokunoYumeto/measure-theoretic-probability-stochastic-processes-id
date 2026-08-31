---
title: "Penguasaan 01–02: perubahan ukuran dan jembatan kernel Gaussian"
lang: id-ID
author:
  - "Codex (penulisan materi asli atas arahan pengguna)"
authoring:
  course_id: "o009"
  unit_id: "unit.o009.mastery.conditional-kernel.01-02"
  target_locale: "id-ID"
  source_type: "original-mastery"
  rights_id: "rights.o009.mastery.conditional-kernel.01-02.cc-by-4.0"
  license: "CC-BY-4.0"
  model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."
bindings:
  - root_id: "unit.o009.mastery.conditional-kernel.01"
    prerequisite_ids:
      - "unit.o009.original.bridge.regular-conditional-probability"
    outcome_ids:
      - "outcome.o009.mastery.conditional-kernel.bayes-tilt"
  - root_id: "unit.o009.mastery.conditional-kernel.02"
    prerequisite_ids:
      - "unit.o009.original.bridge.regular-conditional-probability"
    outcome_ids:
      - "outcome.o009.mastery.conditional-kernel.gaussian-bridge"
---

::: {#unit.o009.mastery.conditional-kernel.01-02 .original-mastery}

# Penguasaan nilai harapan bersyarat dan kernel

::: {#unit.o009.mastery.conditional-kernel.01 .mastery-sequence prerequisite-ids="unit.o009.original.bridge.regular-conditional-probability" outcome-ids="outcome.o009.mastery.conditional-kernel.bayes-tilt"}

::: {#unit.o009.mastery.conditional-kernel.01.bindings .learning-bindings}
**Ikatan prasyarat.**
unit.o009.original.bridge.regular-conditional-probability: nilai harapan
bersyarat sebagai kelas hampir pasti, integrasi terhadap kernel, dan
disintegrasi pada sasaran Borel standar.

**Ikatan hasil.**
outcome.o009.mastery.conditional-kernel.bayes-tilt: membangun dan membuktikan
kernel Bayes sesudah perubahan ukuran, termasuk penanganan himpunan penyebut
nol.
:::

::: {#unit.o009.mastery.conditional-kernel.01.exercise .exercise}
## Soal 1 — perubahan ukuran dan kernel Bayes

Misalkan $(\Omega,\mathcal F,\mathbb P)$ ruang peluang,
$\mathcal G\subseteq\mathcal F$, dan
$Y:\Omega\to(T,\mathcal T)$ terukur, dengan $(T,\mathcal T)$ Borel standar.
Misalkan

$$
K:(\Omega,\mathcal G)\rightsquigarrow(T,\mathcal T)
$$

merupakan distribusi bersyarat reguler $Y$ terhadap $\mathcal G$ di bawah
$\mathbb P$. Ambil fungsi terukur $h:T\to[0,\infty]$ dengan

$$
c=\mathbb E_{\mathbb P}[h(Y)]\in(0,\infty),
$$

dan definisikan ukuran peluang baru

$$
\mathbb Q(A)=\frac1c\int_A h(Y)\,d\mathbb P,
\qquad A\in\mathcal F.
$$

Untuk $B\in\mathcal T$, tetapkan

$$
Z(\omega)=\int_T h(y)K(\omega,dy),
\qquad
H_B(\omega)=\int_B h(y)K(\omega,dy).
$$

Pilih sembarang $\rho\in\mathcal P(T)$ dan tulis
$D=\{0<Z<\infty\}$. Definisikan

$$
K^h(\omega,B)=
\begin{cases}
\dfrac{H_B(\omega)}{Z(\omega)},&\omega\in D,\\[1.2ex]
\rho(B),&\omega\notin D.
\end{cases}
$$

1. Buktikan bahwa $Z$ adalah satu versi dari
   $\mathbb E_{\mathbb P}[h(Y)\mid\mathcal G]$ dan bahwa
   $\mathbb Q(D^c)=0$.
2. Buktikan bahwa $K^h$ merupakan kernel probabilitas.
3. Buktikan bahwa $K^h$ merupakan distribusi bersyarat reguler $Y$ terhadap
   $\mathcal G$ di bawah $\mathbb Q$.
4. Jika $f:T\to\mathbb R$ terukur dan
   $\mathbb E_{\mathbb Q}|f(Y)|<\infty$, turunkan rumus Bayes untuk
   $\mathbb E_{\mathbb Q}[f(Y)\mid\mathcal G]$ dan nyatakan secara tepat
   perlakuan pada himpunan pengecualian.
:::

::: {#unit.o009.mastery.conditional-kernel.01.hint.01 .hint}
**Petunjuk 1.** Gunakan bentuk fungsi dari kernel bersyarat pada $h$. Untuk
$A=\{Z=0\}\in\mathcal G$, ubah integral
$\int_Ah(Y)\,d\mathbb P$ menjadi $\int_AZ\,d\mathbb P$.
:::

::: {#unit.o009.mastery.conditional-kernel.01.hint.02 .hint}
**Petunjuk 2.** Pada $D$, pemetaan
$B\mapsto H_B(\omega)$ adalah ukuran hingga bermassa total $Z(\omega)$.
Keterukuran $\omega\mapsto H_B(\omega)$ mengikuti dari lemma integral
kernel; penambalan pada $D^c\in\mathcal G$ mempertahankan keterukuran.
:::

::: {#unit.o009.mastery.conditional-kernel.01.hint.03 .hint}
**Petunjuk 3.** Untuk $G\in\mathcal G$, kondisikan faktor $h(Y)$ dalam
$\int_GK^h(\omega,B)h(Y(\omega))\,d\mathbb P$. Pada $D$ berlaku
$K^h(\omega,B)Z(\omega)=H_B(\omega)$; pada $\{Z=0\}$ juga
$H_B=0$ karena $0\le H_B\le Z$.
:::

::: {#unit.o009.mastery.conditional-kernel.01.answer .answer}
**Jawaban ringkas.** $Z=\mathbb E_{\mathbb P}[h(Y)\mid\mathcal G]$
hampir pasti dan $D^c$ adalah himpunan $\mathbb Q$-nol. Kernel yang dicari
ialah normalisasi ukuran tertimbang $hK$ pada $D$, dengan hukum $\rho$
sebagai perbaikan utuh pada $D^c$. Untuk $f$ yang diberikan, satu versi
rumus Bayes adalah

$$
\mathbb E_{\mathbb Q}[f(Y)\mid\mathcal G]
=
\frac{\int_T f(y)h(y)K(\,\cdot\,,dy)}
       {\int_T h(y)K(\,\cdot\,,dy)}
\quad\mathbb Q\text{-hampir pasti},
$$

dengan nilai nol pada himpunan tempat penyebut bukan bilangan positif hingga
atau integral nilai mutlak pembilang tidak hingga.
:::

::: {#unit.o009.mastery.conditional-kernel.01.solution .solution}
**Penyelesaian lengkap.** Bentuk fungsi dari distribusi bersyarat reguler
memberi

$$
Z=\int_T h(y)K(\,\cdot\,,dy)
=\mathbb E_{\mathbb P}[h(Y)\mid\mathcal G]
\quad\mathbb P\text{-hampir pasti}.
$$

Karena $Z\ge0$ dan $\mathbb E_{\mathbb P}Z=c<\infty$, kita mempunyai
$\mathbb P(Z=\infty)=0$. Untuk $A_0=\{Z=0\}\in\mathcal G$,

$$
\mathbb Q(A_0)
=\frac1c\int_{A_0}h(Y)\,d\mathbb P
=\frac1c\int_{A_0}Z\,d\mathbb P
=0.
$$

Selain itu, $\mathbb Q\ll\mathbb P$, sehingga
$\mathbb Q(Z=\infty)=0$. Jadi $\mathbb Q(D^c)=0$.

Untuk $\omega\in D$, pemetaan

$$
B\longmapsto H_B(\omega)
=\int_T\mathbf1_B(y)h(y)K(\omega,dy)
$$

adalah ukuran hingga pada $(T,\mathcal T)$ dengan massa total $Z(\omega)$.
Maka $B\mapsto H_B(\omega)/Z(\omega)$ adalah ukuran peluang. Untuk
$\omega\notin D$, pemetaan itu diganti oleh ukuran peluang utuh $\rho$.
Untuk setiap $B$, lemma integral kernel menunjukkan bahwa $H_B$ dan $Z$
adalah $\mathcal G$-terukur. Karena $D\in\mathcal G$,

$$
K^h(\omega,B)
=\mathbf1_D(\omega)\frac{H_B(\omega)}{Z(\omega)}
 +\mathbf1_{D^c}(\omega)\rho(B)
$$

terukur dalam $\omega$. Jadi $K^h$ adalah kernel probabilitas.

Sekarang ambil $G\in\mathcal G$ dan $B\in\mathcal T$. Karena
$\mathbf1_GK^h(\,\cdot\,,B)$ terukur terhadap $\mathcal G$ dan terbatas,
sifat nilai harapan bersyarat memberi

$$
\begin{aligned}
\int_GK^h(\omega,B)\,\mathbb Q(d\omega)
&=\frac1c\,
  \mathbb E_{\mathbb P}
  [\mathbf1_GK^h(\,\cdot\,,B)h(Y)]\\
&=\frac1c\,
  \mathbb E_{\mathbb P}
  [\mathbf1_GK^h(\,\cdot\,,B)Z].
\end{aligned}
$$

Pada $D$, hasil kali terakhir sama dengan $H_B$. Pada $\{Z=0\}$,
$0\le H_B\le Z$ memberi $H_B=0$; himpunan $\{Z=\infty\}$ adalah
$\mathbb P$-nol. Oleh sebab itu,

$$
\begin{aligned}
\int_GK^h(\omega,B)\,\mathbb Q(d\omega)
&=\frac1c\int_GH_B\,d\mathbb P\\
&=\frac1c\int_G\mathbf1_{\{Y\in B\}}h(Y)\,d\mathbb P\\
&=\mathbb Q(G\cap\{Y\in B\}).
\end{aligned}
$$

Baris kedua kembali memakai bentuk fungsi dari $K$, kini pada
$h\mathbf1_B$. Identitas tersebut membuktikan bahwa $K^h$ adalah distribusi
bersyarat reguler yang diminta.

Terakhir, untuk $f$ dalam soal, definisikan

$$
J(\omega)=\int_T|f(y)|h(y)K(\omega,dy).
$$

Karena

$$
\mathbb E_{\mathbb P}[|f(Y)|h(Y)]
=c\,\mathbb E_{\mathbb Q}|f(Y)|<\infty,
$$

$J$ hingga $\mathbb P$-hampir pasti. Jadi
$D_f=D\cap\{J<\infty\}$ mempunyai komplemen $\mathbb Q$-nol. Fungsi

$$
R_f(\omega)=
\begin{cases}
\displaystyle
\frac{\int_Tf(y)h(y)K(\omega,dy)}{Z(\omega)},
   &\omega\in D_f,\\[2ex]
0,&\omega\notin D_f
\end{cases}
$$

terdefinisi di seluruh $\Omega$ dan terukur terhadap $\mathcal G$. Argumen
integral di atas, mula-mula untuk $f^+$ dan $f^-$, menunjukkan bahwa untuk
setiap $G\in\mathcal G$,

$$
\int_GR_f\,d\mathbb Q=\int_Gf(Y)\,d\mathbb Q.
$$

Karena itu $R_f$ adalah versi dari
$\mathbb E_{\mathbb Q}[f(Y)\mid\mathcal G]$. Nilai nol di $D_f^c$ hanyalah
pilihan versi; hukum $\rho$ dan nilai fungsi di sana tidak dipaksa oleh
$\mathbb Q$.
:::

:::

::: {#unit.o009.mastery.conditional-kernel.02 .mastery-sequence prerequisite-ids="unit.o009.original.bridge.regular-conditional-probability" outcome-ids="outcome.o009.mastery.conditional-kernel.gaussian-bridge"}

::: {#unit.o009.mastery.conditional-kernel.02.bindings .learning-bindings}
**Ikatan prasyarat.**
unit.o009.original.bridge.regular-conditional-probability: komposisi integral
kernel, identitas disintegrasi, dan keunikan hampir di mana-mana.

**Ikatan hasil.**
outcome.o009.mastery.conditional-kernel.gaussian-bridge: memfaktorkan hukum
Markov Gaussian menjadi marginal titik ujung dan kernel jembatan, lalu
memakai kernel itu untuk momen bersyarat dan hukum menara.
:::

::: {#unit.o009.mastery.conditional-kernel.02.exercise .exercise}
## Soal 2 — disintegrasi jembatan Gaussian dua langkah

Untuk $s>0$, tulis

$$
\varphi_s(u)=\frac1{\sqrt{2\pi}s}
\exp\left(-\frac{u^2}{2s^2}\right).
$$

Ambil $a,b>0$ dan ukuran peluang $\mu$ pada $\mathbb R$ dengan momen kedua
hingga. Hukum $(X_0,X_1,X_2)$ ditentukan oleh

$$
\Pi(dx,dy,dz)
=\mu(dx)\,\varphi_a(y-x)\,dy\,
  \varphi_b(z-y)\,dz.
$$

Jadi, setelah $X_0=x$, proses bergerak dua langkah Gaussian independen dengan
varians $a^2$ dan $b^2$. Tetapkan

$$
r^2=a^2+b^2,\qquad
v=\frac{a^2b^2}{a^2+b^2},\qquad
m(x,z)=\frac{b^2x+a^2z}{a^2+b^2}.
$$

1. Buktikan bahwa hukum marginal $(X_0,X_2)$ adalah
   $$
   \nu(dx,dz)=\mu(dx)\varphi_r(z-x)\,dz.
   $$
2. Definisikan
   $$
   B((x,z),A)
   =\int_A\varphi_{\sqrt v}(y-m(x,z))\,dy.
   $$
   Buktikan bahwa $B$ adalah kernel Borel dan distribusi bersyarat reguler
   $X_1$ dengan syarat $(X_0,X_2)$.
3. Hitung
   $\mathbb E[X_1\mid\sigma(X_0,X_2)]$ dan
   $\operatorname{Var}(X_1\mid\sigma(X_0,X_2))$.
4. Integrasikan kembali terhadap hukum $X_2$ dengan syarat $X_0$ untuk
   memverifikasi hukum menara dan dekomposisi varians bersyarat:
   $$
   \mathbb E[X_1\mid X_0]=X_0,
   \qquad
   \operatorname{Var}(X_1\mid X_0)=a^2.
   $$
:::

::: {#unit.o009.mastery.conditional-kernel.02.hint.01 .hint}
**Petunjuk 1.** Konvolusi dua kepadatan Gaussian berpusat memberi
$\varphi_r(z-x)$. Untuk memperoleh kernel jembatan, jangan hanya mengutip
konvolusi: lengkapi kuadrat pada eksponen gabungan dalam variabel $y$.
:::

::: {#unit.o009.mastery.conditional-kernel.02.hint.02 .hint}
**Petunjuk 2.** Buktikan identitas titik demi titik

$$
\varphi_a(y-x)\varphi_b(z-y)
=\varphi_r(z-x)\varphi_{\sqrt v}(y-m(x,z)).
$$

Sesudah itu, Tonelli langsung memberi identitas disintegrasi untuk setiap
pasangan himpunan Borel.
:::

::: {#unit.o009.mastery.conditional-kernel.02.hint.03 .hint}
**Petunjuk 3.** Dengan syarat $(X_0,X_2)=(x,z)$, kernel jembatan adalah
$N(m(x,z),v)$. Untuk bagian terakhir, gunakan
$X_2\mid X_0\sim N(X_0,r^2)$ dan

$$
\operatorname{Var}(X_1\mid X_0)
=\mathbb E[\operatorname{Var}(X_1\mid X_0,X_2)\mid X_0]
 +\operatorname{Var}(\mathbb E[X_1\mid X_0,X_2]\mid X_0).
$$
:::

::: {#unit.o009.mastery.conditional-kernel.02.answer .answer}
**Jawaban ringkas.** Marginal titik ujung ialah
$\mu(dx)\varphi_r(z-x)\,dz$, sedangkan kernel jembatannya

$$
X_1\mid(X_0=x,X_2=z)\sim
N\left(\frac{b^2x+a^2z}{a^2+b^2},
       \frac{a^2b^2}{a^2+b^2}\right).
$$

Jadi

$$
\mathbb E[X_1\mid X_0,X_2]=m(X_0,X_2),
\qquad
\operatorname{Var}(X_1\mid X_0,X_2)=v.
$$

Mengintegrasikan $m$ dan memakai dekomposisi varians terhadap
$X_2\mid X_0\sim N(X_0,r^2)$ menghasilkan masing-masing $X_0$ dan $a^2$.
:::

::: {#unit.o009.mastery.conditional-kernel.02.solution .solution}
**Penyelesaian lengkap.** Pertama, untuk $x,z\in\mathbb R$,

$$
\int_{\mathbb R}
\varphi_a(y-x)\varphi_b(z-y)\,dy
=\varphi_r(z-x),
\qquad r^2=a^2+b^2,
$$

karena ruas kiri adalah kepadatan jumlah dua peubah Gaussian independen
bervarians $a^2$ dan $b^2$. Tonelli lalu memberi, untuk setiap
$C\in\mathcal B(\mathbb R^2)$,

$$
\begin{aligned}
\mathbb P((X_0,X_2)\in C)
&=\int_{\mathbb R}\int_{\mathbb R}
  \mathbf1_C(x,z)\mu(dx)
  \left[\int_{\mathbb R}
  \varphi_a(y-x)\varphi_b(z-y)\,dy\right]dz\\
&=\int_C\mu(dx)\varphi_r(z-x)\,dz.
\end{aligned}
$$

Ini membuktikan rumus untuk $\nu$.

Untuk faktor jembatan, perhitungan kuadrat lengkap memberi

$$
\frac{(y-x)^2}{a^2}+\frac{(z-y)^2}{b^2}
=\frac{(z-x)^2}{r^2}
 +\frac{(y-m(x,z))^2}{v}.
$$

Selain itu, $r\sqrt v=ab$. Kesamaan eksponen dan konstanta normalisasi
memberi identitas

$$
\varphi_a(y-x)\varphi_b(z-y)
=\varphi_r(z-x)\varphi_{\sqrt v}(y-m(x,z)).
$$

Untuk setiap $(x,z)$, $A\mapsto B((x,z),A)$ adalah hukum Gaussian dan
karenanya ukuran peluang. Untuk $A$ tetap, peta

$$
(x,z)\longmapsto
\int_{\mathbb R}\mathbf1_A(y)
\varphi_{\sqrt v}(y-m(x,z))\,dy
$$

Borel karena integrannya Borel nonnegatif dan integral berparameter
mempertahankan keterukuran. Jadi $B$ adalah kernel Borel.

Ambil $C\in\mathcal B(\mathbb R^2)$ dan
$A\in\mathcal B(\mathbb R)$. Identitas faktor serta Tonelli memberi

$$
\begin{aligned}
\mathbb P((X_0,X_2)\in C,\ X_1\in A)
&=\int_C\int_A
  \mu(dx)\,
  \varphi_a(y-x)\varphi_b(z-y)\,dy\,dz\\
&=\int_C
  \left[\int_A
  \varphi_{\sqrt v}(y-m(x,z))\,dy\right]
  \mu(dx)\varphi_r(z-x)\,dz\\
&=\int_C B((x,z),A)\,\nu(dx,dz).
\end{aligned}
$$

Karena itu $B$ merupakan distribusi bersyarat reguler $X_1$ dengan syarat
$(X_0,X_2)$.

Rata-rata dan varians hukum $N(m(x,z),v)$ langsung menghasilkan

$$
\mathbb E[X_1\mid\sigma(X_0,X_2)]
=m(X_0,X_2),
\qquad
\operatorname{Var}(X_1\mid\sigma(X_0,X_2))
=v
$$

hampir pasti. Momen kedua $\mu$ yang hingga memastikan semua peubah yang
dipakai dalam identitas momen ini integrabel sebagaimana diperlukan.

Karena $X_2\mid X_0\sim N(X_0,r^2)$,

$$
\begin{aligned}
\mathbb E[m(X_0,X_2)\mid X_0]
&=\frac{b^2X_0+a^2\mathbb E[X_2\mid X_0]}{r^2}\\
&=\frac{(a^2+b^2)X_0}{r^2}
=X_0.
\end{aligned}
$$

Ini adalah verifikasi eksplisit hukum menara. Untuk varians, $v$ konstan dan
$m(X_0,X_2)$, sebagai fungsi dari $X_2$ dengan $X_0$ tetap, mempunyai
koefisien $a^2/r^2$. Maka

$$
\begin{aligned}
\operatorname{Var}(X_1\mid X_0)
&=v+\operatorname{Var}(m(X_0,X_2)\mid X_0)\\
&=\frac{a^2b^2}{r^2}
 +\frac{a^4}{r^4}\operatorname{Var}(X_2\mid X_0)\\
&=\frac{a^2b^2}{r^2}+\frac{a^4}{r^2}
=a^2.
\end{aligned}
$$

Jadi kernel jembatan mempertahankan baik hukum menara maupun dekomposisi
varians ketika titik ujung kanan diintegrasikan kembali.
:::

:::

::: {#rights.o009.mastery.conditional-kernel.01-02.cc-by-4.0 .rights-provenance}

## Hak dan provenans

Kedua soal, seluruh petunjuk, jawaban, penyelesaian, dan pengorganisasian
matematis pada unit ini merupakan materi asli berbahasa Indonesia yang
disusun untuk edisi ini. Materi baru tersebut dilisensikan di bawah
[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/),
sejauh hak baru timbul. ID hak komponennya adalah
rights.o009.mastery.conditional-kernel.01-02.cc-by-4.0.

Penyusunan materi asli dibantu oleh OpenAI Codex atas arahan pengguna.
Masalah perubahan ukuran dan jembatan Gaussian dirumuskan serta diselesaikan
secara mandiri untuk unit penguasaan ini; prosa, susunan soal, dan
penyelesaiannya tidak disalin dari sumber donor. Fakta standar tentang nilai
harapan bersyarat, integral kernel, dan distribusi Gaussian dipakai sebagai
pengetahuan matematika umum. Lisensi unit ini tidak mengubah hak atas materi
donor atau komponen pihak ketiga mana pun.

:::

:::
