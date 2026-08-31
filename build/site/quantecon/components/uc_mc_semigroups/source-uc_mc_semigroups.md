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
title: "Semigrup Markov yang Kontinu Seragam"
lang: id-ID
course_id: o009
unit_id: unit.o009.quantecon.ctmc.uniformly-continuous-markov-semigroups
source_commit: 8b06e0aa5a438692445b2c896f9d238c5a7d5eb7
source_path: lectures/uc_mc_semigroups.md
source_license: CC BY-SA 4.0
target_license: "CC BY-SA 4.0 untuk adaptasi QuantEcon ini"
model_provenance: "OpenAI Codex gpt-5.6-sol, Ultra."
non_endorsement: "Edisi independen; tidak didukung atau disahkan oleh QuantEcon maupun penulis sumber."
---

# Semigrup Markov yang Kontinu Seragam

## Gambaran umum

Dalam kuliah sebelumnya kita membahas sebagian teori umum semigrup operator.

Selanjutnya, kita menerjemahkan hasil-hasil tersebut ke dalam latar semigrup
Markov.

Semigrup Markov di sini didefinisikan pada himpunan terhitung $S$.

Tujuan utama kita adalah memberikan korespondensi satu-ke-satu yang tepat
antara

* semigrup Markov UC,
* matriks intensitas “konservatif”, dan
* dekomposisi rantai lompatan kanonik dengan intensitas lompatan yang
  bergantung pada keadaan.

Sifat konservatif didefinisikan di bawah dan berkaitan dengan sifat “tidak
meledak” dari rantai Markov yang bersesuaian.

Kita juga akan membahas secara singkat matriks intensitas yang tidak memiliki
sifat ini, beserta proses yang dibangkitkannya.

## Notasi dan Terminologi

Misalkan $S$ suatu himpunan terhitung sembarang.

Sepanjang kuliah ini, $\RR_+=[0,\infty)$.

Misalkan $\ell_1$ ruang Banach yang terdiri atas **fungsi yang dapat
dijumlahkan secara mutlak** pada $S$; yakni, semua
$g \, \colon S \to \RR$ yang memenuhi

$$
    \| g \| := \sum_x |g(x)| < \infty.
$$

Perhatikan bahwa $\dD$, himpunan semua distribusi pada $S$, termuat dalam
$\ell_1$.

Setiap matriks Markov $P$ pada $S$ dapat dan akan kita identifikasi dengan
operator linear $f \mapsto fP$ pada $\ell_1$ melalui

$$
    (fP)(y) = \sum_x f(x) P(x, y)
    \qquad (f \in \ell_1, \; y \in S).
$$ (mmismo)

Agar konsisten dengan notasi sebelumnya, kita menuliskan argumen $P$ di
sebelah kiri dan menerapkan $P$ kepadanya seolah-olah kita mengalikan matriks
$P$ dari kiri dengan vektor baris.

Dalam latihan, Anda diminta memverifikasi bahwa {eq}`mmismo` mendefinisikan
operator linear terbatas pada $\ell_1$ sedemikian sehingga

$$
    \|P\| = 1 \text{ dan } \phi P \in \dD \text{ setiap kali } \phi \in \dD.
$$ (propp)

Perhatikan bahwa komposisi $P$ dengan dirinya sendiri setara dengan
pangkat-pangkat matriks di bawah perkalian matriks.

Untuk matriks intensitas $Q$ pada $S$, kita dapat mencoba memperkenalkan
operator yang bersesuaian secara analog melalui

$$
    (fQ)(y) = \sum_x f(x) Q(x, y)
    \qquad (f \in \ell_1, \; y \in S).
$$ (imislo)

Namun, jumlah dalam {eq}`imislo` tidak selalu terdefinisi dengan baik.[^fnim]

[^fnim]: Sebelumnya, kita memperkenalkan pengertian matriks intensitas ketika
  $S$ berhingga, dan definisinya pada dasarnya tidak berubah dalam latar
  sekarang. Secara khusus, $Q \colon S \times S \to \RR$ disebut **matriks
  intensitas** jika jumlah setiap baris $Q$ sama dengan nol dan $Q(x,y)\geq0$
  setiap kali $x\neq y$.

Kita mengatakan bahwa matriks intensitas $Q$ bersifat **konservatif** jika
jumlah dalam {eq}`imislo` terdefinisi dengan baik untuk setiap $y$ dan, selain
itu, pemetaan $f\mapsto fQ$ dalam {eq}`imislo` merupakan operator linear
terbatas pada $\ell_1$.

Di bawah ini kita menunjukkan cara memeriksa sifat tersebut dalam penerapan.

> **Catatan terminologi hilir.** Dalam kuliah ini, “konservatif” adalah istilah
> lokal untuk syarat operator-terbatas di atas. Dalam sebagian literatur
> rantai Markov, “matriks-$Q$ konservatif” hanya berarti bahwa setiap jumlah
> barisnya nol. Definisi sumber yang lebih kuat dipertahankan di sini agar
> semua pernyataan berikut dibaca dengan ruang lingkup yang tepat.

## Semigrup Markov UC dan Generatornya

Misalkan $Q$ suatu matriks intensitas konservatif pada $S$.

Karena $Q$ berada dalam $\linopell$, eksponensial operator $e^{tQ}$
terdefinisi dengan baik sebagai unsur $\linopell$ untuk setiap $t\geq0$.

Selain itu, berdasarkan {prf:ref}`ecuc`, keluarga $(P_t)$ dalam
$\lL(\ell_1)$ yang didefinisikan oleh $P_t=e^{tQ}$ membentuk semigrup Markov
UC pada $\ell_1$.

(Di sini, semigrup Markov $(P_t)$ merupakan sekaligus kumpulan matriks Markov
dan kumpulan operator, seperti dalam {eq}`mmismo`.)

Teorema berikut menyatakan bahwa semigrup Markov UC hanya dapat muncul dengan
cara ini.

```{prf:theorem}
:label: usmg

Jika $(P_t)$ merupakan semigrup Markov UC pada $\ell_1$, terdapat matriks
intensitas konservatif $Q$ sedemikian sehingga $P_t=e^{tQ}$ untuk setiap
$t\geq0$.

```

```{prf:proof}
Misalkan $(P_t)$ suatu semigrup Markov UC pada $\ell_1$.

Karena $(P_t)$ merupakan semigrup UC pada $\ell_1$, dari
{prf:ref}`ucsgec` terdapat $Q\in\lL(\ell_1)$ sedemikian sehingga
$P_t=e^{tQ}$ untuk setiap $t\geq0$.

Kita hanya perlu menunjukkan bahwa $Q$ merupakan matriks intensitas
konservatif.

Karena $(P_t)$ adalah semigrup Markov, $P_t$ merupakan matriks Markov untuk
setiap $t$. Karena $P_t=e^{tQ}$ untuk setiap $t$, dapat disimpulkan bahwa $Q$
merupakan matriks intensitas.

Kita telah membuktikan hal ini untuk kasus $|S|<\infty$ dalam
{prf:ref}`intvsmk`, dan argumen yang sama tetap berlaku ketika
$|S|=\infty$.

Karena $Q\in\lL(\ell_1)$, kita mengetahui bahwa $Q$ merupakan operator
terbatas. Jadi, $Q$ adalah matriks intensitas konservatif.

> **Catatan pelengkapan hilir.** Pada ruang keadaan terhitung, langkah yang
> diringkas di atas dapat dibaca dalam norma $\ell_1$: untuk vektor massa
> satuan $\delta_x$, konvergensi
> $(\delta_xP_h-\delta_x)/h\to\delta_xQ$ memberi
> $Q(x,y)\geq0$ bagi $y\neq x$. Karena konvergensi berlangsung dalam
> $\ell_1$, penjumlahan koordinat boleh dilewatkan melalui limit, sehingga
> $\sum_yQ(x,y)=0$. Ekspansi terhadap basis Schauder $(\delta_x)$ dari
> $\ell_1$ kemudian memberikan representasi matriks {eq}`imislo` untuk setiap
> $f\in\ell_1$. Ini menutup dua syarat matriks intensitas tanpa mengandalkan
> pertukaran jumlah tak berhingga yang tidak dibenarkan.
```

Dari {prf:ref}`usmg` kita dapat segera menyimpulkan bahwa

* $P_t$ terdiferensialkan pada setiap $t\geq0$,
* $Q$ adalah generator dari $(P_t)$,
* $P_t'=QP_t=P_tQ$ untuk setiap $t\geq0$, dan
* $P_0'=Q$, dengan turunan kanan di $t=0$.

Sesungguhnya, hasil-hasil ini hanyalah kasus khusus dari klaim-klaim dalam
{prf:ref}`ucsgec`.

Butir kedua dari belakang merupakan persamaan Kolmogorov maju dan mundur.

Butir terakhir menunjukkan bahwa kita dapat memperoleh matriks intensitas
$Q$ dengan mengambil turunan kanan $P_t$ pada $t=0$.

```{prf:example}
:label: uc-mc-semigroups-prf-1
Mari kita tinjau kembali proses Poisson $(N_t)$ pada $S=\ZZ_+$ dengan laju
$\lambda>0$ dalam kaitannya dengan pembahasan di atas.

Semigrup $(P_t)$ yang bersesuaian bersifat UC. Karena itu, terdapat matriks
intensitas konservatif $Q$ yang memenuhi $P_t=e^{tQ}$ untuk setiap $t\geq0$.

Fakta ini dapat ditetapkan dengan membuktikan sifat UC, lalu menerapkan
{prf:ref}`usmg`.

Alternatif lain, yang lebih mudah dalam kasus ini, adalah memberikan matriks
intensitas $Q$ secara langsung, lalu memverifikasi bahwa $P_t=e^{tQ}$.

Semigrup untuk proses Poisson dengan laju $\lambda$ diberikan dalam
{eq}`poissemi` dan dituliskan kembali di sini:

$$
    P_t(j, k)
    =
    \begin{cases}
    e^{-\lambda t} \frac{ (\lambda t)^{k-j} }{(k-j)!}
        & \text{ jika } j \leq k
        \\
    0 & \text{ selainnya}.
    \end{cases}
$$ (poissemi2)

Untuk matriks intensitasnya, kita ambil

$$
    Q :=
    \begin{pmatrix}
    -\lambda & \lambda & 0 & 0 & 0 & \cdots
    \\
    0 & -\lambda & \lambda & 0 & 0 & \cdots
    \\
    0 & 0 & -\lambda & \lambda & 0 & \cdots
    \\
    0 & 0 & 0 & -\lambda & \lambda & \cdots
    \\
    \vdots & \vdots  & \vdots  & \vdots  & \vdots
    \end{pmatrix}.
$$ (poissonq)

Bentuk $Q$ bersifat intuitif: massa probabilitas mengalir keluar dari keadaan
$i$ dan masuk ke keadaan $i+1$ dengan laju $\lambda$.

Jelas bahwa $Q$ merupakan matriks intensitas, seperti diklaim.

Latihan meminta Anda memastikan bahwa $Q$ berada dalam $\lL(\ell_1)$.

Untuk membuktikan bahwa $P_t=e^{tQ}$ bagi sembarang $t\geq0$, mula-mula kita
uraikan $Q$ sebagai $Q=\lambda(K-I)$, dengan $K$ didefinisikan oleh

$$
    K(i, j) = \mathbb 1\{j = i + 1\}.
$$

Untuk $t\geq0$ yang diberikan, kita kemudian memperoleh

$$
    e^{tQ}
    = e^{\lambda t (K-I)}
    = e^{-\lambda t} e^{\lambda t K}
    = e^{-\lambda t}
    \sum_{m \geq 0} \frac{(\lambda t K)^m}{m!}.
$$

Latihan meminta Anda memverifikasi bahwa pangkat-pangkat $K$ memenuhi
$K^m(i,j)=\mathbb 1\{j=i+m\}$.

Memasukkan bentuk $K^m$ ini menghasilkan

$$
    e^{tQ}(i, j)
    = e^{-\lambda t}
    \sum_{m \geq 0} \frac{(\lambda t )^m}{m!} \mathbb 1\{j = i + m\}
    = e^{-\lambda t}
    \sum_{m \geq 0} \frac{(\lambda t )^m}{m!} \mathbb 1\{m = j-i\}.
$$

Ini identik dengan {eq}`poissemi2`.

Sekarang dapat disimpulkan bahwa $t\mapsto P_t\in\lL(\ell_1)$
terdiferensialkan pada setiap $t\geq0$ dan $Q$ merupakan generator dari
$(P_t)$, dengan turunan kanan $P_0'=Q$.

```

### Syarat Perlu dan Cukup

Definisi kita tentang matriks intensitas konservatif sesuai untuk teori di
atas, tetapi mungkin sulit diperiksa dalam penerapan dan kurang memberikan
intuisi probabilistik.

Untungnya, kita memiliki karakterisasi sederhana berikut.

```{prf:lemma}
:label: scintcon

Matriks intensitas $Q$ pada $S$ bersifat konservatif jika dan hanya jika
$\sup_x|Q(x,x)|$ berhingga.

```

Pembuktiannya merupakan latihan yang telah dilengkapi solusi.

```{prf:example}
:label: jccs

Ingat kembali latar rantai lompatan. Dengan mengulangi {eq}`kolbackeq`, kita
mendefinisikan $Q$ melalui

$$
    Q(x, y) := \lambda(x) (K(x, y) - I(x, y)).
$$ (kolbackeq_inf)

Fungsi $\lambda\colon S\to\RR_+$ memberikan laju lompatan pada setiap
keadaan, sedangkan $K$ merupakan matriks Markov bagi rantai lompatan waktu
diskret yang tertanam.

Sebelumnya kita membahas latar ini ketika $S$ berhingga, tetapi perhatian kita
tidak perlu dibatasi pada kasus tersebut.

Untuk $S$ terhitung yang umum, matriks $Q$ yang didefinisikan dalam
{eq}`kolbackeq_inf` tetap merupakan matriks intensitas.

Jika kita tetap mengasumsikan $K(x,x)=0$ untuk setiap $x$, maka
$Q(x,x)=-\lambda(x)$.

Karena itu, $Q$ bersifat konservatif jika dan hanya jika
$\sup_x\lambda(x)$ berhingga.

Dengan kata lain, $Q$ bersifat konservatif jika himpunan laju lompatannya
terbatas.
```

Sumber menyimpulkan dari contoh ini bahwa syarat konservatif pada $Q$
merupakan pembatasan yang relatif ringan.

> **Catatan kualifikasi hilir.** Syarat tersebut memang mudah diperiksa dan
> memberikan syarat cukup yang kuat untuk tidak terjadinya ledakan. Namun,
> keterbatasan seragam semua laju bukan syarat perlu bagi sifat tidak meledak
> dan dapat mengecualikan model kelahiran atau antrean yang penting.

### Kasus Ruang Keadaan Berhingga

Dari {prf:ref}`scintcon`, langsung terlihat bahwa setiap matriks intensitas
bersifat konservatif ketika ruang keadaan $S$ berhingga.

Karena itu, dalam latar ini setiap matriks intensitas $Q$ pada $S$
mendefinisikan semigrup Markov UC $(P_t)$ melalui $P_t=e^{tQ}$.

Sebaliknya, jika $S$ berhingga, setiap semigrup Markov $(P_t)$ merupakan
semigrup Markov UC.

Untuk melihatnya, ingat bahwa sebagai semigrup Markov, $(P_t)$ memenuhi
$\lim_{t\to0}P_t(x,y)=I(x,y)$ untuk setiap $x,y$ dalam $S$.

Dalam ruang berdimensi berhingga, konvergensi titik demi titik menyiratkan
konvergensi norma. Jadi, $P_t\to I$ dalam norma operator ketika $t\to0$ dari
kanan.

Seperti yang telah kita lihat, ini cukup untuk memastikan bahwa pemetaan
$t\mapsto P_t$ kontinu dalam norma di seluruh $\RR_+$.

Dengan demikian, $(P_t)$ merupakan semigrup Markov UC.

Dengan menggabungkan hasil-hasil tersebut dengan {prf:ref}`usmg`, kita
menyimpulkan bahwa ketika $S$ berhingga, terdapat korespondensi satu-ke-satu
antara semigrup Markov dan matriks intensitas.

## Dari Matriks Intensitas ke Rantai Lompatan

Kini kita memahami bahwa terdapat pasangan satu-ke-satu antara matriks
intensitas konservatif dan semigrup Markov UC.

Gagasan-gagasan ini penting dari sudut pandang analitis.

Sekarang kita memberikan sudut pandang lain yang lebih erat terkait dengan
probabilitas.

Sudut pandang ini penting bagi teori maupun komputasi.

### Pasangan Rantai Lompatan

Mari kita sepakati bahwa $(\lambda,K)$ disebut **pasangan rantai lompatan**
jika $\lambda$ merupakan pemetaan dari $S$ ke $\RR_+$ dan $K$ merupakan
matriks Markov pada $S$.

Mudah diverifikasi bahwa matriks $Q$ pada $S$ yang didefinisikan oleh

$$
    Q(x, y) := \lambda(x) (K(x, y) - I(x, y))
$$ (jcinmat)

merupakan matriks intensitas.

(Dalam {doc}`kuliah sebelumnya <kolmogorov_bwd>`, kita melihat bahwa $Q$
merupakan matriks intensitas bagi rantai lompatan $(X_t)$ yang dibangun melalui
{prf:ref}`ejc_algo` dari pasangan rantai lompatan $(\lambda,K)$.)

Seperti yang akan kita tunjukkan, setiap matriks intensitas memiliki uraian
dalam {eq}`jcinmat` untuk suatu pasangan rantai lompatan.

### Dekomposisi Rantai Lompatan

Untuk matriks intensitas $Q$ yang diberikan, tetapkan

$$
    \lambda(x) := -Q(x, x)
    \qquad (x \in S).
$$ (lambdafromq)

Selanjutnya, kita membangun $K$, mula-mula pada diagonal utama melalui

$$
    K(x,x) =
    \begin{cases}
        0 & \text{ jika } \lambda(x) > 0
        \\
        1 & \text{ selainnya}.
    \end{cases}
$$ (kfromqxx)

Jadi, jika laju meninggalkan $x$ positif, kita menetapkan $K(x,x)=0$ agar
rantai lompatan tertanam berpindah dari $x$ dengan probabilitas satu ketika
lompatan berikutnya terjadi.

Sebaliknya, ketika $Q(x,x)=0$, kita menetap di $x$ selamanya. Jadi, $x$
merupakan **keadaan penyerap**.

Di luar diagonal utama, yakni ketika $x\neq y$, kita tetapkan

$$
    K(x,y) =
    \begin{cases}
        \frac{Q(x,y)}{\lambda(x)} & \text{ jika } \lambda(x) > 0
        \\
        0 & \text{ selainnya}.
    \end{cases}
$$ (kfromqxy)

Latihan di bawah meminta Anda memastikan bahwa untuk $\lambda$ dan $K$ yang
baru didefinisikan,

1. $(\lambda,K)$ merupakan pasangan rantai lompatan; dan
1. matriks intensitas $Q$ memenuhi {eq}`jcinmat`.

Kita menyebut $(\lambda,K)$ sebagai **dekomposisi rantai lompatan** dari $Q$.

Kita merangkumnya dalam sebuah lema.

```{prf:lemma}
:label: imatjc

Suatu matriks $Q$ pada $S$ merupakan matriks intensitas jika dan hanya jika
terdapat pasangan rantai lompatan $(\lambda,K)$ sedemikian sehingga
{eq}`jcinmat` berlaku.
```

### Kasus Konservatif

Dari {prf:ref}`jccs`, kita mengetahui bahwa matriks intensitas $Q$ bersifat
konservatif jika dan hanya jika $\lambda$ terbatas.

Selain itu, dalam {prf:ref}`usmg` kita melihat bahwa pasangan antara matriks
intensitas konservatif dan semigrup Markov UC bersifat satu-ke-satu.

Hal ini menghasilkan pernyataan berikut.

```{prf:theorem}
Pada $S$, terdapat korespondensi satu-ke-satu antara himpunan-himpunan objek
berikut:

1. Himpunan semua dekomposisi rantai lompatan kanonik $(\lambda,K)$ dengan
   $\lambda$ terbatas, $K(x,x)=0$ jika $\lambda(x)>0$, dan $K(x,x)=1$ jika
   $\lambda(x)=0$.
1. Himpunan semua matriks intensitas konservatif.
1. Himpunan semua semigrup Markov UC.

```

> **Catatan koreksi hilir.** Sumber menyatakan butir pertama untuk semua
> pasangan rantai lompatan dengan $\lambda$ terbatas. Tanpa konvensi kanonik
> di atas, pemetaan $(\lambda,K)\mapsto Q$ tidak injektif: transisi-diri dapat
> dipindahkan antara laju $\lambda$ dan diagonal $K$ tanpa mengubah $Q$.
> Pembatasan pada dekomposisi yang baru didefinisikan memulihkan korespondensi
> satu-ke-satu yang dimaksud.

### Simulasi

Berdasarkan pembahasan sebelumnya, kita memiliki cara sederhana untuk
menyimulasikan rantai Markov dari sembarang matriks intensitas konservatif
$Q$.

Langkah-langkahnya adalah

1. Uraikan $Q$ menjadi pasangan rantai lompatan $(\lambda,K)$.
2. Lakukan simulasi melalui {prf:ref}`ejc_algo`.

Dengan mengingat pembahasan persamaan Kolmogorov mundur, kita mengetahui bahwa
prosedur ini menghasilkan rantai Markov dengan semigrup Markov $(P_t)$ yang
memenuhi $P_t=e^{tQ}$ untuk $Q$ dalam {eq}`jcinmat`.

(Walaupun argumen kita mengasumsikan $S$ berhingga, pembuktiannya tetap berlaku
ketika $S$ terhitung tak berhingga dan $Q$ konservatif, dengan perubahan yang
sangat kecil.)

Secara khusus, $(X_t)$ merupakan rantai Markov waktu kontinu dengan matriks
intensitas $Q$.

## Melampaui Matriks Intensitas Terbatas

Jika dalam suatu penerapan kita menjumpai matriks intensitas $Q$ yang tidak
konservatif, apa yang dapat kita harapkan?

Dalam keadaan ini, setidaknya kita dapat berharap bahwa $Q$ mempunyai suatu
realisasi operator—dengan domain rapat yang dinyatakan—yang merupakan generator
semigrup $C_0$.

Jika semigrup yang dibangkitkan juga positif, mempertahankan massa, dan
memenuhi syarat Markov yang sesuai, semigrup tersebut merupakan semigrup
Markov.

> **Catatan koreksi hilir.** Sumber menyatakan bahwa karena $Q$ merupakan
> matriks intensitas, semigrup yang dibangkitkannya pasti merupakan semigrup
> Markov. Untuk operator tak terbatas, bentuk matriks intensitas saja belum
> menjamin sifat generator, kepositifan, ketunggalan, ataupun konservasi massa.
> Syarat-syarat tambahan tersebut diperlukan, terutama ketika ledakan mungkin
> terjadi.

Realisasi minimal dari suatu matriks $Q$ dapat hanya menghasilkan semigrup
sub-Markov: massa totalnya berkurang ketika proses meledak. Bahkan jika suatu
perluasan konservatif ada, ketunggalannya perlu dibuktikan. Keterbatasan
seragam laju lompatan menjamin tidak terjadinya ledakan, tetapi bukan syarat
perlu. Sebagai contoh, proses kelahiran murni dengan laju
$\lambda_n=n+1$ memiliki laju tak terbatas tetapi tidak meledak, sedangkan
$\lambda_n=(n+1)^2$ menghasilkan ledakan.

Untuk mengetahui kapan $Q$ menjadi generator semigrup $C_0$, kita perlu
merujuk pada [Teorema
Hille–Yosida](https://en.wikipedia.org/wiki/Hille%E2%80%93Yosida_theorem) dan
syarat-syarat cukup yang diturunkan darinya.

Walaupun kita tidak membahas rinciannya, patut dicatat bahwa persoalan ini
berkaitan dengan ledakan.

Untuk melihat hubungannya, ingat bahwa sebagian masalah nilai awal tidak
menghasilkan solusi sah yang terdefinisi untuk setiap $t\in\RR_+$.

Salah satu contohnya adalah masalah skalar $x'_t=1+x_t^2$, yang memiliki solusi
$x_t=\tan(t-c)$ untuk suatu konstanta $c$ pada selang keberadaan maksimalnya.

Solusi tersebut menuju $+\infty$ ketika $t\uparrow c+\pi/2$ dan tidak dapat
dilanjutkan sebagai solusi bernilai riil melewati waktu itu.

Masalahnya ialah lintasan waktu meledak menuju tak berhingga dalam waktu
berhingga.

Persoalan yang sama dapat terjadi pada proses Markov jika laju lompatannya
tumbuh cukup cepat.

Untuk pembahasan lebih lanjut, lihat, misalnya, Bagian 2.7 dari
{cite}`norris1998markov`.

> **Catatan koreksi hilir.** Sumber menyatakan bahwa $\tan(t-c)$ “sama dengan
> $+\infty$” untuk semua $t\geq c+\pi/2$. Formulasi di atas menyatakan fakta
> yang tepat: solusi klasik mencapai batas waktu berhingga dan tidak
> terdefinisi di titik ledakan.

## Latihan

```{exercise}
:label: uc-mc-semigroups-ex-1

Misalkan $P$ suatu matriks Markov pada $S$ dan identifikasikan $P$ dengan
operator linear dalam {eq}`mmismo`. Verifikasi klaim-klaim dalam
{eq}`propp`.
```

```{solution} uc-mc-semigroups-ex-1
:class: dropdown

Untuk menentukan norma $P$, kita menggunakan definisi dalam {eq}`norml`.

Untuk setiap $f\in\ell_1$, jumlah dalam {eq}`mmismo` terkonvergensi secara
mutlak sebagai unsur $\ell_1$, sebab

$$
\sum_y\sum_x |f(x)|P(x,y)=\sum_x|f(x)|<\infty.
$$

Identitas ini juga membenarkan pertukaran urutan jumlah di bawah, sedangkan
linearitas mengikuti langsung dari linearitas setiap jumlah koordinat.

Jika $f\in\ell_1$ dan $\|f\|\leq1$, maka

$$
\| f P \|
\leq \sum_y \sum_x |f(x)| P(x, y)
= \sum_x |f(x)| \sum_y P(x, y)
= \sum_x |f(x)|
= \| f \|.
$$

Jadi, $\|P\|\leq1$.

Untuk melihat bahwa kesamaan berlaku, kita dapat mengulangi argumen ini dengan
$f\geq0$ dan $\|f\|=1$, sehingga diperoleh $\|fP\|=\|f\|=1$.

Sekarang, pilih sembarang $\phi\in\dD$.

Jelas bahwa $\phi P\geq0$, dan

$$
\sum_y (\phi P)(y)
=\sum_y \sum_x \phi (x) P(x, y)
=\sum_x \phi (x) \sum_y P(x, y)
= 1.
$$

Jadi, $\phi P\in\dD$, seperti diklaim.
```

```{exercise}
:label: uc-mc-semigroups-ex-2

Buktikan klaim dalam {prf:ref}`scintcon`.
```

```{solution} uc-mc-semigroups-ex-2
:class: dropdown

Berikut salah satu solusinya.

Misalkan $Q$ suatu matriks intensitas pada $S$.

Pertama, anggap bahwa $m:=\sup_x|Q(x,x)|$ berhingga.

Jika $m=0$, sifat jumlah baris nol dan ketaknegatifan unsur luar diagonal
memaksa $Q=0$. Maka $Q$ jelas merupakan operator terbatas.

Sekarang anggap $m>0$ dan tetapkan $\hat P:=I+Q/m$.

Tidak sulit untuk memeriksa bahwa $\hat P$ merupakan matriks Markov dan
$Q=m(\hat P-I)$.

Karena $\hat P$ merupakan matriks Markov, ia menginduksi operator linear
terbatas pada $\ell_1$ melalui {eq}`mmismo`.

Karena $\lL(\ell_1)$ merupakan ruang linear, $Q$ juga berada dalam
$\lL(\ell_1)$.

Secara khusus, $Q$ merupakan operator terbatas dan karena itu bersifat
konservatif.

Sebaliknya, anggap bahwa $Q$ konservatif tetapi
$\sup_x|Q(x,x)|$ tak berhingga.

Pilih $x\in S$ sedemikian sehingga $|Q(x,x)|>\|Q\|$.

Definisikan $f\in\ell_1$ dengan $f(z)=\mathbb 1\{z=x\}$.

Karena $\|f\|=1$, kita memperoleh

$$
\| Q \|
\geq \| f Q \|
= \sum_y \left| \sum_z f(z) Q(z, y) \right|
= \sum_y | Q(x, y) |
\geq | Q(x, x) |,
$$

yang merupakan kontradiksi.

> **Catatan koreksi hilir.** Solusi sumber langsung membagi dengan
> $m=\sup_x|Q(x,x)|$ tanpa menangani kemungkinan $m=0$. Kasus nol dipisahkan
> di atas agar definisi $\hat P=I+Q/m$ sah.
```

```{exercise}
:label: uc-mc-semigroups-ex-3

Pastikan bahwa $Q$ yang didefinisikan dalam {eq}`poissonq` menginduksi
operator linear terbatas pada $\ell_1$ melalui {eq}`imislo`.
```

```{solution} uc-mc-semigroups-ex-3
:class: dropdown

Linearitasnya langsung terlihat, sehingga kita berfokus pada keterbatasan.

Untuk sembarang $f\in\ell_1$ dan pilihan $Q$ ini, dengan konvensi
$f(-1)=0$, berlaku

$$
    (fQ)(y)=\lambda\bigl(f(y-1)-f(y)\bigr)
    \qquad (y\in\ZZ_+).
$$

Oleh karena itu, ketaksamaan segitiga memberi

$$
\begin{aligned}
\|fQ\|
&=\lambda\sum_{y\geq0}|f(y-1)-f(y)| \\
&\leq\lambda\sum_{y\geq0}|f(y-1)|
   +\lambda\sum_{y\geq0}|f(y)| \\
&=2\lambda\|f\|.
\end{aligned}
$$

Jadi, $\|fQ\|\leq2\lambda\|f\|$, yang menyiratkan
$Q\in\lL(\ell_1)$ sebagaimana diperlukan.

> **Catatan koreksi hilir.** Solusi sumber menuliskan jumlah ganda yang tidak
> sesuai indeks dan akan tak berhingga. Identitas koordinat yang tepat bagi
> $fQ$ serta estimasi norma yang dimaksud dinyatakan secara eksplisit di atas.
```

```{exercise}
:label: uc-mc-semigroups-ex-4

Misalkan $K$ didefinisikan pada $\ZZ_+\times\ZZ_+$ oleh
$K(i,j)=\mathbb 1\{j=i+1\}$.

Tunjukkan bahwa, dengan $K^m$ menyatakan hasil kali matriks ke-$m$ dari $K$
dengan dirinya sendiri, berlaku
$K^m(i,j)=\mathbb 1\{j=i+m\}$ bagi setiap $i,j\in\ZZ_+$.
```

```{solution} uc-mc-semigroups-ex-4
:class: dropdown

Untuk $m=0$, $K^0=I$, sehingga
$K^0(i,j)=\mathbb 1\{j=i\}$.

Sekarang, anggap bahwa pernyataan tersebut berlaku pada suatu $m\geq0$.

Berdasarkan definisi komposisi atau perkalian matriks, kita memperoleh

$$
    K^{m+1}(i, j)
    = \sum_n K^m(i, n) K(n, j)
    = \sum_n \mathbb 1\{n=i+m\}\mathbb 1\{j=n+1\}
    = \mathbb 1\{j=i+m+1\}.
$$

Ini menyelesaikan langkah induksi dan mencakup setiap $m\in\ZZ_+$.

> **Catatan pelengkapan hilir.** Solusi sumber mulai dari $m=1$ dan menulis
> $K(i,j-m)$, yang berada di luar ruang keadaan ketika $j<m$. Pembuktian di
> atas menyertakan $m=0$ dan menghindari evaluasi indeks negatif.
```

```{exercise}
:label: uc-mc-semigroups-ex-5

Misalkan $Q$ sembarang matriks intensitas pada $S$.

Buktikan bahwa dekomposisi rantai lompatan dari $Q$ benar-benar merupakan
pasangan rantai lompatan.

Buktikan pula bahwa dekomposisi $(\lambda,K)$ ini memenuhi {eq}`jcinmat`.
```

```{solution} uc-mc-semigroups-ex-5
:class: dropdown

Misalkan $Q$ suatu matriks intensitas dan $(\lambda,K)$ dekomposisi rantai
lompatan dari $Q$.

Ketaknegatifan $\lambda$ langsung mengikuti definisi matriks intensitas.

Untuk melihat bahwa $K$ merupakan matriks Markov, tetapkan $x\in S$ dan
pertama-tama anggap $\lambda(x)>0$. Maka

$$
\sum_y K(x, y)
= \sum_{y \neq x} K(x,y)
= \sum_{y \neq x} \frac{Q(x,y)}{\lambda(x)}
= \frac{-Q(x,x)}{\lambda(x)}
= 1.
$$

Jika $\lambda(x)=0$, maka $Q(x,x)=0$. Karena unsur luar diagonal tak negatif
dan jumlah baris $Q$ sama dengan nol, $Q(x,y)=0$ bagi setiap $y\neq x$.
Definisi {eq}`kfromqxx`–{eq}`kfromqxy` kemudian memberi $K(x,x)=1$ dan
$K(x,y)=0$ bagi $y\neq x$, sehingga sekali lagi $\sum_yK(x,y)=1$.

Karena $K$ tak negatif, $K$ merupakan matriks Markov. Jadi,
$(\lambda,K)$ merupakan pasangan rantai lompatan yang sah.

Terakhir, kita verifikasi {eq}`jcinmat`. Jika $\lambda(x)>0$ dan $y\neq x$,
maka $\lambda(x)K(x,y)=Q(x,y)$; sedangkan untuk $y=x$,

$$
\lambda(x)(K(x,x)-1)=-\lambda(x)=Q(x,x).
$$

Jika $\lambda(x)=0$, kedua ruas {eq}`jcinmat` bernilai nol bagi $y=x$ maupun
$y\neq x$, berdasarkan pengamatan pada paragraf sebelumnya. Jadi,
{eq}`jcinmat` berlaku untuk semua $x,y\in S$.

> **Catatan pelengkapan hilir.** Solusi sumber menyebut verifikasi terakhir
> “mekanis” lalu menghilangkan rinciannya. Pemisahan kasus lengkap diberikan
> di atas agar pasangan latihan–solusi tetap memadai untuk belajar mandiri.

```
