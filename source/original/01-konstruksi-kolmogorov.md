---
title: "Konstruksi Kolmogorov dan proses kanonik"
lang: id-ID
author:
  - "Codex (penulisan materi asli atas arahan pengguna)"
authoring:
  course_id: "o009"
  unit_id: "unit.o009.original.bridge.kolmogorov-canonical-process"
  target_locale: "id-ID"
  source_type: "original"
  rights_id: "rights.o009.original.bridge.kolmogorov.cc-by-4.0"
  license: "CC-BY-4.0"
  model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."
---

::: {#unit.o009.original.bridge.kolmogorov-canonical-process .original-bridge}

# Konstruksi Kolmogorov dan proses kanonik

::: {#tujuan-dan-prasyarat .bridge-section}

## Tujuan dan prasyarat

Sebuah proses stokastik sering diperkenalkan melalui hukum-hukum berdimensi
hingga: kita menentukan distribusi bersama pada setiap kumpulan waktu yang
hingga, lalu berharap semuanya berasal dari satu proses. Harapan itu perlu
sebuah teorema. Unit ini mengisi langkah dari keluarga hukum yang konsisten
menuju ukuran peluang pada ruang lintasan mentah, kemudian menuju proses
koordinat kanonik.

Setelah menyelesaikan unit ini, pembaca mampu:

1. mengaudit hipotesis teorema perluasan Kolmogorov dan membedakan kesimpulan
   sebenarnya dari klaim tambahan tentang lintasan; dan
2. membangun proses koordinat kanonik dari hukum-hukum berdimensi hingga yang
   konsisten secara proyektif.

Prasyaratnya ialah pembahasan [ruang produk peluang dan ruang
kanonik](../prob/Probability2.html), [proses stokastik dan distribusi
berdimensi hingga](../prob/Processes.html), serta, untuk contoh Markov,
[sifat Markov dan kernel transisi](../quantecon/lectures/markov_prop.html).
Kita tidak mengulang pembuktian produk koordinat yang saling bebas, definisi
dasar proses stokastik, ataupun teori rantai Markov waktu kontinu. Fokusnya
lebih sempit: apa tepatnya yang harus konsisten, ukuran pada ruang mana yang
dihasilkan, dan apa yang belum dihasilkan oleh teorema tersebut.

Secara operasional, konstruksi ini memisahkan tiga pertanyaan yang mudah
tercampur. Pertama, apakah rumus-rumus hingga benar-benar saling cocok ketika
koordinat dihapus atau diurutkan ulang? Kedua, apakah kecocokan itu melahirkan
ukuran yang aditif terhitung pada ruang produk? Ketiga, apakah ukuran tersebut
memiliki lintasan dengan keteraturan yang diinginkan? Konsistensi proyektif
menjawab pertanyaan pertama, teorema perluasan dengan hipotesisnya menjawab
pertanyaan kedua, sedangkan pertanyaan ketiga tetap memerlukan teorema lain.
Pemisahan ini menjadi pola audit yang akan dipakai sepanjang unit.

:::

::: {#ruang-lintasan-produk .bridge-section}

## Ruang lintasan produk

Biarkan $T$ menjadi himpunan indeks sebarang. Unsur $T$ dapat berupa waktu,
lokasi, atau label lain; pada tahap ini kita bahkan tidak memerlukan urutan
atau topologi pada $T$. Biarkan $(S,\mathcal S)$ menjadi ruang terukur dengan
$S$ tak kosong. Ruang lintasan mentah adalah

$$
\Omega=S^T=\{\omega:T\to S\}.
$$

Untuk $t\in T$, proyeksi koordinat didefinisikan oleh

$$
\pi_t(\omega)=\omega(t).
$$

Jika $J\subset T$ hingga, tulis $S^J$ untuk himpunan semua fungsi $J\to S$
dan definisikan proyeksi hingga

$$
\pi_J:S^T\longrightarrow S^J,
\qquad
\pi_J(\omega)=\omega|_J.
$$

Pada $S^J$ kita memakai sigma-aljabar produk hingga
$\mathcal S^{\otimes J}$. Untuk $A\in\mathcal S^{\otimes J}$, himpunan

$$
C(J,A)=\pi_J^{-1}(A)
$$

disebut *himpunan silinder*. Keanggotaannya hanya diperiksa melalui sejumlah
hingga koordinat dalam $J$. Sigma-aljabar yang relevan bagi konstruksi ini
adalah

$$
\mathcal F^0
=\sigma(\pi_t:t\in T)
=\sigma\!\left\{\pi_J^{-1}(A):
J\subset T\text{ hingga},\ A\in\mathcal S^{\otimes J}\right\}
=\mathcal S^{\otimes T}.
$$

Notasi terakhir, $\mathcal S^{\otimes T}$, **didefinisikan** sebagai
sigma-aljabar produk yang dibangkitkan proyeksi koordinat. Ini penting ketika
$T$ tak terhitung: kita tidak sedang memakai semua bagian dari $S^T$, dan
kita tidak diam-diam memilih sigma-aljabar yang lebih besar. Keunikan ukuran
yang dibuktikan nanti juga hanya merupakan keunikan pada $\mathcal F^0$.

Silinder menerjemahkan pengamatan yang benar-benar berdimensi hingga. Sebagai
contoh, pernyataan bahwa lintasan berada dalam himpunan tertentu pada tiga
waktu hanya bergantung pada proyeksi ke tiga koordinat itu. Komplemen,
gabungan hingga, dan irisan hingga dari silinder dapat ditulis lagi sebagai
silinder setelah semua koordinat yang terlibat digabungkan. Jadi silinder
membentuk aljabar kejadian dasar, walaupun belum tertutup terhadap seluruh
operasi terhitung.

Ada satu fakta lingkup yang berguna ketika $T$ tak terhitung: setiap kejadian
dalam $\mathcal F^0$ bergantung pada paling banyak terhitung banyak
koordinat. Untuk melihatnya, kumpulkan semua kejadian yang keanggotaannya
ditentukan oleh suatu himpunan koordinat terhitung. Kelas ini memuat setiap
silinder dan tertutup terhadap komplemen serta gabungan terhitung, karena
gabungan terhitung dari himpunan koordinat terhitung tetap terhitung. Maka
kelas itu memuat sigma-aljabar yang dibangkitkan silinder. Fakta ini tidak
mengubah ruang lintasan menjadi terhitung; fakta ini hanya membatasi berapa
banyak koordinat yang dapat dibaca oleh satu kejadian terukur produk.

:::

::: {#konsistensi-proyektif .bridge-section}

## Konsistensi proyektif

Misalkan untuk setiap $J\subset T$ yang hingga diberikan ukuran peluang
$\mu_J$ pada $(S^J,\mathcal S^{\otimes J})$. Apabila $K\subset J$, definisikan

$$
p_{J,K}:S^J\longrightarrow S^K,
\qquad
p_{J,K}(x)=x|_K.
$$

Keluarga $\{\mu_J\}$ disebut **konsisten secara proyektif** apabila

$$
\mu_J\circ p_{J,K}^{-1}=\mu_K
\qquad\text{untuk setiap }K\subset J\subset T
\text{ yang hingga}.
\tag{1}
$$

Artinya, jika sebuah vektor acak pada koordinat $J$ dibuang semua
koordinatnya di luar $K$, hukum marginal yang tersisa harus tepat $\mu_K$.
Kita mengindeks hukum dengan *himpunan berlabel* $J$, bukan dengan daftar
berurutan. Karena itu, dua pengurutan dari anggota $J$ hanyalah dua cara
menuliskan unsur yang sama dari $S^J$; perubahan urutan diterjemahkan oleh
peta permutasi koordinat. Dengan konvensi ini, syarat permutasi dan syarat
marginal yang biasa ditulis terpisah untuk tupel berurutan sama-sama tercakup
oleh (1): pelabelan menangani permutasi, sedangkan $p_{J,K}$ menangani
penghapusan koordinat.

Syarat (1) perlu. Jika suatu ukuran $\mu$ pada $(S^T,\mathcal F^0)$ memang
memiliki marginal $\mu_J=\mu\circ\pi_J^{-1}$, maka identitas
$\pi_K=p_{J,K}\circ\pi_J$ langsung memberikan

$$
\mu_J\circ p_{J,K}^{-1}
=\mu\circ\pi_J^{-1}\circ p_{J,K}^{-1}
=\mu\circ\pi_K^{-1}
=\mu_K.
$$

Pertanyaan yang lebih dalam adalah apakah syarat yang perlu ini juga cukup.
Jawabannya ya di bawah hipotesis keteraturan yang eksplisit berikut.

Pada himpunan persegi panjang terukur, syarat tersebut sangat konkret. Jika
$J=\{t_1,\ldots,t_n\}$ dan
$A=A_1\times\cdots\times A_n$, penghapusan beberapa waktu harus menghasilkan
peluang yang sama dengan hukum yang sejak awal diberi pada waktu-waktu yang
tersisa. Namun pemeriksaan hanya pada rumus kepadatan atau momen tidak selalu
cukup: konsistensi merupakan kesamaan ukuran pada seluruh
$\mathcal S^{\otimes K}$. Karena itu, contoh Markov dan Gaussian di bawah
memverifikasi identitas marginal pada tingkat hukum, bukan sekadar kecocokan
beberapa statistik.

:::

::: {#teorema-perluasan-kolmogorov .bridge-section}

## Teorema perluasan Kolmogorov

> **Teorema (perluasan Kolmogorov, bentuk ruang Borel standar).** Misalkan
> $(S,\mathcal S)$ adalah ruang Borel standar dan $T$ adalah himpunan
> sebarang. Untuk setiap himpunan hingga $J\subset T$, misalkan $\mu_J$
> merupakan ukuran peluang pada
> $(S^J,\mathcal S^{\otimes J})$. Jika keluarga $\{\mu_J\}$ konsisten secara
> proyektif, maka terdapat tepat satu ukuran peluang $\mu$ pada
> $(S^T,\mathcal S^{\otimes T})$ sedemikian sehingga
> $$
> \mu\circ\pi_J^{-1}=\mu_J
> \qquad\text{untuk setiap }J\subset T\text{ yang hingga}.
> $$

Ruang Borel standar adalah ruang terukur yang isomorfik secara terukur dengan
suatu himpunan Borel dalam ruang Polish. Kelas ini mencakup ruang keadaan yang
paling sering dipakai, seperti himpunan hingga atau terhitung dengan
sigma-aljabar diskret, $\mathbb R^d$ dengan sigma-aljabar Borelnya, serta
ruang Polish beserta sigma-aljabar Borelnya. Hipotesis Borel standar di sini
merupakan hipotesis **cukup** yang jelas dan dapat diaudit; pernyataan ini
tidak mengklaim bahwa hipotesis tersebut perlu dalam setiap versi teorema
perluasan.

Keteraturan ditempatkan pada ruang keadaan, bukan pada himpunan indeks.
Teorema tidak meminta $T$ terhitung, berurutan, atau bertopologi. Sebaliknya,
struktur Borel standar pada $S$ memastikan bahwa masalah proyektif tidak
kehilangan keteraturan ukuran ketika jumlah koordinat bertambah. Ini juga
menjelaskan mengapa urutan waktu, semigrup, atau kovarians bukan bagian dari
pernyataan abstrak: semua struktur tersebut masuk melalui keluarga
$\{\mu_J\}$ pada penerapan tertentu.

:::

::: {#lingkup-bukti .bridge-section}

## Lingkup bukti

Ada tiga bagian yang perlu dibedakan. Kita membuktikan bahwa nilai yang hendak
diberikan pada silinder tidak bergantung pada representasinya, menguraikan
dengan jujur tempat teorema perluasan dipakai untuk keberadaan, lalu
membuktikan keunikan pada sigma-aljabar produk.

### Representasi silinder yang sama

Secara alami kita ingin menetapkan

$$
q\bigl(\pi_J^{-1}(A)\bigr)=\mu_J(A).
\tag{2}
$$

Namun satu silinder dapat mempunyai dua representasi. Misalkan

$$
\pi_J^{-1}(A)=\pi_K^{-1}(B),
\qquad
A\in\mathcal S^{\otimes J},\quad
B\in\mathcal S^{\otimes K}.
\tag{3}
$$

Ambil $L=J\cup K$. Pada ruang bersama $S^L$, bentuk dua pengangkatan

$$
A_L=p_{L,J}^{-1}(A),
\qquad
B_L=p_{L,K}^{-1}(B).
$$

Kita klaim $A_L=B_L$. Pilih satu titik tetap $s_0\in S$. Setiap
$x\in S^L$ dapat diperluas menjadi $\omega\in S^T$ dengan menetapkan
$\omega|_L=x$ dan $\omega(t)=s_0$ untuk $t\notin L$. Karena
$\pi_J=p_{L,J}\circ\pi_L$ dan
$\pi_K=p_{L,K}\circ\pi_L$, persamaan (3) mengatakan

$$
x\in A_L
\iff \omega\in\pi_J^{-1}(A)
\iff \omega\in\pi_K^{-1}(B)
\iff x\in B_L.
$$

Jadi kedua himpunan terangkat sama. Konsistensi proyektif kemudian memberi

$$
\mu_J(A)
=\mu_L\bigl(p_{L,J}^{-1}(A)\bigr)
=\mu_L\bigl(p_{L,K}^{-1}(B)\bigr)
=\mu_K(B).
\tag{4}
$$

Dengan demikian, (2) terdefinisi dengan baik. Argumen ini juga menunjukkan
mengapa konsistensi harus diperiksa pada ruang koordinat bersama, bukan hanya
dengan membandingkan rumus yang kebetulan tampak serupa.

### Keberadaan: bagian yang benar-benar memakai teorema

Konsistensi membuat nilai silinder pada (2) kompatibel dan aditif untuk
pembagian hingga yang tetap bergantung pada sejumlah hingga koordinat. Akan
tetapi, **aditivitas hingga bukan aditivitas terhitung**. Jadi kita tidak boleh
menyebut (2) sebagai ukuran peluang pada $\mathcal F^0$ hanya karena semua
marginal berhingga saling cocok.

Pada titik inilah teorema batas proyektif Kolmogorov untuk ruang Borel
standar dipakai. Dalam pembuktian lengkap teorema tersebut, keteraturan Borel
standar menyediakan kendali yang diperlukan agar sistem ukuran pada ruang
koordinat hingga menghasilkan ukuran yang aditif terhitung. Salah satu peta
jalan pembuktiannya ialah pertama menangani himpunan koordinat terhitung
melalui ukuran-ukuran proyektif yang konsisten dan keteraturan ruang keadaan,
lalu memakai fakta bahwa setiap kejadian dalam sigma-aljabar produk dibangun
dari paling banyak terhitung banyak koordinat. Teorema itu menghasilkan
ukuran $\mu$ pada $\mathcal F^0$ yang nilainya pada setiap silinder ialah
(2). Unit ini menggunakan hasil keberadaan tersebut; unit ini tidak
menyamarkan langkah aditivitas terhitung sebagai akibat otomatis dari
konsistensi hingga dan tidak mengulang teori umum perluasan ukuran.

Peta jalan itu dapat dibuat lebih konkret tanpa mengulang seluruh teorema.
Untuk setiap himpunan koordinat terhitung $I\subset T$, teorema pada produk
terhitung memberi ukuran $\mu_I$ yang mempunyai marginal yang ditentukan.
Jika suatu kejadian $E\in\mathcal F^0$ ditentukan oleh koordinat dalam $I$,
nilainya dibaca dari $\mu_I$. Apabila $E$ juga mempunyai representasi melalui
himpunan terhitung $K$, kedua nilai dibandingkan di ruang bersama
$S^{I\cup K}$; konsistensi marginal di ruang itu membuat hasilnya sama.
Untuk memeriksa aditivitas terhitung suatu barisan kejadian, gabungkan semua
himpunan koordinat yang menopang kejadian-kejadian tersebut. Gabungan itu
masih terhitung, sehingga seluruh pemeriksaan berlangsung di bawah satu
ukuran $\mu_L$ yang sudah aditif terhitung. Inilah mekanisme yang menjelaskan
mengapa pengurangan ke koordinat terhitung sah, sekaligus mengapa keteraturan
ruang keadaan tetap diperlukan pada langkah perluasan terhitung.

Dengan kata lain, pembuktian representasi silinder di atas hanya memastikan
bahwa kandidat nilai $q(C)$ tidak ambigu. Teorema batas proyektif itulah yang
memastikan bahwa apabila silinder-silinder disusun dalam barisan yang
melibatkan makin banyak koordinat, nilai kandidat itu tetap memenuhi syarat
limit yang diperlukan oleh ukuran peluang. Setelah teorema diterapkan, kita
boleh memakai semua operasi terhitung dalam $\mathcal F^0$ secara sah. Tanpa
langkah tersebut, yang tersedia baru data hingga yang kompatibel, bukan ruang
peluang proses yang sudah dibangun.

### Keunikan pada sigma-aljabar produk

Misalkan $\mu$ dan $\nu$ adalah dua ukuran peluang pada
$(S^T,\mathcal F^0)$ dengan marginal hingga yang sama. Kelas semua silinder

$$
\mathcal C
=\{\pi_J^{-1}(A):J\subset T\text{ hingga},
A\in\mathcal S^{\otimes J}\}
$$

adalah suatu sistem-$\pi$. Memang, jika dua silinder masing-masing bergantung
pada $J$ dan $K$, irisan keduanya dapat ditulis sebagai silinder pada
$L=J\cup K$. Selain itu, $\Omega\in\mathcal C$ dan
$\sigma(\mathcal C)=\mathcal F^0$.

Kesamaan marginal memastikan $\mu$ dan $\nu$ sepakat pada setiap anggota
$\mathcal C$; pembuktian representasi bersama sebelumnya menjamin bahwa
pernyataan ini tidak bergantung pada cara silinder ditulis. Langkah berikut
harus memperluas kesepakatan dari pengamatan hingga ke semua kejadian yang
dibangun melalui operasi terhitung. Inilah fungsi argumen kelas monoton, dan
bukan suatu asumsi tambahan tentang topologi lintasan.

Bentuk kelas

$$
\mathcal D=\{E\in\mathcal F^0:\mu(E)=\nu(E)\}.
$$

Karena $\mu$ dan $\nu$ adalah ukuran peluang, $\mathcal D$ memuat $\Omega$,
tertutup terhadap komplemen relatif, dan tertutup terhadap gabungan terhitung
dari himpunan-himpunan saling lepas. Jadi $\mathcal D$ merupakan sistem
Dynkin. Kedua ukuran mempunyai marginal yang sama, sehingga
$\mathcal C\subset\mathcal D$. Teorema sistem-$\pi$–$\lambda$—bentuk
indikator dari teorema kelas monoton—memberikan

$$
\mathcal F^0=\sigma(\mathcal C)\subset\mathcal D.
$$

Akibatnya $\mu(E)=\nu(E)$ untuk setiap $E\in\mathcal F^0$. Inilah seluruh
lingkup klaim keunikan: kesamaan pada sigma-aljabar produk yang dibangkitkan
silinder, bukan pada sigma-aljabar lebih besar yang tidak disebutkan.

:::

::: {#proses-koordinat-kanonik .bridge-section}

## Proses koordinat kanonik

Setelah teorema menghasilkan $\mu$, tetapkan pada
$(\Omega,\mathcal F^0,\mu)=(S^T,\mathcal S^{\otimes T},\mu)$

$$
X_t(\omega)=\omega(t)=\pi_t(\omega),
\qquad t\in T.
$$

Untuk $B\in\mathcal S$,

$$
X_t^{-1}(B)=\pi_t^{-1}(B)\in\mathcal F^0,
$$

sehingga setiap $X_t$ terukur. Jika $J\subset T$ hingga, peta vektor
$(X_t)_{t\in J}$ persis $\pi_J$. Oleh karena itu, untuk setiap
$A\in\mathcal S^{\otimes J}$,

$$
\mathbb P\bigl((X_t)_{t\in J}\in A\bigr)
=\mu(\pi_J^{-1}(A))
=\mu_J(A).
$$

Jadi hukum berdimensi hingga proses koordinat kanonik tepat keluarga yang
diberikan. Ini juga membuktikan klaim koordinat dan distribusi berdimensi
hingga tanpa memilih versi proses di ruang peluang lain.

Konstruksi kanonik juga merangkum setiap realisasi lain. Misalkan pada ruang
peluang $(\Omega',\mathcal A,\mathbb P')$ sudah ada keluarga peubah acak
$Y_t$ dengan hukum-hukum hingga $\mu_J$. Peta lintasan

$$
\Phi:\Omega'\longrightarrow S^T,
\qquad
\Phi(\omega')=(Y_t(\omega'))_{t\in T},
$$

terukur terhadap $\mathcal F^0$: prabayangan setiap silinder adalah kejadian
yang ditentukan oleh vektor hingga $(Y_t)_{t\in J}$. Ukuran dorong
$\mathbb P'\circ\Phi^{-1}$ memiliki marginal $\mu_J$, sehingga keunikan
memberikan $\mathbb P'\circ\Phi^{-1}=\mu$. Jadi hukum pada ruang kanonik
menyimpan tepat informasi distribusional dari setiap realisasi tersebut.
Argumen ini tidak mengatakan bahwa peta evaluasi bersama
$(t,\omega')\mapsto Y_t(\omega')$ terukur dan tidak menyamakan lintasan dua
realisasi di luar kesamaan hukumnya.

Jika $T$ terurut, kita boleh membentuk filtrasi kanonik mentah

$$
\mathcal F_t^0=\sigma(X_s:s\le t).
$$

Filtrasi ini belum dilengkapi oleh himpunan nol dan belum dibuat kontinu
kanan. Pelengkapan serta augmentasi biasa bergantung pada hukum $\mu$ dan
konvensi waktu yang dipilih; keduanya bukan bagian dari konstruksi
Kolmogorov mentah.

:::

::: {#contoh-keluarga-markov .bridge-section}

## Contoh keluarga Markov

Misalkan $(S,\mathcal S)$ Borel standar, waktu $T\subset[0,\infty)$ memuat
$0$, $\eta$ adalah hukum awal, dan $P_{s,t}(x,\mathrm dy)$ adalah keluarga
kernel transisi terukur untuk $s\le t$. Anggap
$P_{t,t}(x,\cdot)=\delta_x$ dan hukum komposisi Chapman–Kolmogorov berlaku:

$$
P_{r,t}(x,A)
=\int_S P_{r,s}(x,\mathrm dy)P_{s,t}(y,A),
\qquad r\le s\le t.
\tag{5}
$$

Tulis $\eta_t(A)=\int_S\eta(\mathrm dx)P_{0,t}(x,A)$. Untuk himpunan waktu
$J=\{t_1<\cdots<t_n\}$, definisikan hukum hingga melalui

$$
\begin{aligned}
&\mu_J(\mathrm dx_1\cdots\mathrm dx_n)\\
&\quad=\eta_{t_1}(\mathrm dx_1)
P_{t_1,t_2}(x_1,\mathrm dx_2)\cdots
P_{t_{n-1},t_n}(x_{n-1},\mathrm dx_n).
\end{aligned}
\tag{6}
$$

Secara lebih eksplisit, untuk persegi panjang
$A_1\times\cdots\times A_n$, ruas kanan (6) berarti integral berulang

$$
\int_{A_1}\eta_{t_1}(\mathrm dx_1)
\int_{A_2}P_{t_1,t_2}(x_1,\mathrm dx_2)\cdots
\int_{A_n}P_{t_{n-1},t_n}(x_{n-1},\mathrm dx_n).
$$

Keterukuran kernel memastikan bahwa setiap integral luar terdefinisi. Bentuk
ini lalu menentukan satu ukuran peluang pada sigma-aljabar produk hingga,
bukan hanya pada persegi panjang. Urutan waktu dipakai untuk memfaktorkan
hukum; indeks hukum itu sendiri tetap himpunan berlabel $J$, sehingga hasil
akhir tidak bergantung pada cara kita menuliskan daftar yang sama.

Menghapus koordinat terakhir berarti mengintegralkan
$P_{t_{n-1},t_n}(x_{n-1},\mathrm dx_n)$ atas seluruh $S$; hasilnya satu,
karena kernel tersebut merupakan ukuran peluang. Menghapus koordinat
interior $t_i$ menggabungkan dua kernel yang bersebelahan, dan (5) mengganti
integralnya dengan $P_{t_{i-1},t_{i+1}}$. Menghapus koordinat pertama memakai
$\eta_{t_1}P_{t_1,t_2}=\eta_{t_2}$. Penghapusan berulang menangani setiap
$K\subset J$, sehingga keluarga (6) konsisten secara proyektif.

Teorema perluasan kini menghasilkan hukum pada ruang mentah $S^T$ dan proses
koordinat dengan hukum-hukum (6). Kesimpulannya hanya itu. Untuk teori rantai
Markov waktu kontinu, generator, dan semigrup, lihat unit
[QuantEcon](../quantecon/lectures/markov_prop.html). Jika teori tersebut
memakai ruang lintasan kontinu kanan yang lebih sempit, diperlukan argumen
tambahan untuk menunjukkan bahwa hukum mentah berkonsentrasi di sana atau
untuk membangun ukuran langsung pada ruang yang lebih sempit tersebut.

:::

::: {#contoh-keluarga-gaussian .bridge-section}

## Contoh keluarga Gaussian

Ambil $S=\mathbb R$ dengan sigma-aljabar Borel. Misalkan
$m:T\to\mathbb R$ dan $K:T\times T\to\mathbb R$ memenuhi
$K(s,t)=K(t,s)$ serta bersifat semidefinit positif: untuk setiap
$t_1,\ldots,t_n\in T$ dan $a_1,\ldots,a_n\in\mathbb R$,

$$
\sum_{i=1}^n\sum_{j=1}^n a_i a_jK(t_i,t_j)\ge0.
\tag{7}
$$

Untuk $J=\{t_1,\ldots,t_n\}$, tetapkan $m_J=(m(t_i))_{i=1}^n$ dan
$K_J=(K(t_i,t_j))_{i,j=1}^n$. Ada hukum Gaussian multivariat
$\mu_J=\mathcal N(m_J,K_J)$, termasuk ketika $K_J$ singular. Sebagai contoh,
hukum singular dapat dipahami melalui fungsi karakteristik

$$
u\longmapsto
\exp\!\left(iu^\mathsf Tm_J-\tfrac12u^\mathsf TK_Ju\right),
$$

yang tetap sah untuk matriks kovarians semidefinit positif.

Singularitas berarti sebagian kombinasi linear koordinat mempunyai varians
nol dan karena itu memenuhi hubungan deterministik di bawah hukum tersebut.
Hal ini tidak merusak ukuran peluang: ukuran Gaussian hanya terkonsentrasi
pada subruang afin yang dimensinya lebih kecil. Karena proyeksi linear dari
Gaussian—singular ataupun tak singular—tetap Gaussian, pengambilan marginal
tidak memerlukan invers matriks kovarians ataupun kepadatan terhadap ukuran
Lebesgue. Inilah alasan formulasi semidefinit positif, bukan definit positif,
merupakan formulasi yang tepat bagi keluarga hingga.

Marginal sebuah vektor Gaussian pada subhimpunan koordinat tetap Gaussian;
vektor rataan dan matriks kovariansnya menjadi subvektor dan submatriks yang
bersesuaian. Maka untuk $K_0\subset J$ berlaku
$\mu_J\circ p_{J,K_0}^{-1}=\mu_{K_0}$. Teorema Kolmogorov menghasilkan proses
Gaussian kanonik dengan fungsi rataan $m$ dan fungsi kovarians $K$.
Pemilihan $K(s,t)=\min(s,t)$ terkait dengan pembahasan
[gerak Brown standar](../brown/Standard.html), tetapi konstruksi di
sini sendiri tidak membuktikan lintasan kontinu, sifat Markov, atau sifat
lintasan Brown lainnya.

:::

::: {#audit-hipotesis-dan-bukan-klaim .bridge-section}

## Audit hipotesis dan bukan klaim

Empat batas berikut mencegah teorema perluasan dipakai melampaui isinya.

1. **Borel standar adalah hipotesis cukup yang dinyatakan.** Kita tidak
   mengasumsikan bahwa keluarga konsisten pada ruang terukur sebarang selalu
   dapat diperluas. Ada versi teorema dengan hipotesis lain, tetapi versi
   itulah yang harus dinyatakan dan dibuktikan jika hendak dipakai.
2. **Ukuran hidup pada sigma-aljabar produk.** Untuk $T$ tak terhitung,
   $\mathcal S^{\otimes T}$ dapat lebih kecil daripada sigma-aljabar lain yang
   muncul dari suatu topologi pada $S^T$, apalagi daripada himpunan semua
   bagiannya. Keunikan pada silinder tidak menentukan nilai kejadian di luar
   $\mathcal S^{\otimes T}$.
3. **Ruang lintasan mentah bukan ruang lintasan teratur.** Konstruksi pada
   $S^T$ tidak dengan sendirinya memberi ukuran pada $C(T,S)$, $D(T,S)$,
   atau kelas lintasan kontinu kanan. Untuk berpindah ke kelas tersebut perlu
   dibuktikan keterukuran kelasnya dan konsentrasi ukuran, atau digunakan
   teorema konstruksi lain. Hukum berdimensi hingga saja tidak menyertakan
   keteraturan lintasan.
4. **Keterukuran setiap koordinat bukan keterukuran bersama.** Kita telah
   membuktikan bahwa $\omega\mapsto X_t(\omega)$ terukur untuk setiap $t$
   tetap. Itu tidak otomatis membuktikan bahwa
   $(t,\omega)\mapsto X_t(\omega)$ terukur terhadap sigma-aljabar produk pada
   $T\times\Omega$. Keterukuran bersama, modifikasi proses, dan ekuivalensi
   lintasan memerlukan pembahasan penghubung tersendiri.

Dengan batas-batas ini, perluasan Kolmogorov melakukan satu pekerjaan yang
sangat kuat tetapi spesifik: mengubah hukum berdimensi hingga yang konsisten
menjadi satu hukum pada ruang koordinat mentah, lalu menyediakan realisasi
kanonik melalui proyeksi koordinat.

Karena itu, setiap penerapan sebaiknya meninggalkan jejak audit yang menyebut
ruang keadaan, sigma-aljabar hasil, keluarga marginal, dan teorema tambahan
apa pun yang dipakai untuk keteraturan lintasan. Menuliskan keempat unsur itu
mencegah kesimpulan sah tentang hukum koordinat berubah tanpa disadari
menjadi klaim yang lebih kuat tentang geometri lintasan.

:::

::: {#latihan-penguasaan .bridge-section}

## Latihan penguasaan

::: {#unit.o009.original.mastery.process-construction.01 .mastery-sequence}

::: {#unit.o009.original.mastery.process-construction.01.exercise .exercise}
### Latihan 1 — satu silinder, dua representasi

Misalkan $J,K\subset T$ hingga,
$A\in\mathcal S^{\otimes J}$, $B\in\mathcal S^{\otimes K}$, dan
$\pi_J^{-1}(A)=\pi_K^{-1}(B)$.

1. Dengan $L=J\cup K$, buktikan bahwa
   $p_{L,J}^{-1}(A)=p_{L,K}^{-1}(B)$ di $S^L$.
2. Buktikan bahwa penetapan peluang silinder tidak bergantung pada
   representasinya, yaitu $\mu_J(A)=\mu_K(B)$.
3. Gunakan bentuk silinder untuk membuktikan bahwa setiap koordinat
   $X_t(\omega)=\omega(t)$ terukur pada $\mathcal F^0$.
:::

::: {#unit.o009.original.mastery.process-construction.01.hint.01 .hint}
**Petunjuk 1.** Pindahkan kedua representasi ke ruang koordinat bersama
$S^L$. Untuk membandingkan keanggotaan titik $x\in S^L$, perpanjang $x$
menjadi sebuah lintasan $\omega\in S^T$.
:::

::: {#unit.o009.original.mastery.process-construction.01.hint.02 .hint}
**Petunjuk 2.** Setelah kedua himpunan terangkat terbukti sama, terapkan
konsistensi proyektif sekali dari $L$ ke $J$ dan sekali dari $L$ ke $K$.
Untuk keterukuran koordinat, hitung prabayangan $X_t^{-1}(D)$ bagi
$D\in\mathcal S$.
:::

::: {#unit.o009.original.mastery.process-construction.01.answer .answer}
**Jawaban ringkas.** Kedua himpunan yang diangkat ke $S^L$ sama, sehingga

$$
\mu_J(A)=\mu_L(p_{L,J}^{-1}A)
=\mu_L(p_{L,K}^{-1}B)=\mu_K(B).
$$

Selain itu, $X_t^{-1}(D)=\pi_{\{t\}}^{-1}(D)$ adalah silinder dan karena itu
berada dalam $\mathcal F^0$.
:::

::: {#unit.o009.original.mastery.process-construction.01.solution .solution}
**Penyelesaian lengkap.** Pilih $s_0\in S$. Untuk $x\in S^L$, definisikan
$\omega_x\in S^T$ dengan $\omega_x|_L=x$ dan
$\omega_x(t)=s_0$ di luar $L$. Karena kedua silinder pada soal sama,

$$
\begin{aligned}
x\in p_{L,J}^{-1}(A)
&\iff \pi_J(\omega_x)\in A\\
&\iff \omega_x\in\pi_J^{-1}(A)\\
&\iff \omega_x\in\pi_K^{-1}(B)\\
&\iff \pi_K(\omega_x)\in B\\
&\iff x\in p_{L,K}^{-1}(B).
\end{aligned}
$$

Kesetaraan berlaku untuk setiap $x$, jadi kedua himpunan terangkat sama.
Konsistensi proyektif memberikan

$$
\mu_J(A)=\mu_L(p_{L,J}^{-1}A)
=\mu_L(p_{L,K}^{-1}B)=\mu_K(B).
$$

Dengan demikian peluang silinder terdefinisi baik, meskipun satu silinder
ditulis memakai dua himpunan koordinat berbeda. Terakhir, bagi
$D\in\mathcal S$,

$$
X_t^{-1}(D)
=\{\omega:\omega(t)\in D\}
=\pi_{\{t\}}^{-1}(D)\in\mathcal F^0.
$$

Karena ini berlaku untuk setiap $D\in\mathcal S$, peta $X_t$ terukur.
:::

:::

::: {#unit.o009.original.mastery.process-construction.02 .mastery-sequence}

::: {#unit.o009.original.mastery.process-construction.02.exercise .exercise}
### Latihan 2 — konsistensi hukum Markov

Misalkan $S=\{0,1\}$, $\eta$ suatu hukum awal, dan rantai Markov homogen
mempunyai matriks transisi

$$
P=\begin{pmatrix}3/4&1/4\\[2pt]1/2&1/2\end{pmatrix}.
$$

1. Tuliskan hukum bersama tiga waktu $(X_0,X_1,X_2)$.
2. Jumlahkan keadaan interior $X_1$ dan tunjukkan bahwa marginal
   $(X_0,X_2)$ memakai matriks dua-langkah $P^2$.
3. Periksa dengan aritmetika rasional nilai $P^2$, jelaskan penghapusan
   koordinat ujung, lalu simpulkan konsistensi semua hukum waktu hingga dan
   terapkan teorema perluasan Kolmogorov.
:::

::: {#unit.o009.original.mastery.process-construction.02.hint.01 .hint}
**Petunjuk 1.** Untuk $i,j,k\in S$, hukum tiga waktunya adalah
$\eta_iP_{ij}P_{jk}$. Ketika $j$ dijumlahkan, pisahkan dua faktor kernel yang
bersebelahan.
:::

::: {#unit.o009.original.mastery.process-construction.02.hint.02 .hint}
**Petunjuk 2.** Gunakan hukum komposisi
$\sum_jP_{ij}P_{jk}=(P^2)_{ik}$. Menghapus koordinat terakhir memakai jumlah
baris satu, sedangkan penghapusan berulang menangani subhimpunan waktu
sebarang.
:::

::: {#unit.o009.original.mastery.process-construction.02.answer .answer}
**Jawaban ringkas.** Hukum tiga waktunya
$\mu_{\{0,1,2\}}(i,j,k)=\eta_iP_{ij}P_{jk}$. Chapman–Kolmogorov tepat memberi
identitas marginal yang hilang, dan

$$
P^2=\begin{pmatrix}11/16&5/16\\[2pt]5/8&3/8\end{pmatrix}.
$$

Karena setiap penghapusan koordinat mempertahankan hukum yang ditentukan,
keluarganya konsisten dan menghasilkan hukum kanonik pada $S^{\mathbb N_0}$.
:::

::: {#unit.o009.original.mastery.process-construction.02.solution .solution}
**Penyelesaian lengkap.** Dengan menulis
$\eta_i=\eta(\{i\})$ dan $P_{ij}=P(i,\{j\})$, sifat Markov memberi

$$
\mathbb P(X_0=i,X_1=j,X_2=k)=\eta_iP_{ij}P_{jk}.
$$

Jika koordinat interior dijumlahkan, diperoleh

$$
\sum_{j\in S}\eta_iP_{ij}P_{jk}
=\eta_i\sum_{j\in S}P_{ij}P_{jk}
=\eta_i(P^2)_{ik}.
$$

Jadi hukum marginal $(X_0,X_2)$ memakai kernel dua-langkah; identitas ini
persis hukum Chapman–Kolmogorov. Perhitungan rasional menghasilkan

$$
\begin{aligned}
(P^2)_{00}&=\frac34\frac34+\frac14\frac12
=\frac9{16}+\frac2{16}=\frac{11}{16},\\
(P^2)_{01}&=\frac34\frac14+\frac14\frac12
=\frac3{16}+\frac2{16}=\frac5{16},\\
(P^2)_{10}&=\frac12\frac34+\frac12\frac12
=\frac38+\frac14=\frac58,\\
(P^2)_{11}&=\frac12\frac14+\frac12\frac12
=\frac18+\frac14=\frac38.
\end{aligned}
$$

Maka, tepat seperti yang harus diperiksa,

$$
P^2=
\begin{pmatrix}
11/16&5/16\\[2pt]
5/8&3/8
\end{pmatrix}.
$$

Menghapus $X_2$ dari hukum tiga waktu memberi

$$
\sum_k\eta_iP_{ij}P_{jk}
=\eta_iP_{ij}\sum_kP_{jk}
=\eta_iP_{ij},
$$

karena setiap baris $P$ berjumlah satu. Menghapus $X_0$ memberi
$\sum_i\eta_iP_{ij}P_{jk}=(\eta P)_jP_{jk}$, yaitu hukum dua waktu dengan
distribusi awal pada waktu $1$. Untuk kumpulan waktu yang lebih panjang,
koordinat ujung dihapus dengan normalisasi kernel, sedangkan koordinat
interior dihapus dengan komposisi kernel. Penghapusan berulang membuktikan
konsistensi untuk setiap pasangan himpunan waktu hingga $K\subset J$.

Ruang keadaan hingga adalah Borel standar. Karena itu, teorema perluasan
Kolmogorov memberikan ukuran peluang unik pada
$(S^{\mathbb N_0},\mathcal S^{\otimes\mathbb N_0})$ dengan semua hukum hingga
tersebut. Proyeksi koordinat di ruang ini membentuk rantai Markov kanonik.
Penerapan teorema ini belum menambahkan struktur lintasan apa pun di luar
koordinat diskret tersebut.
:::

:::

::: {#unit.o009.original.mastery.process-construction.03 .mastery-sequence}

::: {#unit.o009.original.mastery.process-construction.03.exercise .exercise}
### Latihan 3 — keluarga Gaussian kanonik

Untuk $T\subset\mathbb R$, definisikan

$$
K(s,t)=1+st.
$$

1. Buktikan bahwa $K$ simetris dan semidefinit positif.
2. Untuk setiap $J=\{t_1,\ldots,t_n\}\subset T$ yang hingga, definisikan
   hukum Gaussian berataan nol dan berkovarians
   $K_J=(1+t_it_j)_{i,j}$. Buktikan keluarga hukum ini konsisten, termasuk
   saat $K_J$ singular.
3. Terapkan teorema perluasan Kolmogorov dan nyatakan dengan tepat apa yang
   dapat—dan tidak dapat—disimpulkan tentang proses kanoniknya.
:::

::: {#unit.o009.original.mastery.process-construction.03.hint.01 .hint}
**Petunjuk 1.** Untuk skalar $a_1,\ldots,a_n$, tulis ulang bentuk kuadratnya
sebagai

$$
\left(\sum_i a_i\right)^2
+\left(\sum_i a_it_i\right)^2.
$$
:::

::: {#unit.o009.original.mastery.process-construction.03.hint.02 .hint}
**Petunjuk 2.** Marginal dari Gaussian multivariat diperoleh dengan mengambil
subvektor rataan dan submatriks kovarians. Fakta ini tetap berlaku untuk
Gaussian singular; gunakan fungsi karakteristik jika diperlukan.
:::

::: {#unit.o009.original.mastery.process-construction.03.answer .answer}
**Jawaban ringkas.** Identitas bentuk kuadrat menunjukkan bahwa $K$ positif
semidefinit. Marginal Gaussian pada koordinat $K_0\subset J$ mempunyai
kovarians $(1+st)_{s,t\in K_0}$, sehingga keluarga konsisten. Teorema
Kolmogorov menghasilkan proses koordinat Gaussian kanonik berataan nol dan
berkovarians $K$ pada sigma-aljabar produk; tahap ini tidak menyimpulkan
kontinuitas atau keteraturan lintasan lainnya.
:::

::: {#unit.o009.original.mastery.process-construction.03.solution .solution}
**Penyelesaian lengkap.** Simetri langsung mengikuti
$1+st=1+ts$. Untuk $t_1,\ldots,t_n\in T$ dan
$a_1,\ldots,a_n\in\mathbb R$,

$$
\begin{aligned}
\sum_{i,j=1}^na_ia_jK(t_i,t_j)
&=\sum_{i,j=1}^na_ia_j(1+t_it_j)\\
&=\left(\sum_{i=1}^na_i\right)^2
+\left(\sum_{i=1}^na_it_i\right)^2
\ge0.
\end{aligned}
$$

Jadi setiap matriks $K_J=(1+t_it_j)_{i,j}$ simetris dan semidefinit positif.
Karena itu terdapat hukum Gaussian multivariat
$\mu_J=\mathcal N(0,K_J)$. Matriks ini dapat singular—misalnya, untuk banyak
titik peringkatnya tidak melebihi dua—tetapi singularitas tidak menggagalkan
keberadaan ukuran Gaussian. Fungsi karakteristiknya tetap

$$
\varphi_J(u)=\exp\!\left(-\tfrac12u^\mathsf TK_Ju\right).
$$

Ambil $K_0\subset J$ dan proyeksikan vektor ke koordinat dalam $K_0$.
Fungsi karakteristik marginal diperoleh dengan memberi nilai nol pada
komponen $u$ di luar $K_0$. Hasilnya

$$
u_0\longmapsto
\exp\!\left(-\tfrac12u_0^\mathsf TK_{K_0}u_0\right),
$$

yang merupakan fungsi karakteristik $\mathcal N(0,K_{K_0})$. Maka
$\mu_J\circ p_{J,K_0}^{-1}=\mu_{K_0}$ bahkan ketika kovariansnya singular.

Karena $\mathbb R$ dengan sigma-aljabar Borel adalah ruang Borel standar,
teorema perluasan memberikan ukuran unik pada
$(\mathbb R^T,\mathcal B(\mathbb R)^{\otimes T})$. Proses koordinat
$X_t(\omega)=\omega(t)$ di bawah ukuran itu adalah Gaussian, berataan nol,
dan memenuhi

$$
\operatorname{Cov}(X_s,X_t)=1+st.
$$

Konstruksi ini menetapkan semua hukum berdimensi hingga. Konstruksi ini saja
tidak membuktikan bahwa lintasan $t\mapsto X_t(\omega)$ kontinu, kontinu
kanan, terukur bersama, atau memiliki keteraturan lain. Setiap klaim semacam
itu memerlukan argumen tambahan di luar teorema perluasan yang dipakai di
sini.
:::

:::

:::

::: {#hak-dan-provenans .bridge-section}

## Hak dan provenans

Seluruh unit asli ini—termasuk uraian, teorema sebagaimana dirumuskan di sini,
tiga latihan, enam petunjuk progresif, tiga jawaban ringkas, dan tiga
penyelesaian lengkap—dilepas dengan lisensi
[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
di bawah pengenal hak
`rights.o009.original.bridge.kolmogorov.cc-by-4.0`.

Unit ini ditulis sebagai jembatan mandiri untuk menghubungkan materi Random
tentang [ruang produk](../prob/Probability2.html) dan
[distribusi berdimensi hingga](../prob/Processes.html) dengan materi
QuantEcon tentang [proses Markov waktu
kontinu](../quantecon/lectures/markov_prop.html). Teksnya bukan bagian dari
sumber-sumber donor tersebut dan tidak mengubah lisensi apa pun yang berlaku
pada sumber donor. Catatan audit mengenai hipotesis ruang keadaan, lingkup
langkah keberadaan, dan perbedaan antara ruang lintasan mentah dan kelas
lintasan kontinu kanan merupakan koreksi hilir; byte sumber donor tetap
dipertahankan tanpa perubahan.

Pengungkapan produksi: **OpenAI Codex gpt-5.6-sol, Ultra.** Materi ini dibuat
atas arahan pengguna. Random dan QuantEcon tidak mendukung, mengesahkan, atau
mensponsori unit ini; penyebutan dan pranala hanya menyatakan hubungan
kurikuler serta provenans intelektual yang relevan.

:::

:::
