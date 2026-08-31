---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: '0.9'
    jupytext_version: 1.5.0
kernelspec:
  display_name: Python 3
  language: python
  name: python3
title: "Semigrup dan Generator"
lang: id-ID
course_id: o009
unit_id: unit.o009.quantecon.ctmc.generators
source_commit: 8b06e0aa5a438692445b2c896f9d238c5a7d5eb7
source_path: lectures/generators.md
source_license: CC BY-SA 4.0
target_license: "CC BY-SA 4.0 untuk adaptasi QuantEcon ini"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
non_endorsement: "Edisi independen; tidak didukung atau disahkan oleh QuantEcon maupun penulis sumber."
---

# Semigrup dan Generator

## Gambaran umum

Dalam kuliah-kuliah sebelumnya kita telah melihat bahwa, dalam latar yang
dibahas di sana, setiap matriks intensitas membangkitkan suatu semigrup Markov.

Kita juga telah mengisyaratkan bahwa pasangan tersebut bersifat satu-ke-satu,
dalam arti yang akan diperjelas.

Untuk memperjelas gagasan ini, kita mulai dalam latar abstrak, dengan suatu
masalah nilai awal yang sembarang.

Dalam latar ini kita memperkenalkan semigrup operator umum beserta
generatornya.

Setelah itu, kita dapat kembali ke kasus Markov dan menjelaskan sepenuhnya
hubungan antara matriks intensitas dan semigrup Markov.

Materi di bawah ini relatif teknis. Sebagian besar kerumitannya timbul karena
ruang keadaan dapat berukuran tak berhingga.

Teknisitas semacam ini sulit dihindari karena begitu banyak rantai Markov yang
menarik memang memiliki ruang keadaan tak berhingga.

* Contoh pertama kita—proses Poisson—memiliki ruang keadaan tak berhingga.
* Contoh lain adalah kajian antrean, yang sering kali tidak memiliki batas
  atas alami.[^footnotepp]

[^footnotepp]: Bahkan, salah satu perhatian utama dalam teori antrean adalah
  memastikan bahwa panjang antrean tidak meledak menuju tak berhingga. Masalah
  ini tidak dapat dikaji dengan benar kecuali ruang keadaannya boleh tak
  berhingga.

Pembaca diasumsikan memiliki pengetahuan dasar tentang
[ruang Banach](https://en.wikipedia.org/wiki/Banach_space).

## Motivasi

Teori umum semigrup operator kontinu dimotivasi oleh masalah penyelesaian ODE
linear dalam ruang berdimensi tak berhingga.[^fnpde]

[^fnpde]: Pengantar yang sangat baik mengenai semigrup operator, beserta
  penerapannya pada PDE dan proses Markov, dapat ditemukan dalam
  {cite}`applebaum2019semigroups`.

Lebih khusus lagi, tantangannya adalah menyelesaikan masalah nilai awal seperti

$$
    x'_t = A x_t,
    \quad x_0 \text{ diberikan}
$$ (abscp)

dengan

* $x_t$ bernilai di suatu ruang Banach pada setiap waktu $t$,
* $A$ merupakan operator linear, dan
* turunan waktu $x'_t$ memakai definisi yang sesuai untuk ruang Banach.

Masalah ini juga disebut “masalah Cauchy abstrak”.

Mengapa kita perlu menyelesaikan masalah seperti ini?

Salah satu contohnya berasal dari PDE.

PDE memberi tahu kita bagaimana fungsi berubah seiring waktu, bermula dari
deskripsi infinitesimal.

Ketika $x_t$ merupakan suatu titik dalam ruang fungsi, masalah tersebut cocok
dengan kerangka {eq}`abscp`.

Contoh lain berasal dari proses Markov. Seperti yang telah kita lihat, aliran
distribusi sepanjang waktu dapat direpresentasikan sebagai ODE linear dalam
ruang distribusi.

Jika banyaknya keadaan tak berhingga, ruang distribusinya pun berdimensi tak
berhingga.

Ini merupakan versi lain dari {eq}`abscp`; kita akan kembali kepadanya setelah
membahas teori umum.

Sebagai gambaran tingkat tinggi tentang hasil-hasil di bawah, solusi masalah
Cauchy direpresentasikan sebagai lintasan $t \mapsto U_t x_0$ dari nilai awal
$x_0$ di bawah suatu semigrup pemetaan $(U_t)$.

Operator $A$ dalam {eq}`abscp` disebut “generator” dari $(U_t)$ dan merupakan
deskripsi infinitesimalnya.

> **Catatan ruang lingkup hilir.** Jika $A$ mungkin tak terbatas, lintasan
> $U_tx_0$ merupakan solusi klasik dari {eq}`abscp` hanya di bawah syarat domain
> dan keteraturan yang sesuai—khususnya $x_0\in D(A)$. Untuk $x_0$ umum,
> $U_tx_0$ ditafsirkan sebagai solusi ringan (*mild solution*). Dalam kasus UC
> yang dibahas di bawah, generatornya terbatas dan $D(A)=\BB$, sehingga pembedaan ini tidak
> menimbulkan masalah.

## Pendahuluan teknis

Sepanjang kuliah ini, $(\BB, \| \cdot \|)$ adalah ruang Banach.

### Ruang Operator Linear

Ingat bahwa **operator linear** pada $\BB$ adalah pemetaan $A$ dari $\BB$ ke
dirinya sendiri yang memenuhi

$$
    A(\alpha g + \beta h) = \alpha A g + \beta A h,
    \quad
    \forall \, g, h \in \BB, \;\; \alpha, \beta \in \RR
$$

Operator $A$ disebut **terbatas** jika

$$
    \| A \| := \sup_{g \in \BB, \, \| g \| \leq 1} \| A g \| < \infty
$$ (norml)

Ini adalah definisi biasa bagi
[operator linear terbatas](https://en.wikipedia.org/wiki/Bounded_operator)
pada ruang linear bernorma.

Himpunan semua operator linear terbatas pada $\BB$ dinotasikan dengan $\linop$
dan merupakan ruang Banach.

Penjumlahan dan perkalian skalar unsur-unsur $\linop$ didefinisikan dengan cara
biasa. Jadi, untuk $\alpha \in \RR$, $A,B\in\linop$, dan $g\in\BB$, berlaku

$$
    (A + B) g = Ag + Bg,
    \quad (\alpha A) g = \alpha (A g)
$$

dan seterusnya.

Kita menulis $AB$ untuk menyatakan komposisi operator $A,B\in\linop$.

Nilai yang didefinisikan dalam {eq}`norml` disebut
[**norma operator**](https://en.wikipedia.org/wiki/Operator_norm) dari $A$ dan,
seperti ditunjukkan notasinya, merupakan norma pada $\linop$.

Selain merupakan norma, norma operator memiliki sifat submultiplikatif
$\|AB\|\leq\|A\|\|B\|$ untuk semua $A,B\in\linop$.

Misalkan $I$ adalah identitas dalam $\linop$, sehingga $Ig=g$ untuk setiap
$g\in\BB$.

(Sesungguhnya, $\linop$ adalah
[aljabar Banach unital](https://en.wikipedia.org/wiki/Banach_algebra) apabila
perkalian diidentifikasi dengan komposisi operator dan $I$ dipakai sebagai
unsur identitasnya.)

### Fungsi Eksponensial

Untuk $A\in\linop$, eksponensial $A$ adalah unsur $\linop$ yang didefinisikan
oleh

$$
    e^A
    = \sum_{k \geq 0} \frac{A^k}{k!}
    = I + A + \frac{A^2}{2!} + \cdots
$$ (opexpo)

Definisi ini sama dengan definisi eksponensial matriks. Fungsi eksponensial
muncul secara alami sebagai solusi ODE dalam ruang Banach. Salah satu contohnya,
seperti akan kita lihat, ialah aliran distribusi yang berkaitan dengan rantai
Markov waktu kontinu.

Pemetaan eksponensial memiliki sifat-sifat berikut:

* Untuk setiap $A\in\linop$, operator $e^A$ merupakan unsur $\linop$ yang
  terdefinisi dengan baik dan $\|e^A\|\leq e^{\|A\|}$.[^fncoex]
* $e^0=I$, dengan $0$ unsur nol dalam $\linop$.
* Jika $A,B\in\linop$ dan $AB=BA$, maka $e^{A+B}=e^Ae^B$.
* Jika $A\in\linop$, maka $e^A$ dapat dibalik dan $(e^A)^{-1}=e^{-A}$.

Fakta terakhir mudah diperiksa dari fakta-fakta sebelumnya.

[^fncoex]: Konvergensi deret dalam {eq}`opexpo` mengikuti keterbatasan $A$ dan
  fakta bahwa $\linop$ merupakan ruang Banach.

### Kalkulus Operator

Tinjau fungsi

$$
    \RR_+ \ni t \mapsto U_t \in \linop
$$

yang dapat kita pandang sebagai lintasan waktu dalam $\linop$, misalnya aliran
operator Markov.

Kita mengatakan bahwa fungsi ini **terdiferensialkan di
$\tau\in\RR_+$** apabila terdapat unsur $T$ dari $\linop$ sedemikian sehingga

$$
    \frac{U_{\tau+h} - U_\tau}{h} \to T
    \; \text{ ketika } h \to 0
$$ (devlim)

Dalam hal ini, $T$ disebut **turunan** fungsi $t\mapsto U_t$ di $\tau$, dan
kita menulis

$$
    T = U'_\tau
    \; \text{ atau } \;
    T = \frac{d}{dt} U_t \, \Big|_{t=\tau}.
$$

(Konvergensi operator berlangsung dalam norma operator. Jika $\tau=0$, limit
$h\to0$ dalam {eq}`devlim` adalah limit kanan.)

```{prf:example}
:label: generators-prf-1
Jika $U_t=tV$ untuk suatu $V\in\linop$ yang tetap, mudah dilihat bahwa $V$
adalah turunan $t\mapsto U_t$ pada setiap $t\in\RR_+$.
```

```{prf:example}
:label: generators-prf-2
Dalam {doc}`pembahasan kita <kolmogorov_fwd>` mengenai persamaan Kolmogorov maju
ketika $S$ berhingga, kita memperkenalkan turunan pemetaan $t\mapsto P_t$,
dengan setiap $P_t$ merupakan matriks pada $S$.

Turunan tersebut didefinisikan dengan menurunkan $P_t$ unsur demi unsur.

Ini berimpit dengan definisi operator-teoretis dalam {eq}`devlim` ketika $S$
berhingga. Dalam hal itu, ruang $\lL(\ell_1(S))$ yang terdiri atas semua
operator linear terbatas pada $\ell_1(S)$ berdimensi berhingga, sehingga
konvergensi titik demi titik dan konvergensi norma berimpit.

> **Catatan klarifikasi hilir.** Sumber menulis $\ell_1$ tanpa menampilkan
> ketergantungannya pada $S$. Ruang $\ell_1$ standar pada barisan tak berhingga
> bukan berdimensi berhingga; klaim di atas berlaku karena di sini yang
> dimaksud adalah $\ell_1(S)$ untuk himpunan keadaan berhingga $S$.
```

Seperti pada kasus matriks dan skalar, kita memperoleh hasil berikut.

```{prf:lemma} Keterdiferensialan Kurva Eksponensial
:label: diffexpmap

Untuk setiap $A\in\linop$, kurva eksponensial $t\mapsto e^{tA}$
terdiferensialkan di setiap titik dan

$$
    \frac{d}{dt} e^{tA} = e^{tA} A = A e^{tA}.
$$ (expdiffer)
```

Pembuktiannya menjadi latihan yang telah dilengkapi solusi di bawah.

## Semigrup dan Generator

Untuk rantai Markov waktu kontinu dengan ruang keadaan berhingga $S$, kita
telah melihat bahwa semigrup Markov sering berbentuk $P_t=e^{tQ}$ bagi suatu
matriks intensitas $Q$.

Bentuk ini ideal karena seluruh semigrup dicirikan secara sederhana oleh
deskripsi infinitesimalnya, yaitu $Q$.

Ternyata, ketika $S$ berhingga, pernyataan ini selalu benar: jika $(P_t)$
merupakan semigrup Markov, terdapat matriks intensitas $Q$ yang memenuhi
$P_t=e^{tQ}$ untuk setiap $t$.

Selain itu, pernyataan tersebut tetap benar ketika $S$ tak berhingga, asalkan
semigrupnya memenuhi beberapa pembatasan.

> **Catatan ruang lingkup hilir.** Pernyataan ruang keadaan berhingga memakai
> pengertian semigrup Markov yang kontinu di waktu nol. Untuk ruang keadaan tak
> berhingga, matriks intensitas umum dapat menimbulkan ledakan, kehilangan
> massa, atau masalah ketunggalan; karena itu pembatasan yang disebut pada
> kalimat sebelumnya benar-benar diperlukan untuk memperoleh semigrup Markov
> yang konservatif (*honest*), dengan massa total tetap satu.

Tujuan kita adalah merumuskan pernyataan-pernyataan ini secara tepat, mula-mula
dalam latar abstrak lalu melalui spesialisasi.

### Semigrup Operator

Misalkan $U_t$ merupakan unsur $\linop$ untuk setiap $t\in\RR_+$.

Kita mengatakan bahwa $(U_t)$ adalah **semigrup evolusi** pada $\BB$ jika
$U_0=I$ dan $U_{s+t}=U_sU_t$ untuk setiap $s,t\geq0$.

> **Catatan koreksi hilir.** Sumber menyebut semigrup evolusi “pada
> $\linop$”. Keluarga tersebut terdiri atas operator dalam $\linop$, tetapi
> bertindak pada ruang Banach $\BB$; formulasi standar dan konsisten dengan
> definisi-definisi berikut adalah “semigrup pada $\BB$”.

Gagasannya ialah bahwa $(U_t)$ menghasilkan lintasan dalam $\BB$ dari setiap
titik awal $g\in\BB$, sehingga $U_tg$ ditafsirkan sebagai letak keadaan setelah
$t$ satuan waktu.

Semigrup evolusi $(U_t)$ disebut

* $C_0$ **semigrup** pada $\BB$ jika, untuk setiap $g\in\BB$, pemetaan
  $t\mapsto U_tg$ dari $\RR_+$ ke $\BB$ kontinu; dan
* **semigrup kontinu seragam** pada $\BB$ jika pemetaan $t\mapsto U_t$ dari
  $\RR_+$ ke $\linop$ kontinu.

Mengikuti istilah sumber *uniformly continuous*, selanjutnya kita
mempertahankan singkatan UC untuk “kontinu seragam”.[^ucnote]

[^ucnote]: Hati-hati: definisi semigrup UC mensyaratkan agar $t\mapsto U_t$
  kontinu sebagai pemetaan ke $\linop$, bukan agar pemetaan itu kontinu seragam
  dalam variabel waktu. Istilah UC muncul karena, bagi semigrup UC, definisi
  norma operator memberi
  $\sup_{\|g\|\leq1}\|U_sg-U_tg\|\to0$ ketika $s\to t$.

```{prf:example} Kurva eksponensial adalah semigrup UC
:label: ecuc

Jika $U_t=e^{tA}$ untuk $t\in\RR_+$ dan $A\in\linop$, maka $(U_t)$ merupakan
semigrup kontinu seragam pada $\BB$.
```

Klaim bahwa $(U_t)$ merupakan semigrup evolusi langsung mengikuti sifat-sifat
fungsi eksponensial di atas.

Kontinuitas dalam norma dapat dibuktikan dengan argumen yang serupa dengan
argumen dalam pembuktian keterdiferensialan pada {prf:ref}`diffexpmap`.

Karena konvergensi norma pada $\linop$ menyiratkan konvergensi titik demi titik,
setiap semigrup kontinu seragam merupakan semigrup $C_0$.

Kebalikannya tentu tidak benar—banyak semigrup $C_0$ penting yang tidak
kontinu seragam.

Bahkan, semigrup yang berkaitan dengan PDE, difusi, dan proses Markov lain pada
ruang keadaan kontinu biasanya merupakan semigrup $C_0$ tetapi bukan semigrup
kontinu seragam.

Ada pula contoh penting semigrup Markov pada ruang keadaan diskret tak
berhingga yang tidak kontinu seragam.

Namun, kita akan segera melihat bahwa bagi sebagian besar rantai Markov waktu
kontinu yang dipakai dalam penerapan, semigrupnya kontinu seragam.

### Generator

Tinjau rantai Markov waktu kontinu pada ruang keadaan berhingga dengan matriks
intensitas $Q$.

Semigrup Markov $(P_t)$ ditentukan sepenuhnya oleh deskripsi infinitesimal $Q$,
dalam arti bahwa

* $P_t=e^{tQ}$ untuk setiap $t\geq0$; dan, secara ekuivalen,
* persamaan maju dan mundur berlaku: $P_t'=P_tQ=QP_t$.

Karena $P_0=I$, matriks $Q$ dapat diperoleh kembali dari semigrup melalui

$$
    Q = P'_0 = \lim_{h \downarrow 0} \frac{P_h - I}{h}.
$$

Dalam latar semigrup $C_0$ yang lebih abstrak, kita mengatakan bahwa $Q$
adalah “generator” semigrup $(P_t)$.

Secara lebih umum, jika $(U_t)$ merupakan semigrup $C_0$, **generator** dari
$(U_t)$ adalah operator linear $A:D(A)\subseteq\BB\to\BB$ yang didefinisikan
oleh

$$
    A g = \lim_{h \downarrow 0} \frac{U_h g - g}{h}
$$ (defgenr)

untuk semua $g\in\BB$ yang limitnya ada.

Himpunan titik tempat limit tersebut ada—domain generator—dinotasikan dengan
$D(A)$.

> **Catatan klarifikasi hilir.** Sumber mula-mula menyebut $A$ sebagai operator
> dari seluruh $\BB$ ke dirinya sendiri, lalu mendefinisikan $D(A)$ sebagai
> himpunan titik tempat limit ada. Penulisan $A:D(A)\subseteq\BB\to\BB$ di atas
> menyatakan tipe operator yang mungkin tak terbatas secara tepat.

Pada tahap ini kita ingin menulis {eq}`defgenr` sebagai $A=U'_0$, atau
menyatakan $U_t$ sebagai $e^{tA}$, analog dengan kasus Markov.

Namun, ada beberapa masalah.

Pertama, limit dalam {eq}`defgenr` dapat gagal ada untuk sebagian $g\in\BB$.

Memang, mengapa limit itu harus ada, sementara semigrup $C_0$ tidak disyaratkan
terdiferensialkan?

Kedua, sekalipun limitnya ada, operator linear $A$ dapat tak terbatas—yakni,
bukan unsur $\linop$—sehingga pernyataan seperti $U_t=e^{tA}$ menjadi
bermasalah.

Walaupun demikian, teori semigrup $C_0$ ternyata sangat kuat. Dengan sejumlah
pekerjaan, masalah teknis tersebut dapat diatasi.[^fnhy]

[^fnhy]: Uraian yang sangat baik mengenai teori umum semigrup $C_0$ dapat
  ditemukan dalam {cite}`bobrowski2005functional`.

Lebih baik lagi, untuk penerapan yang hendak kita tinjau, kita dapat berfokus
pada semigrup UC, yang tidak menghadapi masalah-masalah tersebut.

Bagian berikut memberikan rinciannya.

### Karakterisasi Semigrup Kontinu Seragam

Dalam {prf:ref}`ecuc` kita melihat bahwa kurva eksponensial merupakan contoh
semigrup UC.

Teorema berikut memberi tahu kita bahwa tidak ada contoh lain.

```{prf:theorem} Semigrup UC adalah Kurva Eksponensial
:label: ucsgec

Jika $(U_t)$ merupakan semigrup UC pada $\BB$, terdapat $A\in\linop$ sedemikian
sehingga $U_t=e^{tA}$ untuk setiap $t\geq0$. Selain itu,

* $U_t$ terdiferensialkan pada setiap $t\geq0$,
* $A$ adalah generator dari $(U_t)$, dan
* $U_t'=AU_t=U_tA$ untuk setiap $t\geq0$.
```

Tiga klaim terakhir dalam {prf:ref}`ucsgec` langsung mengikuti klaim pertama.

Pernyataan $U_t'=AU_t=U_tA$ merupakan generalisasi persamaan Kolmogorov maju
dan mundur.

Walaupun sedikit lebih rumit dalam latar Banach, pembuktian klaim pertama—
adanya representasi eksponensial—merupakan perluasan langsung dari fakta bahwa
setiap fungsi kontinu $f$ dari $\RR_+$ ke $\RR$ yang memenuhi

* $f(s)f(t)=f(s+t)$ untuk setiap $s,t\geq0$; dan
* $f(0)=1$

juga memenuhi $f(t)=e^{ta}$ untuk suatu $a\in\RR$ dan setiap $t\geq0$.

> **Catatan koreksi hilir.** Sumber menuliskan domain $f$ sebagai $\RR$, tetapi
> hanya mengasumsikan persamaan fungsional untuk argumen tak negatif. Domain dan
> kesimpulan di atas dibatasi pada $\RR_+$, tepat sesuai hipotesis yang
> dinyatakan.

Kita membuktikan hal yang sangat serupa dalam {prf:ref}`exp_unique`, mengenai
sifat tanpa ingatan fungsi eksponensial.

Untuk pembahasan lebih lanjut tentang kasus skalar, lihat, misalnya,
{cite}`sahoo2011introduction`.

Untuk pembuktian lengkap klaim pertama dalam {prf:ref}`ucsgec`, dalam latar
aljabar Banach, lihat, misalnya, Bab 7 dari {cite}`bobrowski2005functional`.

## Latihan

```{exercise}
:label: generators-ex-1

Buktikan bahwa {eq}`expdiffer` berlaku untuk setiap $A\in\linop$.
```

```{solution} generators-ex-1
:class: dropdown

Untuk membuktikan kesamaan pertama, tetapkan $t\in\RR_+$ dan ambil $h\neq0$
dengan $t+h\geq0$. Karena $tA$ dan $hA$ saling komutatif,

$$
e^{(t+h)A} - e^{tA} - h e^{tA} A
= e^{tA} (e^{hA} - I - hA).
$$

Sifat submultiplikatif norma pada $\linop$ memberi

$$
\left\|
\frac{e^{(t+h)A}-e^{tA}}{h}-e^{tA}A
\right\|
\leq
\|e^{tA}\|\,
\frac{\|e^{hA}-I-hA\|}{|h|}.
$$

Dari definisi eksponensial dan sifat submultiplikatif,

$$
\|e^{hA}-I-hA\|
\leq \sum_{k\geq2}\frac{|h|^k\|A\|^k}{k!}
=e^{|h|\|A\|}-1-|h|\|A\|
=O(h^2)=o(|h|).
$$

Jadi ruas kanan menuju nol ketika $h\to0$. Untuk $t>0$ argumen ini mencakup
kenaikan positif dan negatif; untuk $t=0$ limitnya memang limit kanan. Kita
memperoleh kesamaan pertama dalam {eq}`expdiffer`, yaitu

$$
\frac{d}{dt}e^{tA}=e^{tA}A.
$$

Karena $A$ komutatif dengan setiap pangkatnya sendiri, $A$ juga komutatif
dengan $e^{tA}$. Maka $e^{tA}A=Ae^{tA}$, yang membuktikan kesamaan kedua.

> **Catatan koreksi hilir.** Dalam dua tempat, solusi sumber menghilangkan
> faktor $h$: ia menulis sisa dengan $-e^{tA}A$ dan $-I-A$. Dengan bentuk itu
> sisanya tidak bernilai $o(h)$. Faktor $h$, estimasi deret, dan limit dari dua
> sisi pada titik interior dipulihkan di atas.
```

```{exercise}
:label: generators-ex-2

Dalam banyak buku, semigrup $C_0$ didefinisikan sebagai semigrup evolusi
$(U_t)$ sedemikian sehingga

$$
U_t g \to g \text{ ketika } t \to 0 \text{ untuk setiap } g \in \BB.
$$ (czsg2)

Tujuan kita adalah menunjukkan bahwa {eq}`czsg2` menyiratkan kontinuitas pada
setiap titik $t$, seperti dalam definisi yang kita gunakan di atas.

[Teorema Banach–Steinhaus](https://en.wikipedia.org/wiki/Uniform_boundedness_principle)
dapat dipakai untuk menunjukkan bahwa, bagi semigrup evolusi $(U_t)$ yang
memenuhi {eq}`czsg2`, terdapat konstanta berhingga $\omega$ dan $M$ sedemikian
sehingga

$$
\| U_t \| \leq e^{t\omega} M
\quad \text{untuk setiap } \; t \geq 0.
$$ (sgbound)

Gunakan fakta ini bersama {eq}`czsg2` untuk menunjukkan bahwa, bagi setiap
$g\in\BB$, pemetaan $t\mapsto U_tg$ kontinu pada semua $t$.
```

```{solution} generators-ex-2
:class: dropdown

Misalkan $(U_t)$ merupakan semigrup evolusi yang memenuhi {eq}`czsg2`, dan
misalkan $\omega$ serta $M$ seperti dalam {eq}`sgbound`.

Pilih sembarang $g\in\BB$ dan $t>0$. Untuk $h\downarrow0$, di satu sisi,

$$
U_{t+h}g=U_hU_tg\to U_tg
$$

menurut {eq}`czsg2`, yang diterapkan pada vektor tetap $U_tg$.

Di sisi lain, untuk $0<h<t$, dari {eq}`sgbound` dan definisi norma operator,

$$
\| U_{t-h} g - U_t g\|
= \|  U_{t-h} ( g - U_h g) \|
\leq e^{(t-h)\omega} M \| g - U_h g\|
\to 0.
$$

Jadi limit kanan dan limit kiri di $t$ sama dengan $U_tg$. Pada $t=0$ hanya
limit kanan yang relevan dan itulah {eq}`czsg2`. Karena setiap barisan
$t_n\to t$ akhirnya dapat dipisahkan menjadi suku-suku dari kanan, dari kiri,
dan yang sama dengan $t$, kita memperoleh $U_{t_n}g\to U_tg$. Dengan demikian
$t\mapsto U_tg$ kontinu pada setiap $t\in\RR_+$.

> **Catatan pelengkapan hilir.** Solusi sumber menampilkan dua limit bagi
> $h_n\downarrow0$, tetapi berhenti sebelum menghubungkannya secara eksplisit
> dengan barisan umum yang mendekati $t$. Langkah sekuensial terakhir di atas
> menutup kesimpulan yang diminta.
```

```{exercise}
:label: generators-ex-3

Melanjutkan latihan sebelumnya, semigrup UC sering didefinisikan sebagai
semigrup evolusi $(U_t)$ sedemikian sehingga

$$
\| U_t - I \| \to 0 \text{ ketika } t \to 0.
$$ (czsg3)

Tunjukkan bahwa {eq}`czsg3` menyiratkan kontinuitas norma pada setiap titik
$t$, seperti dalam definisi yang kita gunakan di atas.

Secara khusus, tunjukkan bahwa untuk setiap $t_n\to t$ berlaku
$\|U_{t_n}-U_t\|\to0$ ketika $n\to\infty$.
```

```{solution} generators-ex-3
:class: dropdown

Solusinya serupa dengan solusi latihan sebelumnya.

Perhatikan lebih dahulu bahwa {eq}`czsg3` menyiratkan {eq}`czsg2`, sebab

$$
\|U_tg-g\|\leq\|U_t-I\|\,\|g\|\to0.
$$

Karena itu, batas {eq}`sgbound` tersedia. Tetapkan $t>0$. Untuk
$h\downarrow0$, di satu sisi,

$$
\|U_{t+h}-U_t\|
=\|(U_h-I)U_t\|
\leq\|U_h-I\|\,\|U_t\|
\to0.
$$

Di sisi lain, untuk $0<h<t$, sifat submultiplikatif norma operator dan
{eq}`sgbound` memberi

$$
\| U_{t-h} - U_t \|
= \|  U_{t-h} ( I - U_h) \|
\leq e^{(t-h)\omega} M  \| I - U_h \|
\to0.
$$

Pada $t=0$, {eq}`czsg3` sendiri memberi kontinuitas kanan. Dengan memisahkan
sembarang barisan $t_n\to t$ menurut sisi pendekatannya seperti pada latihan
sebelumnya, kita memperoleh $\|U_{t_n}-U_t\|\to0$. Jadi $t\mapsto U_t$
kontinu sebagai pemetaan ke $\linop$.

> **Catatan pelengkapan hilir.** Solusi sumber hanya menulis kenaikan khusus
> $h_n\downarrow0$ dan memakai {eq}`sgbound` tanpa menyatakan mengapa batas itu
> tersedia. Implikasi {eq}`czsg3` $\Rightarrow$ {eq}`czsg2`, kedua limit satu
> sisi, dan reduksi barisan umum dinyatakan secara eksplisit di atas.
```
