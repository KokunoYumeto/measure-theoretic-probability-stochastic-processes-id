---
title: "Keterukuran proses dan hukum lintasan"
lang: id-ID
author:
  - "Codex (penulisan materi asli atas arahan pengguna)"
authoring:
  course_id: "o009"
  unit_id: "unit.o009.original.bridge.process-measurability-path-law"
  target_locale: "id-ID"
  source_type: "original"
  rights_id: "rights.o009.original.bridge.process-measurability-path-law.cc-by-4.0"
  license: "CC-BY-4.0"
  model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."
---

::: {#unit.o009.original.bridge.process-measurability-path-law .original-bridge}

# Keterukuran proses dan hukum lintasan

::: {#tujuan-dan-empat-lapis-objek .bridge-section}

## Tujuan dan empat lapis objek

Sebuah proses stokastik mempunyai koordinat waktu, tetapi kata "terukur"
dapat merujuk pada beberapa peta yang berbeda. Jika peta-peta itu disamakan,
argumen yang benar tentang distribusi berdimensi hingga dapat berubah menjadi
klaim yang salah tentang lintasan. Unit [Konstruksi Kolmogorov dan proses
kanonik](01-konstruksi-kolmogorov.html) telah membangun hukum pada ruang
produk mentah. Sekarang kita menentukan dengan tepat informasi apa yang
tersimpan dalam hukum itu dan apa yang masih memerlukan struktur tambahan.

Biarkan $(T,\mathcal T)$ menjadi ruang indeks terukur,
$(\Omega,\mathcal A,\mathbb P)$ ruang peluang, dan $(S,\mathcal S)$ ruang
keadaan terukur. Untuk keluarga $X=(X_t)_{t\in T}$, empat objek berikut harus
dibedakan.

1. Untuk setiap $t$ tetap, ada **peta koordinat**
   $$
   X_t:\Omega\longrightarrow S.
   $$
2. Seluruh keluarga dapat dikemas sebagai **peta lintasan mentah**
   $$
   \Phi_X:\Omega\longrightarrow S^T,
   \qquad \Phi_X(\omega)(t)=X_t(\omega),
   $$
   dengan sasaran diberi sigma-aljabar produk
   $\mathcal S^{\otimes T}=\sigma(\pi_t:t\in T)$.
3. Indeks dan hasil acak dapat dibaca bersama melalui **peta evaluasi proses**
   $$
   \widehat X:T\times\Omega\longrightarrow S,
   \qquad \widehat X(t,\omega)=X_t(\omega).
   $$
4. Jika lintasan mempunyai keteraturan tertentu, peta yang sama mungkin
   dipandang sebagai peubah acak bernilai ruang lintasan, misalnya
   $$
   \Phi_X:\Omega\longrightarrow C([0,1],\mathbb R)
   $$
   dengan sigma-aljabar Borel dari norma seragam.

Keempat pernyataan keterukuran itu tidak identik. Setelah menyelesaikan unit
ini, pembaca mampu membuktikan hubungan yang benar di antaranya, menentukan
tepat apa yang ditentukan oleh distribusi berdimensi hingga, dan mengaudit
klaim tentang modifikasi, ketakterbedaan, serta keteraturan lintasan.

Prasyaratnya ialah [ruang produk peluang](../prob/Probability2.html),
[proses dan distribusi berdimensi hingga](../prob/Processes.html), dan
jembatan Kolmogorov di atas. Kita tidak mengulang konstruksi ukuran dari
keluarga proyektif, teori gerak Brown, atau teori rantai Markov waktu kontinu.
Fokus kita adalah perbedaan logis antara koordinat, peta lintasan, evaluasi
gabungan, dan hukum pada ruang lintasan teratur.

:::

::: {#peta-lintasan-mentah .bridge-section}

## Peta lintasan mentah dan keterukuran tiap waktu

Definisi dasar proses stokastik hanya meminta setiap $X_t$ terukur sebagai
peta dari $(\Omega,\mathcal A)$ ke $(S,\mathcal S)$. Syarat ini tepat setara
dengan keterukuran peta lintasan mentah ke ruang produk.

> **Proposisi (koordinat demi koordinat).** Peta
> $\Phi_X:\Omega\to(S^T,\mathcal S^{\otimes T})$ terukur jika dan hanya jika
> $X_t:\Omega\to S$ terukur untuk setiap $t\in T$.

**Bukti.** Jika $\Phi_X$ terukur, maka

$$
X_t=\pi_t\circ\Phi_X
$$

terukur karena proyeksi koordinat $\pi_t$ terukur menurut definisi
$\mathcal S^{\otimes T}$. Sebaliknya, anggap setiap $X_t$ terukur. Untuk
himpunan silinder

$$
C=\pi_J^{-1}(B),
\qquad J\subset T\text{ hingga},\quad
B\in\mathcal S^{\otimes J},
$$

prabayangannya adalah

$$
\Phi_X^{-1}(C)
=\{\omega:(X_t(\omega))_{t\in J}\in B\}.
$$

Peta vektor hingga $(X_t)_{t\in J}$ terukur terhadap sigma-aljabar produk
hingga, sehingga prabayangan itu berada dalam $\mathcal A$. Karena silinder
membangkitkan $\mathcal S^{\otimes T}$, kriteria sigma-aljabar pembangkit
memberikan keterukuran $\Phi_X$. $\square$

Tidak ada hipotesis Borel standar pada $S$ dalam proposisi ini. Hipotesis
seperti itu diperlukan pada teorema keberadaan tertentu, bukan pada fakta
formal bahwa sigma-aljabar produk dibangkitkan oleh koordinat.

Proposisi tersebut juga menjelaskan hukum lintasan mentah. Jika setiap
koordinat terukur, kita dapat membentuk ukuran dorong

$$
\mathsf P_X=\mathbb P\circ\Phi_X^{-1}
$$

pada $(S^T,\mathcal S^{\otimes T})$. Ukuran ini membaca setiap kejadian yang
dapat dibangun dari koordinat melalui operasi terhitung. Akan tetapi, sasaran
ini belum mengatakan bahwa peta $(t,\omega)\mapsto X_t(\omega)$ terukur, dan
belum mengatakan bahwa himpunan semua lintasan kontinu atau cadlag merupakan
kejadian terukur.

:::

::: {#keterukuran-bersama .bridge-section}

## Keterukuran bersama dan evaluasi kanonik

Keluarga $X$ disebut **terukur bersama** apabila

$$
\widehat X:(T\times\Omega,\mathcal T\otimes\mathcal A)
\longrightarrow(S,\mathcal S)
$$

terukur. Keterukuran bersama bergantung pada sigma-aljabar $\mathcal T$ yang
dipilih pada $T$; tanpa struktur terukur pada himpunan indeks, pernyataan ini
bahkan belum terdefinisi.

Jika $\widehat X$ terukur, setiap bagian waktu
$\omega\mapsto\widehat X(t,\omega)=X_t(\omega)$ terukur. Untuk $t$ tetap,
peta $\omega\mapsto(t,\omega)$ terukur, lalu komposisinya dengan
$\widehat X$ ialah $X_t$. Demikian pula, untuk setiap $\omega$ tetap, lintasan
$t\mapsto X_t(\omega)$ merupakan peta terukur dari $(T,\mathcal T)$ ke
$(S,\mathcal S)$. Jadi keterukuran bersama lebih kuat daripada keterukuran
tiap waktu dan juga memaksa setiap lintasan menjadi terukur terhadap waktu.

Kebalikannya gagal bahkan pada proses koordinat kanonik yang paling alami.

> **Teorema (evaluasi kanonik mentah tidak terukur bersama).** Ambil
> $T=[0,1]$ dengan sigma-aljabar Borel, $S=\{0,1\}$ dengan sigma-aljabar
> diskret, dan $\Omega=S^T$ dengan sigma-aljabar produk
> $\mathcal S^{\otimes T}$. Peta evaluasi
> $$
> e:T\times S^T\longrightarrow S,
> \qquad e(t,\omega)=\omega(t),
> $$
> tidak terukur terhadap
> $\mathcal B(T)\otimes\mathcal S^{\otimes T}$.

Untuk membuktikannya, kita memerlukan lemma yang mempertahankan satu himpunan
koordinat untuk seluruh nilai $t$.

> **Lemma (ketergantungan koordinat terhitung pada produk).** Untuk setiap
> $E\in\mathcal T\otimes\mathcal S^{\otimes T}$ terdapat himpunan terhitung
> $J\subset T$ sedemikian sehingga, apabila
> $\omega|_J=\omega'|_J$, maka
> $$
> (t,\omega)\in E\iff(t,\omega')\in E
> \qquad\text{untuk setiap }t\in T.
> $$

**Bukti lemma.** Bentuk kelas $\mathcal D$ dari semua bagian
$E\subset T\times S^T$ yang memiliki sifat tersebut untuk suatu $J$
terhitung. Kelas ini merupakan sigma-aljabar. Komplemen memakai $J$ yang
sama. Untuk gabungan terhitung $E_n$, gunakan
$J=\bigcup_nJ_n$, yang masih terhitung.

Setiap persegi panjang terukur $B\times C$ berada dalam $\mathcal D$. Memang,
setiap $C\in\mathcal S^{\otimes T}$ bergantung pada paling banyak terhitung
banyak koordinat: kelas kejadian ruang lintasan yang memiliki sifat itu
merupakan sigma-aljabar dan memuat seluruh silinder. Karena persegi panjang
membangkitkan $\mathcal T\otimes\mathcal S^{\otimes T}$, seluruh bagian
terukur berada dalam $\mathcal D$. $\square$

**Bukti teorema.** Andaikan
$E=e^{-1}(\{1\})$ terukur. Pilih himpunan terhitung $J$ dari lemma dan ambil
$t_0\in[0,1]\setminus J$. Biarkan $\omega_0$ menjadi lintasan nol dan
$\omega_1$ lintasan yang bernilai satu hanya pada $t_0$. Kedua lintasan sama
pada $J$. Namun

$$
e(t_0,\omega_0)=0,
\qquad
e(t_0,\omega_1)=1,
$$

sehingga keanggotaan $(t_0,\omega_0)$ dan $(t_0,\omega_1)$ dalam $E$
berbeda. Ini bertentangan dengan lemma. $\square$

Tidak ada kontradiksi dengan proposisi sebelumnya. Setiap koordinat
$\pi_t:S^T\to S$ terukur, sehingga peta lintasan identitas
$S^T\to S^T$ terukur. Yang gagal ialah keterukuran peta dua-argumen
$(t,\omega)\mapsto\omega(t)$ pada sigma-aljabar produk yang dinyatakan.

Ada dua batas positif yang membantu mengisolasi sumber kegagalan.

- Jika $T$ terhitung dan setiap singleton $\{t\}$ berada dalam $\mathcal T$,
  maka untuk $A\in\mathcal S$,
  $$
  e^{-1}(A)
  =\bigcup_{t\in T}\bigl(\{t\}\times\pi_t^{-1}(A)\bigr),
  $$
  suatu gabungan terhitung himpunan terukur. Jadi evaluasi kanonik terukur
  bersama.
- Jika $T$ kompak metrik, evaluasi pada
  $T\times C(T,\mathbb R)$ dengan topologi produk dan norma seragam adalah
  kontinu. Jika $(t_n,f_n)\to(t,f)$, maka
  $$
  |f_n(t_n)-f(t)|
  \le \|f_n-f\|_\infty+|f(t_n)-f(t)|\longrightarrow0.
  $$

Dengan demikian, ruang lintasan yang lebih teratur dapat memperbaiki
keterukuran evaluasi, tetapi hanya setelah hukum proses benar-benar dibangun
sebagai hukum pada ruang tersebut.

:::

::: {#fdd-dan-hukum-lintasan-mentah .bridge-section}

## Distribusi berdimensi hingga dan hukum lintasan mentah

Distribusi berdimensi hingga, disingkat FDD, membaca hukum vektor
$(X_t)_{t\in J}$ untuk setiap $J\subset T$ hingga. Pada ruang produk mentah,
informasi ini lengkap.

> **Proposisi (FDD menentukan hukum produk mentah).** Dua proses $X$ dan $Y$,
> yang boleh didefinisikan pada ruang peluang berbeda tetapi mempunyai ruang
> keadaan $(S,\mathcal S)$ yang sama, mempunyai FDD yang sama jika dan hanya
> jika hukum lintasan mentahnya sama pada
> $(S^T,\mathcal S^{\otimes T})$.

**Bukti.** Jika hukum lintasannya sama, dorongan melalui setiap proyeksi hingga
$\pi_J$ sama, sehingga FDD sama. Sebaliknya, anggap semua FDD sama. Untuk
silinder $C=\pi_J^{-1}(B)$,

$$
\mathsf P_X(C)
=\mathbb P_X((X_t)_{t\in J}\in B)
=\mathbb P_Y((Y_t)_{t\in J}\in B)
=\mathsf P_Y(C).
$$

Silinder membentuk sistem-$\pi$, memuat seluruh ruang, dan membangkitkan
$\mathcal S^{\otimes T}$. Kelas kejadian tempat kedua ukuran peluang itu
sepakat merupakan sistem Dynkin. Teorema sistem-$\pi$- $\lambda$ memberi
kesamaan pada seluruh sigma-aljabar produk. $\square$

Proposisi ini merupakan pernyataan keunikan, bukan teorema keberadaan baru.
Jembatan Kolmogorov menjawab kapan keluarga FDD melahirkan hukum produk;
proposisi di sini menjawab bahwa, setelah hukum itu ada, tidak ada dua hukum
berbeda pada sigma-aljabar produk dengan FDD yang sama.

Kata-kata "pada sigma-aljabar produk" tidak boleh dihapus. FDD tidak otomatis
menentukan nilai pada himpunan yang bukan anggota sigma-aljabar tersebut, dan
tidak membuat himpunan seperti "lintasan kontinu" menjadi terukur di ruang
mentah.

:::

::: {#sifat-lintasan-di-ruang-mentah .bridge-section}

## Mengapa sifat lintasan belum menjadi kejadian mentah

Setiap $E\in\mathcal S^{\otimes T}$ bergantung pada paling banyak terhitung
banyak koordinat. Bukti singkatnya mengikuti pola yang sudah dipakai: kelas
semua bagian $E\subset S^T$ yang keanggotaannya ditentukan oleh suatu
$J\subset T$ terhitung merupakan sigma-aljabar; kelas itu memuat setiap
silinder, sehingga memuat sigma-aljabar yang dibangkitkan silinder.

Ambil sekarang $T=[0,1]$, $S=\mathbb R$, dan

$$
\mathcal C=C([0,1],\mathbb R)\subset\mathbb R^{[0,1]}.
$$

Himpunan $\mathcal C$ **bukan** anggota sigma-aljabar produk mentah
$\mathcal B(\mathbb R)^{\otimes[0,1]}$. Andaikan ia terukur dan bergantung
pada koordinat dalam himpunan terhitung $J$. Pilih $t_0\notin J$. Lintasan
nol $f_0$ kontinu. Lintasan

$$
f_1(t)=\mathbf 1_{\{t_0\}}(t)
$$

tidak kontinu, tetapi $f_0|_J=f_1|_J$. Keanggotaan dalam $\mathcal C$ tidak
dapat ditentukan oleh $J$, suatu kontradiksi.

Akibatnya, jika $\mu$ baru didefinisikan pada
$\mathcal B(\mathbb R)^{\otimes[0,1]}$, ungkapan

$$
\mu\bigl(C([0,1],\mathbb R)\bigr)=1
$$

belum merupakan pernyataan yang sah: argumennya bukan kejadian pada ruang
terukur itu. Demikian pula, kita tidak boleh mengurangi sigma-aljabar secara
diam-diam ke ruang lintasan kontinu atau cadlag. Diperlukan konstruksi ukuran
pada ruang lintasan teratur, atau sebuah teorema versi/modifikasi yang
menyediakan peubah acak bernilai ruang tersebut.

Contoh satu lonjakan memperlihatkan fenomena ini secara probabilistik. Pada
$([0,1],\mathcal B,\lambda)$, definisikan

$$
X_t(\omega)=0,
\qquad
Y_t(\omega)=\mathbf1_{\{t=\omega\}}.
\tag{1}
$$

Untuk setiap himpunan waktu hingga, dengan peluang satu nilai $\omega$ tidak
sama dengan satu pun waktu itu. Maka seluruh FDD $Y$ sama dengan FDD proses
nol $X$. Menurut proposisi sebelumnya, hukum lintasan mentah keduanya sama,
yaitu ukuran titik pada lintasan nol jika dilihat melalui sigma-aljabar
produk. Namun setiap lintasan $Y$ mempunyai satu lonjakan dan tidak kontinu.
Tidak ada kontradiksi: kontinuitas bukan kejadian pada sigma-aljabar produk
mentah.

:::

::: {#hukum-pada-ruang-lintasan-kontinu .bridge-section}

## Hukum pada ruang lintasan kontinu

Sekarang beri $C=C([0,1],\mathbb R)$ norma seragam
$\|f\|_\infty=\sup_t|f(t)|$ dan sigma-aljabar Borel $\mathcal B(C)$. Untuk
$t\in[0,1]$, evaluasi $e_t(f)=f(t)$ kontinu. Lebih kuat lagi, evaluasi pada
waktu-waktu rasional sudah membangkitkan seluruh sigma-aljabar Borel.

> **Teorema (koordinat rasional membangkitkan ruang kontinu).** Jika
> $Q=\mathbb Q\cap[0,1]$, maka
> $$
> \mathcal B(C)=\sigma(e_q:q\in Q).
> $$

**Bukti.** Karena setiap $e_q$ kontinu,
$\sigma(e_q:q\in Q)\subset\mathcal B(C)$. Untuk arah sebaliknya, kontinuitas
dan kerapatan $Q$ memberi, bagi $f,g\in C$,

$$
\|f-g\|_\infty
=\sup_{t\in[0,1]}|f(t)-g(t)|
=\sup_{q\in Q}|f(q)-g(q)|.
\tag{2}
$$

Untuk pusat $f\in C$ dan $r>0$, bola terbuka dapat ditulis

$$
B(f,r)
=\bigcup_{n:\,1/n<r}
\bigcap_{q\in Q}
\left\{g:|g(q)-f(q)|\le r-\frac1n\right\}.
\tag{3}
$$

Ruas kanan terukur terhadap evaluasi rasional. Kesetaraan (3) memakai celah
positif antara $\|f-g\|_\infty$ dan $r$; sekadar menulis irisan semua
ketaksamaan ketat akan keliru pada kasus supremum sama dengan $r$.

Ruang $C([0,1],\mathbb R)$ separabel dalam norma seragam. Memang, teorema
aproksimasi Weierstrass dan pendekatan koefisien real oleh bilangan rasional
menunjukkan bahwa polinom berkoefisien rasional membentuk himpunan rapat yang
terhitung. Karena itu setiap himpunan terbuka merupakan gabungan terhitung
bola dari suatu basis terhitung. Semua himpunan terbuka berada dalam
$\sigma(e_q:q\in Q)$, sehingga seluruh $\mathcal B(C)$ juga berada di sana.
$\square$

Akibatnya, jika $Z$ dan $W$ benar-benar merupakan peubah acak bernilai
$C([0,1],\mathbb R)$ dan mempunyai FDD yang sama, maka hukum Borel mereka pada
$C$ sama. Bahkan FDD pada waktu rasional cukup: kedua hukum sepakat pada
silinder rasional, lalu pada sigma-aljabar yang dibangkitkannya.

Hasil ini tidak membuktikan bahwa proses mentah sebarang mempunyai versi
kontinu. Ia hanya menyatakan keunikan hukum setelah keterukuran sebagai peubah
acak bernilai $C$ sudah tersedia. Teorema Kolmogorov-Chentsov atau argumen
keteraturan lain diperlukan untuk menghasilkan versi semacam itu. Teorema
perluasan Kolmogorov dan teorema kontinuitas Kolmogorov-Chentsov mempunyai
fungsi yang berbeda.

:::

::: {#modifikasi-dan-ketakterbedaan .bridge-section}

## Modifikasi, FDD yang sama, dan ketakterbedaan

Demi membuat kejadian kesamaan di bawah terdefinisi, pada bagian ini anggap
diagonal $\Delta_S=\{(x,x):x\in S\}$ berada dalam
$\mathcal S\otimes\mathcal S$; syarat ini berlaku, misalnya, untuk ruang
keadaan Borel standar dan khususnya untuk proses bernilai real.

Dua proses $X$ dan $Y$ pada ruang peluang yang sama disebut **modifikasi**
satu sama lain apabila

$$
\mathbb P(X_t=Y_t)=1
\qquad\text{untuk setiap }t\in T.
\tag{4}
$$

Mereka disebut **tak terbedakan** apabila terdapat satu kejadian terukur
$A\in\mathcal A$ dengan $\mathbb P(A)=1$ sedemikian sehingga

$$
X_t(\omega)=Y_t(\omega)
\qquad
\text{untuk setiap }t\in T\text{ dan setiap }\omega\in A.
\tag{5}
$$

Definisi (5) sengaja menyebut satu kejadian terukur. Kita tidak mendefinisikan
$A$ sebagai irisan tak terhitung dari kejadian-kejadian pada (4), karena irisan
tak terhitung tidak harus berada dalam sigma-aljabar dan tidak mewarisi
peluang satu.

Selalu berlaku

$$
\text{tak terbedakan}
\Longrightarrow
\text{modifikasi}
\Longrightarrow
\text{FDD sama}.
\tag{6}
$$

Implikasi kedua benar karena untuk $J$ hingga, irisan kejadian
$\{X_t=Y_t\}$, $t\in J$, masih mempunyai peluang satu. Pada kejadian itu
vektor hingga kedua proses sama.

Kedua kebalikan pada (6) gagal secara umum.

- **FDD sama tidak menyiratkan modifikasi.** Pada ruang dua titik dengan
  peubah Bernoulli seimbang $U$, tetapkan $X_t=U$ dan $Y_t=1-U$ untuk semua
  $t$. Setiap vektor hingga $X$ bernilai semua nol atau semua satu dengan
  peluang masing-masing setengah; vektor $Y$ mempunyai hukum yang sama.
  Namun $\mathbb P(X_t=Y_t)=0$ untuk setiap $t$.
- **Modifikasi tidak menyiratkan ketakterbedaan.** Proses pada (1) merupakan
  modifikasi satu sama lain, sebab untuk setiap $t$ tetap,
  $\lambda(\{\omega:t=\omega\})=0$. Akan tetapi, untuk setiap $\omega$,
  keduanya berbeda pada waktu $t=\omega$. Tidak ada satu pun titik sampel
  tempat kedua lintasan sama untuk seluruh waktu.

Contoh (1) bahkan terukur bersama: himpunan
$\{(t,\omega):t=\omega\}$ adalah diagonal tertutup dalam $[0,1]^2$. Jadi
keterukuran bersama pun tidak mengubah modifikasi menjadi ketakterbedaan.

Keteraturan lintasan memberi kondisi tambahan yang berguna. Misalkan $X$ dan
$Y$ adalah modifikasi pada ruang peluang yang sama. Andaikan ada kejadian
terukur $A_X,A_Y$ berpeluang satu tempat lintasan masing-masing kontinu pada
$[0,1]$. Untuk setiap $q\in Q$, kejadian
$A_q=\{X_q=Y_q\}$ mempunyai peluang satu. Maka

$$
A=A_X\cap A_Y\cap\bigcap_{q\in Q}A_q
$$

terukur dan berpeluang satu karena $Q$ terhitung. Pada $A$, dua fungsi kontinu
sama pada himpunan rasional yang rapat, sehingga sama pada seluruh
$[0,1]$. Jadi modifikasi kontinu tak terbedakan.

Perhatikan dua peran yang berbeda. FDD yang sama untuk peubah acak bernilai
$C$ memberi **hukum Borel yang sama** pada $C$; ia tidak menentukan kopling
kedua peubah acak. Asumsi modifikasi memberi kesamaan tiap waktu dalam satu
kopling; kontinuitas lalu mengangkat kesamaan rasional menjadi kesamaan semua
waktu pada satu kejadian berpeluang satu.

:::

::: {#audit-klaim-lintasan .bridge-section}

## Audit klaim lintasan

Tabel berikut merangkum batas kesimpulan.

| Data yang tersedia | Kesimpulan yang sah | Yang belum mengikuti |
|---|---|---|
| Setiap $X_t$ terukur | $\Phi_X$ terukur ke ruang produk mentah | keterukuran bersama; keteraturan lintasan |
| $\widehat X$ terukur bersama | setiap koordinat dan setiap bagian lintasan terukur | kontinuitas atau sifat cadlag |
| Semua FDD diketahui | hukum unik pada $\mathcal S^{\otimes T}$, jika hukum itu ada | nilai pada himpunan di luar sigma-aljabar produk |
| Peubah acak bernilai $C([0,1],\mathbb R)$ | hukum Borel ditentukan oleh evaluasi rasional | keberadaan versi kontinu dari proses mentah |
| $X,Y$ modifikasi | FDD sama | ketakterbedaan tanpa keteraturan tambahan |
| Modifikasi dengan lintasan kontinu hampir pasti | ketakterbedaan | tidak ada klaim tambahan tentang proses lain |

Saat membaca sebuah pembuktian, tanyakan secara berurutan: apa ruang sasaran
peta lintasannya, sigma-aljabar apa yang dipakai, apakah evaluasi waktu-proses
perlu terukur bersama, apakah sifat lintasan merupakan kejadian pada ruang itu,
dan apakah kesamaan yang diklaim adalah kesamaan hukum, modifikasi, atau
ketakterbedaan. Lima pertanyaan itu mencegah FDD diberi kekuatan yang tidak
dimilikinya.

:::

::: {#latihan-penguasaan-keterukuran .bridge-section}

## Latihan penguasaan

::: {#unit.o009.original.mastery.measurability-path-law.01 .mastery-sequence}

::: {#unit.o009.original.mastery.measurability-path-law.01.exercise .exercise}
### Latihan 1 — koordinat kanonik tidak terukur bersama

Ambil $T=[0,1]$, $S=\{0,1\}$, dan $\Omega=S^T$ seperti pada teorema evaluasi
kanonik.

1. Buktikan bahwa setiap
   $E\in\mathcal B(T)\otimes\mathcal S^{\otimes T}$ bergantung pada suatu
   himpunan koordinat lintasan $J\subset T$ yang terhitung, seragam untuk
   seluruh nilai $t$.
2. Gunakan hasil itu untuk membuktikan bahwa
   $e(t,\omega)=\omega(t)$ tidak terukur bersama.
3. Jelaskan mengapa setiap $\pi_t$ dan peta lintasan identitas tetap terukur.
:::

::: {#unit.o009.original.mastery.measurability-path-law.01.hint.01 .hint}
**Petunjuk 1.** Bentuk kelas bagian $E\subset T\times S^T$ yang
keanggotaannya tidak berubah apabila lintasan diubah di luar suatu $J$
terhitung. Tunjukkan bahwa kelas itu sigma-aljabar dan memuat persegi panjang
$B\times C$.
:::

::: {#unit.o009.original.mastery.measurability-path-law.01.hint.02 .hint}
**Petunjuk 2.** Setelah memperoleh $J$, pilih $t_0\notin J$. Bandingkan lintasan
nol dengan lintasan yang hanya bernilai satu pada $t_0$, lalu evaluasi keduanya
pada waktu yang sama $t_0$.
:::

::: {#unit.o009.original.mastery.measurability-path-law.01.answer .answer}
**Jawaban ringkas.** Sigma-aljabar produk hanya dapat membaca paling banyak
terhitung banyak koordinat lintasan sekaligus. Jika
$e^{-1}(\{1\})$ bergantung pada $J$, lintasan nol dan lonjakan pada
$t_0\notin J$ seharusnya memberi keanggotaan yang sama, padahal evaluasi pada
$t_0$ memberi nol dan satu. Setiap $\pi_t$ tetap terukur karena justru
proyeksi-proyeksi itu yang membangkitkan sigma-aljabar produk.
:::

::: {#unit.o009.original.mastery.measurability-path-law.01.solution .solution}
**Penyelesaian lengkap.** Misalkan $\mathcal D$ adalah kelas semua
$E\subset T\times S^T$ yang mempunyai suatu $J_E\subset T$ terhitung dengan
sifat

$$
\omega|_{J_E}=\omega'|_{J_E}
\Longrightarrow
\bigl[(t,\omega)\in E\iff(t,\omega')\in E\bigr]
$$

untuk semua $t$. Komplemen mempertahankan $J_E$. Untuk $E_n\in\mathcal D$,
gabungan $J=\bigcup_nJ_{E_n}$ terhitung dan menopang $\bigcup_nE_n$.
Jadi $\mathcal D$ sigma-aljabar.

Jika $E=B\times C$ dan $C\in\mathcal S^{\otimes T}$, kejadian $C$ bergantung
pada suatu himpunan koordinat terhitung: kelas kejadian dengan sifat itu adalah
sigma-aljabar yang memuat silinder. Maka $B\times C\in\mathcal D$. Karena
persegi panjang membangkitkan sigma-aljabar produk,
$\mathcal B(T)\otimes\mathcal S^{\otimes T}\subset\mathcal D$.

Andaikan $e$ terukur. Untuk $E=e^{-1}(\{1\})$, ambil penopang terhitung $J$
dan $t_0\notin J$. Definisikan $\omega_0(t)=0$ untuk semua $t$ dan
$\omega_1(t)=\mathbf1_{\{t_0\}}(t)$. Kedua lintasan sama pada $J$, tetapi

$$
(t_0,\omega_0)\notin E,
\qquad
(t_0,\omega_1)\in E,
$$

kontradiksi. Untuk setiap $t$ tetap, $\pi_t^{-1}(A)$ adalah silinder, sehingga
$\pi_t$ terukur. Peta identitas $S^T\to S^T$ juga terukur. Jadi kegagalan
terletak tepat pada keterukuran dua-argumen, bukan pada koordinat atau peta
lintasan mentah.
:::

:::

::: {#unit.o009.original.mastery.measurability-path-law.02 .mastery-sequence}

::: {#unit.o009.original.mastery.measurability-path-law.02.exercise .exercise}
### Latihan 2 — modifikasi terukur bersama dengan lintasan berbeda

Pada $([0,1],\mathcal B,\lambda)$, definisikan

$$
X_t(\omega)=0,
\qquad
Y_t(\omega)=\mathbf1_{\{t=\omega\}}.
$$

Buktikan bahwa $Y$ terukur bersama, $X$ dan $Y$ merupakan modifikasi, semua
FDD mereka sama, tetapi mereka tidak tak terbedakan. Tunjukkan pula bahwa
setiap lintasan $X$ kontinu sedangkan setiap lintasan $Y$ mempunyai satu
lonjakan. Rekonsiliasikan fakta ini dengan kesamaan hukum lintasan mentah.
:::

::: {#unit.o009.original.mastery.measurability-path-law.02.hint.01 .hint}
**Petunjuk 1.** Himpunan tempat $Y=1$ adalah diagonal
$\{(t,\omega):t=\omega\}$ dalam $[0,1]^2$. Untuk $t$ tetap, singleton
$\{t\}$ mempunyai ukuran Lebesgue nol.
:::

::: {#unit.o009.original.mastery.measurability-path-law.02.hint.02 .hint}
**Petunjuk 2.** Untuk banyak waktu yang hingga, gabungkan singleton waktu itu.
Untuk ketakterbedaan, pada setiap $\omega$ pilih waktu $t=\omega$. Kesamaan
hukum mentah hanya menguji kejadian yang bergantung pada koordinat terhitung.
:::

::: {#unit.o009.original.mastery.measurability-path-law.02.answer .answer}
**Jawaban ringkas.** Diagonal tertutup membuat $Y$ terukur bersama. Untuk tiap
$t$, $Y_t=0=X_t$ hampir pasti, sehingga keduanya modifikasi dan mempunyai FDD
yang sama. Namun $Y_\omega(\omega)=1\ne0=X_\omega(\omega)$ untuk setiap
$\omega$, jadi tidak ada titik sampel tempat seluruh lintasan sama. Hukum
produk mentah tetap sama karena kontinuitas bukan kejadian dalam
$\mathcal B(\mathbb R)^{\otimes[0,1]}$.
:::

::: {#unit.o009.original.mastery.measurability-path-law.02.solution .solution}
**Penyelesaian lengkap.** Diagonal
$D=\{(t,\omega):t=\omega\}$ tertutup dalam $[0,1]^2$, sehingga indikatornya
$Y$ terukur terhadap $\mathcal B\otimes\mathcal B$. Untuk $t$ tetap,

$$
\lambda\{\omega:Y_t(\omega)\ne X_t(\omega)\}
=\lambda(\{t\})=0.
$$

Jadi $X$ dan $Y$ merupakan modifikasi. Jika
$J=\{t_1,\ldots,t_n\}$, di luar himpunan hingga $J$ seluruh
$Y_{t_i}(\omega)$ nol. Himpunan itu berpeluang satu, sehingga vektor
$(Y_{t_1},\ldots,Y_{t_n})$ hampir pasti sama dengan vektor nol, persis FDD
$X$.

Sebaliknya, untuk setiap $\omega$, pilih $t=\omega$. Maka
$Y_t(\omega)=1$ dan $X_t(\omega)=0$. Himpunan titik sampel tempat kedua proses
sama untuk semua $t$ kosong, jadi keduanya tidak tak terbedakan.

Lintasan $X$ adalah fungsi nol yang kontinu. Lintasan $Y$ pada titik sampel
$\omega$ adalah fungsi yang satu hanya di $t=\omega$, sehingga tidak kontinu.
Kesamaan FDD memberi kesamaan ukuran dorong pada sigma-aljabar produk mentah.
Setiap kejadian mentah bergantung pada koordinat dalam suatu $J$ terhitung;
dengan peluang satu, $\omega\notin J$, sehingga lonjakan tidak terbaca oleh
kejadian itu. Himpunan semua lintasan kontinu sendiri bukan kejadian mentah.
Inilah sebabnya kesamaan hukum mentah konsisten dengan perilaku lintasan yang
berbeda pada setiap titik sampel.
:::

:::

::: {#unit.o009.original.mastery.measurability-path-law.03 .mastery-sequence}

::: {#unit.o009.original.mastery.measurability-path-law.03.exercise .exercise}
### Latihan 3 — modifikasi kontinu menjadi tak terbedakan

Misalkan $X$ dan $Y$ adalah proses real pada $[0,1]$.

1. Jika keduanya merupakan peubah acak bernilai
   $C([0,1],\mathbb R)$ dan mempunyai FDD yang sama, buktikan bahwa hukum Borel
   mereka pada $C([0,1],\mathbb R)$ sama.
2. Sekarang andaikan $X$ dan $Y$ berada pada ruang peluang yang sama,
   merupakan modifikasi, dan masing-masing mempunyai lintasan kontinu pada
   suatu kejadian terukur berpeluang satu. Buktikan bahwa keduanya tak
   terbedakan.
3. Jelaskan mengapa kesamaan FDD saja tidak cukup untuk kesimpulan bagian 2.
:::

::: {#unit.o009.original.mastery.measurability-path-law.03.hint.01 .hint}
**Petunjuk 1.** Sigma-aljabar Borel pada $C([0,1],\mathbb R)$ dibangkitkan
oleh evaluasi pada $Q=\mathbb Q\cap[0,1]$. FDD yang sama membuat kedua hukum
sepakat pada seluruh silinder rasional.
:::

::: {#unit.o009.original.mastery.measurability-path-law.03.hint.02 .hint}
**Petunjuk 2.** Untuk bagian kedua, iris kejadian kontinuitas kedua proses
dengan kejadian $\{X_q=Y_q\}$ untuk seluruh $q\in Q$. Irisan ini terhitung.
Pada kejadian hasilnya, gunakan kerapatan $Q$ dan kontinuitas.
:::

::: {#unit.o009.original.mastery.measurability-path-law.03.answer .answer}
**Jawaban ringkas.** Evaluasi rasional membangkitkan $\mathcal B(C)$, sehingga
FDD rasional menentukan hukum Borel pada $C$. Jika kedua proses juga
modifikasi pada ruang yang sama, ada kejadian berpeluang satu tempat keduanya
kontinu dan sama pada semua waktu rasional; kontinuitas memperluas kesamaan itu
ke semua waktu. Kesamaan FDD sendiri hanya menyamakan hukum, bukan kopling
titik demi titik.
:::

::: {#unit.o009.original.mastery.measurability-path-law.03.solution .solution}
**Penyelesaian lengkap.** Biarkan $\nu_X$ dan $\nu_Y$ menjadi hukum Borel
kedua peubah acak bernilai $C$. Untuk $q_1,\ldots,q_n\in Q$ dan
$B\in\mathcal B(\mathbb R^n)$, FDD yang sama memberi

$$
\nu_X\{f:(f(q_1),\ldots,f(q_n))\in B\}
=
\nu_Y\{f:(f(q_1),\ldots,f(q_n))\in B\}.
$$

Silinder rasional membentuk sistem-$\pi$ yang membangkitkan
$\mathcal B(C)$, sehingga teorema sistem-$\pi$- $\lambda$ memberi
$\nu_X=\nu_Y$.

Untuk bagian kedua, pilih kejadian terukur $A_X,A_Y$ berpeluang satu tempat
lintasan masing-masing kontinu. Karena $X$ dan $Y$ modifikasi, untuk setiap
$q\in Q$ kejadian $A_q=\{X_q=Y_q\}$ berpeluang satu. Bentuk

$$
A=A_X\cap A_Y\cap\bigcap_{q\in Q}A_q.
$$

Himpunan $Q$ terhitung, sehingga $A$ terukur dan berpeluang satu. Untuk
$\omega\in A$, fungsi kontinu $t\mapsto X_t(\omega)$ dan
$t\mapsto Y_t(\omega)$ sama pada $Q$ yang rapat. Bagi $t\in[0,1]$, ambil
$q_n\to t$; kontinuitas memberi

$$
X_t(\omega)
=\lim_nX_{q_n}(\omega)
=\lim_nY_{q_n}(\omega)
=Y_t(\omega).
$$

Jadi satu kejadian $A$ membuktikan ketakterbedaan. Kesamaan FDD tanpa asumsi
modifikasi tidak menentukan bagaimana dua proses dipasangkan pada ruang
peluang yang sama; contoh $U$ dan $1-U$ menunjukkan bahwa FDD dapat sama
sementara kesamaan pada satu waktu pun gagal hampir pasti.
:::

:::

:::

::: {#hak-dan-provenans-keterukuran .bridge-section}

## Hak dan provenans

Unit **Keterukuran proses dan hukum lintasan**, termasuk ketiga latihan,
petunjuk, jawaban, dan penyelesaian di atas, merupakan materi asli berbahasa
Indonesia yang disusun untuk edisi ini dan dilisensikan terpisah di bawah
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), sejauh hak baru
timbul. ID hak komponennya ialah
`rights.o009.original.bridge.process-measurability-path-law.cc-by-4.0`.

Penyusunan unit ini dibantu oleh **OpenAI Codex gpt-5.6-sol, Ultra.** Identitas
model tersebut tidak menggantikan kredit penulis sumber atau kontributor
manusia. Tautan ke unit Random Services, QuantEcon, dan jembatan sebelumnya
berfungsi sebagai prasyarat dan batas duplikasi; materi asli ini tidak
melisensikan ulang komponen mereka. Hak campuran seluruh edisi tetap dijelaskan
dalam `LICENSES.md` dan backend hak per komponen.

Unit ini independen dan tidak didukung atau disahkan oleh penulis Random
Services, QuantEcon, lembaga mereka, atau penulis sumber lain. Ia juga tidak
mengklaim bahwa teorema perluasan Kolmogorov sendiri menghasilkan lintasan
kontinu, keterukuran bersama, atau hukum pada sigma-aljabar lintasan yang tidak
dinyatakan.

:::

:::
