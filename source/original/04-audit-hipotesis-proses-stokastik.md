---
title: "Audit hipotesis untuk proses stokastik"
lang: id-ID
author:
  - "Codex (penulisan materi asli atas arahan pengguna)"
authoring:
  course_id: "o009"
  unit_id: "unit.o009.original.bridge.hypothesis-audits"
  target_locale: "id-ID"
  source_type: "original"
  rights_id: "rights.o009.original.bridge.hypothesis-audits.cc-by-4.0"
  license: "CC-BY-4.0"
  model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."
---

::: {#unit.o009.original.bridge.hypothesis-audits .original-bridge}

# Audit hipotesis untuk proses stokastik

::: {#tujuan-dan-protokol-audit-hipotesis .bridge-section}

## Tujuan dan protokol audit hipotesis

Sebuah teorema proses stokastik sering tampak pendek karena banyak syaratnya
sudah ditetapkan beberapa halaman sebelumnya. Ketika teorema itu dikutip di
tempat lain, syarat lokal tersebut mudah hilang. Akibatnya, pernyataan yang
benar pada ruang keadaan berhingga dapat terdengar seolah-olah berlaku pada ruang
keadaan umum; kesamaan hampir pasti dapat terbaca sebagai kesamaan pada setiap
titik; atau konvergensi distribusi berdimensi
hingga (FDD) dapat disalahartikan
sebagai konvergensi hukum lintasan.

Unit ini tidak menyebut setiap penyederhanaan sebagai kesalahan. Ia juga tidak
mengubah byte sumber yang telah dibekukan. Tujuannya ialah memberi pembaca
protokol untuk memulihkan ruang lingkup sebuah klaim. Setiap kalimat berlabel
**klaim uji** di bawah ini sengaja dibuat terlalu luas untuk keperluan audit;
kalimat itu bukan kutipan dari Random Services, QuantEcon, atau sumber lain.
Tautan ke unit sumber menunjukkan konteks matematika yang harus dibaca, bukan
tuduhan bahwa penulis sumber membuat klaim uji tersebut.

Sebelum memakai sebuah hasil, tulis lima kotak berikut.

| Kotak | Pertanyaan yang harus dijawab |
|---|---|
| **Objek** | Apakah yang dikuantifikasi berupa peubah acak, proses, kernel, semigrup, waktu henti, atau hukum pada ruang lintasan? |
| **Latar** | Apa ruang peluangnya, aljabar-σ dan filtrasinya, ruang keadaan beserta topologinya, himpunan waktu, serta ruang lintasannya? |
| **Hipotesis** | Di mana keterintegralan, kendali ekor, independensi, Gaussianitas, sifat Borel standar, sifat hingga-σ, sifat konservatif, sifat tidak meledak, rekurensi, atau keteraturan lintasan dipakai? |
| **Kesimpulan** | Apakah hasilnya hampir pasti, dalam probabilitas, dalam distribusi, dalam $L^p$, untuk distribusi berdimensi hingga, atau untuk hukum lintasan dalam topologi tertentu? |
| **Saksi kegagalan** | Contoh apa yang gagal, atau langkah bukti mana yang tidak sah, jika satu hipotesis dihapus? |

Setelah lima kotak itu terisi, nyatakan **perbaikan yang dipakai di sini**:
sebuah syarat cukup yang bersih dan kesimpulan tepat yang dihasilkannya.
Perbaikan itu tidak perlu diklaim sebagai syarat paling lemah yang mungkin.
Ia harus cukup eksplisit sehingga pembaca dapat memeriksa setiap bagiannya.

Protokol ini melengkapi tiga jembatan sebelumnya. Jembatan
[konstruksi Kolmogorov](01-konstruksi-kolmogorov.html) memisahkan keluarga
distribusi berdimensi hingga dari ukuran pada ruang produk. Jembatan
[keterukuran proses dan hukum lintasan](02-keterukuran-proses-dan-hukum-lintasan.html)
memisahkan keterukuran tiap waktu, keterukuran bersama, dan hukum pada ruang
lintasan teratur. Jembatan
[distribusi bersyarat reguler](03-probabilitas-bersyarat-reguler.html)
memisahkan versi per kejadian dari satu kernel yang koheren. Di sini ketiga
pemisahan itu dipakai sebagai kebiasaan membaca lintas topik.

:::

::: {#audit-konvergensi-dan-integrabilitas .bridge-section}

## Audit konvergensi dan keterintegralan

Unit [konvergensi peubah acak](../prob/Convergence.html) dan
[konvergensi distribusi](../dist/Convergence.html) memperkenalkan beberapa
mode konvergensi. Nama mode tersebut adalah bagian dari kesimpulan, bukan
hiasan yang boleh dihapus.

> **Klaim uji (bukan kutipan sumber).** Jika $X_n\to X$ hampir pasti dan
> $\sup_n\mathbb E|X_n|<\infty$, maka
> $\mathbb E[X_n]\to\mathbb E[X]$.

Klaim ini salah. Ambil satu peubah $U$ yang seragam pada $(0,1]$ dan tetapkan

$$
X_n=n\mathbf1_{\{U\le 1/n\}}.
$$

Untuk setiap $U>0$, indikator itu akhirnya nol, sehingga $X_n\to0$ hampir
pasti. Namun

$$
\mathbb E[X_n]
=n\mathbb P(U\le1/n)
=1
$$

untuk setiap $n$. Keterbatasan norma $L^1$ tidak sama dengan
**keterintegralan seragam**. Untuk $K>0$, pilih bilangan bulat $n>K$; maka

$$
\mathbb E\!\left[|X_n|\mathbf1_{\{|X_n|>K\}}\right]=1.
$$

Supremum ekor itu tidak menuju nol ketika $K\to\infty$.

Audit lima kotaknya ialah sebagai berikut.

- **Objek:** barisan peubah acak real terintegralkan.
- **Latar:** satu ruang probabilitas; semua $X_n$ dibangun dari $U$ yang sama.
- **Hipotesis yang hilang:** kendali ekor seragam, bukan sekadar
  $\sup_n\mathbb E|X_n|<\infty$.
- **Kesimpulan yang benar:** konvergensi hampir pasti menyiratkan konvergensi dalam
  probabilitas, tetapi tidak otomatis menyiratkan konvergensi $L^1$ atau
  konvergensi ekspektasi.
- **Saksi kegagalan:** seluruh massa harapan berpindah ke kejadian yang makin
  jarang sambil tingginya makin besar.

Satu perbaikan yang dapat langsung diperiksa adalah teorema Vitali:

> Jika $X_n\to X$ dalam probabilitas dan keluarga $(X_n)$ terintegralkan
> seragam, maka $X_n\to X$ dalam $L^1$. Karena itu
> $\mathbb E[X_n]\to\mathbb E[X]$.

Untuk peubah acak bernilai real, konvergensi dalam distribusi bersama
keterintegralan seragam keluarga $(|X_n|)_n$ juga cukup untuk memperoleh
$\mathbb E[X_n]\to\mathbb E[X]$. Tanpa syarat
ekor, konvergensi dalam distribusi hanya mengendalikan fungsi uji terbatas dan
kontinu. Fungsi $x\mapsto x$ tidak terbatas.

**Catatan lingkup pada saksi terpilih.** Paragraf penutup
[bagian konvergensi pada unit keterintegralan seragam](../expect/Uniform.html#con)
harus dibaca bersama premis pada kalimat tepat sebelumnya:
$X_n\to X$ dengan probabilitas satu, dan karena itu dalam probabilitas.
Keterintegralan seragam **sendiri** tidak menyiratkan
$X_n\to X$ dalam rataan; ia harus dipasangkan dengan konvergensi dalam
probabilitas seperti pada teorema `con2` di halaman yang sama. Catatan ini
memperjelas premis yang mudah terlepas ketika akibat tersebut dikutip.

Ikatan O006/C140 tetap berupa prasyarat eksternal untuk LLN, CLT, distribusi
sampling, dan inferensi. Unit ini tidak menyalin bab sampling atau membuktikan
ulang LLN/CLT; ia hanya mencatat bahwa kesimpulan limit selalu harus dibaca
bersama mode konvergensi dan syarat pertukaran limitnya.

:::

::: {#audit-pengondisian-dan-kernel .bridge-section}

## Audit pengondisian dan kernel

Unit [nilai harapan bersyarat](../expect/Conditional2.html),
[keterintegralan seragam bersyarat](../expect/Uniform.html), dan
[kernel](../expect/Kernels.html) memakai objek bersyarat pada tingkat yang
berbeda. Jembatan ketiga memberi syarat keberadaan dan disiplin versi bagi
[distribusi bersyarat reguler](03-probabilitas-bersyarat-reguler.html).

> **Klaim uji (bukan kutipan sumber).** Karena
> $\mathbb P(Y\in B\mid\mathcal G)$ ada untuk setiap $B$, nilai-nilai itu
> secara otomatis membentuk satu ukuran peluang dalam $B$ pada setiap
> $\omega$.

Klaim ini mencampur tiga tingkat. Untuk satu $B$ tetap,

$$
\mathbb P(Y\in B\mid\mathcal G)
=\mathbb E[\mathbf1_{\{Y\in B\}}\mid\mathcal G]
$$

adalah kelas fungsi yang sama hampir pasti. Himpunan nol tempat dua versi
berbeda boleh bergantung pada $B$. Jika versi dipilih terpisah bagi tak
terhitung banyak $B$, tidak ada alasan bahwa
$B\mapsto K(\omega,B)$ ternormalisasi dan aditif terhitung pada satu
$\omega$.

Perbaikannya memakai objek yang lebih kuat. Bila sasaran $Y$ merupakan ruang
Borel standar tak kosong, terdapat sebuah kernel probabilitas

$$
K:(\Omega,\mathcal G)\rightsquigarrow(T,\mathcal T)
$$

yang mewakili seluruh peluang bersyarat secara koheren. Dua kernel semacam itu
sama sebagai ukuran di luar satu himpunan nol bersama karena sasaran mempunyai
kelas penentu terhitung. Kesamaan itu tetap bukan kesamaan pada setiap titik.
Jika pengondisian ditulis sebagai $X=x$, ukuran yang mengendalikan kata
“hampir di mana-mana” adalah hukum marginal $\mathbb P_X$. Nilai kernel pada
titik dengan $\mathbb P_X(\{x\})=0$ merupakan pilihan versi kecuali struktur
tambahan—misalnya kontinuitas—memilih perpanjangan tertentu.

Ada pula syarat penyebut yang tidak boleh hilang. Rumus Bayes pada
[unit nilai harapan bersyarat](../expect/Conditional2.html#bay) mempunyai
penyebut

$$
\mathbb E[\mathbb P(B\mid\mathcal G)]=\mathbb P(B).
$$

Karena itu, rumus rasio tersebut menyatakan probabilitas bersyarat
$\mathbb P(A\mid B)$ hanya ketika $\mathbb P(B)>0$ menurut definisi rasio
yang dipakai halaman itu. Bila $\mathbb P(B)=0$, pembilang dan penyebut sama
nol dan rumus tidak memilih nilai kanonik. Syarat positif ini merupakan
perbaikan lingkup pada pernyataan `bay`; ia tidak mengubah byte sumber.

Audit yang aman sebelum memakai sebuah rumus bersyarat ialah:

1. pastikan peubah yang diambil nilai harapannya terintegralkan, atau nyatakan
   dengan jelas kasus nonnegatif bernilai diperluas;
2. sebutkan aljabar-σ pengondisi dan ukuran yang menentukan kesamaan hampir
   pasti;
3. bedakan satu fungsi bersyarat dari satu kernel peluang;
4. untuk keberadaan kernel, pasang hipotesis Borel standar pada sasaran yang
   benar;
5. ketika mengganti versi pada himpunan nol, ganti seluruh ukuran sekaligus,
   bukan setiap kejadian secara bebas.

Saksi kegagalan lengkap dan bukti perbaikannya sudah diberikan dalam
jembatan ketiga. Unit ini tidak mengulang bukti tersebut; ia membuat
hipotesisnya terlihat ketika hasil bersyarat dipakai di topik lain.

:::

::: {#audit-martingal-dan-waktu-henti .bridge-section}

## Audit martingal dan waktu henti

Unit [martingal yang dihentikan](../martingales/Stop.html) dan
[konvergensi martingal](../martingales/Convergence.html) harus dibaca dengan
kuantor waktu dan syarat ekornya. Adaptasi dan keterintegralan pada setiap
waktu deterministik tidak sendiri mengendalikan peubah pada satu waktu acak
yang tak terbatas.

> **Klaim uji (bukan kutipan sumber).** Jika $(M_n)$ martingal terintegralkan
> dan $\tau<\infty$ hampir pasti merupakan waktu henti, maka
> $\mathbb E[M_\tau]=\mathbb E[M_0]$.

Ambil gerak acak simetris sederhana

$$
S_n=\xi_1+\cdots+\xi_n,
\qquad
\mathbb P(\xi_k=1)=\mathbb P(\xi_k=-1)=\tfrac12,
$$

dan $\tau=\inf\{n\ge0:S_n=1\}$. Waktu $\tau$ berhingga hampir pasti, tetapi
$\mathbb E\tau=\infty$. Untuk setiap $N$, waktu $\tau\wedge N$ terbatas dan

$$
\mathbb E[S_{\tau\wedge N}]=0.
$$

Di sisi lain, $S_{\tau\wedge N}\to S_\tau=1$ hampir pasti. Pertukaran limit
dan ekspektasi gagal karena keluarga
$(S_{\tau\wedge N})_N$ tidak terintegralkan seragam.

Kotak audit yang sering hilang ialah:

- apakah $\tau$ terbatas, hanya berhingga hampir pasti, atau juga terintegralkan;
- apakah keluarga martingal yang dihentikan terintegralkan seragam;
- apakah inkremennya dibatasi, dan teorema versi mana yang memakai batas itu;
- apakah kesimpulannya kesamaan, ketaksamaan supermartingal, atau hanya hasil
  bagi $\tau\wedge N$.

Beberapa jalur aman harus dinyatakan terpisah. Penghentian opsional berlaku
untuk waktu henti terbatas. Ia juga berlaku ketika keluarga
$(M_{\tau\wedge n})_n$ terintegralkan seragam dan limit yang dimaksud telah
diidentifikasi. Untuk martingal dengan inkremen dibatasi oleh konstanta,
$\mathbb E\tau<\infty$ memberi dominasi terintegralkan yang cukup. Kalimat
“syarat penghentian opsional terpenuhi” tidak memadai tanpa menyebut jalur
mana yang telah diperiksa.

**Catatan lingkup pada saksi terpilih.** Paragraf penjudi pada
[unit martingal yang dihentikan](../martingales/Stop.html#stp3) langsung
diikuti kesimpulan yang benar bagi $X_{t\wedge\tau}$ pada waktu deterministik
$t$. Retorika “tidak ada waktu henti yang dapat membantu” tidak boleh
dipisahkan dari pemotongan itu lalu digunakan untuk $X_\tau$ pada waktu tak
terbatas. Bagian waktu diskret halaman tersebut kemudian memang menyatakan
syarat-syarat tambahan. Koreksi hilir
`correction.o009.random.martingales.stop.optional-stopping-missing-variables`
juga telah memulihkan nama peubah yang hilang pada satu pernyataan sumber;
unit ini menautkannya dan tidak membuka ulang koreksi tersebut.

:::

::: {#audit-markov-dan-ctmc .bridge-section}

## Audit rantai Markov waktu diskret dan waktu kontinu (CTMC)

Unit [perilaku limit rantai diskret](../markov/Limiting.html) membahas konteks
rantai Markov waktu diskret. Komponen QuantEcon membahas
[generator](../quantecon/lectures/generators.html) dan
[ergodisitas CTMC](../quantecon/lectures/ergodicity.html) dalam konteksnya
sendiri. Pernyataan dari kedua konteks itu tidak boleh disatukan hanya karena
keduanya memakai kata *Markov*.

> **Klaim uji (bukan kutipan sumber).** Setiap rantai Markov tak tereduksi
> mempunyai distribusi stasioner tunggal dan konvergen menuju distribusi itu.

Matriks transisi dua keadaan

$$
P=
\begin{pmatrix}
0&1\\
1&0
\end{pmatrix}
$$

memberi saksi kegagalan langsung. Rantai ini berhingga dan tak tereduksi, serta
mempunyai distribusi stasioner tunggal $(1/2,1/2)$. Namun dari keadaan nol,
hukumnya berganti-ganti antara $\delta_0$ dan $\delta_1$; tidak ada konvergensi
waktu biasa. Untuk saksi berhingga ini, hipotesis yang hilang bagi konvergensi
waktu biasa ialah aperiodisitas. Pada rantai Markov berhingga,
tak tereduksi dan aperiodik memberi konvergensi menuju distribusi stasioner
tunggal. Pada ruang keadaan terhitung atau umum, rekurensi positif,
sifat tak tereduksi dalam arti yang sesuai, dan syarat Harris atau hanyutan dapat
menjadi isu terpisah. Kesimpulan untuk ruang keadaan berhingga tidak boleh diekspor tanpa teorema
baru.

Untuk CTMC, auditnya mempunyai lapisan tambahan.

1. **Ruang keadaan dan ruang operator.** Pada ruang keadaan berhingga, sebuah
   matriks intensitas dengan entri luar diagonal tak negatif dan jumlah baris
   nol memberi semigrup Markov melalui $e^{tQ}$. Pada dimensi tak hingga,
   domain operator dan
   topologi normanya harus disebut.
2. **Sifat konservatif dan sifat tidak meledak.** Persamaan formal untuk $Q$ tidak
   otomatis menjamin bahwa seluruh massa tetap satu bagi setiap $t$.
3. **Keunikan.** Persamaan maju atau mundur perlu dibaca bersama kelas solusi
   tempat keunikan dibuktikan.
4. **Limit.** Keberadaan distribusi stasioner, keunikannya, dan konvergensi
   menuju distribusi itu adalah tiga klaim berbeda.

Karena itu, frasa “generator menentukan proses” harus selalu dilengkapi ruang
operator, domain, dan kondisi tidak meledak atau teorema semigrup yang dipakai.
Komponen QuantEcon tetap dibaca dalam latar yang dinyatakannya; unit ini tidak
mengubahnya menjadi teorema ruang-keadaan umum.

Pada bagian
[ketunggalan distribusi stasioner](../quantecon/lectures/ergodicity.html#uniirr),
teorema formal menyatakan hasil yang tepat: sifat tak tereduksi memberi **paling
banyak satu** distribusi stasioner. Kalimat pengantar yang mengatakan bahwa
sifat tak tereduksi “menghasilkan ketunggalan” harus dibaca sebagai keunikan bila
sebuah distribusi stasioner ada, bukan sebagai teorema keberadaan. Keberadaan
dan kestabilan asimtotik memerlukan hasil lain pada bagian itu.

Dua masalah versi pada kernel transisi keadaan nol sudah diperbaiki di lapisan pembaca
oleh
`correction.o009.random.markov.general.homogeneity-consistent-transition-kernels`
dan
`correction.o009.random.markov.general.transition-kernel-version-scope`.
Audit baru ini mempertahankan hubungan ke kedua catatan tersebut dan tidak
mengulang perbaikannya.

:::

::: {#audit-poisson-dan-konstruksi-proses .bridge-section}

## Audit objek Poisson dan konstruksi proses

Unit [objek Poisson pada ruang umum](../poisson/General.html) dan kuliah
QuantEcon tentang [proses Poisson](../quantecon/lectures/poisson.html)
memakai kata *Poisson* untuk objek yang berkaitan tetapi tidak identik.

> **Klaim uji (bukan kutipan sumber).** Jika $N(A)$ berdistribusi Poisson
> dengan parameter $\mu(A)$ dan keluarga hitungan pada setiap koleksi himpunan
> saling lepas bersifat independen, maka $(N(A))_A$ otomatis merupakan ukuran
> acak yang bernilai hingga pada setiap himpunan terukur.

Pertama, peubah acak berdistribusi Poisson biasa bernilai hingga hanya ketika
$\mu(A)<\infty$. Jika $\mu(A)=\infty$, tidak ada peubah acak Poisson bernilai
hingga dengan “parameter tak hingga”. Kedua,
rumus satu himpunan dan independensi harus kompatibel dengan gabungan lepas:

$$
N\!\left(\bigsqcup_{j=1}^{\infty}A_j\right)
=\sum_{j=1}^{\infty}N(A_j)
$$

dalam arti ukuran acak. Ketiga, **hingga secara lokal** hanya bermakna setelah
kelas himpunan lokal dan topologi ditentukan; ia mengikuti dari intensitas
yang hingga pada kelas lokal tersebut, bukan dari kata Poisson saja.

Audit objeknya membedakan:

- satu peubah dengan hukum Poisson;
- proses penghitungan satu parameter dengan inkremen stasioner dan independen;
- ukuran acak Poisson pada ruang terukur dengan ukuran intensitas;
- proses bertanda atau integral terhadap ukuran acak, yang memerlukan syarat
  keterukuran dan keterintegralan tambahan.

Pada keluarga indeks umum, konsistensi distribusi berdimensi hingga belum
merupakan konstruksi lintasan. Teorema perluasan pada
[jembatan Kolmogorov](01-konstruksi-kolmogorov.html) membutuhkan keluarga yang
konsisten dan menghasilkan ukuran pada sigma-aljabar produk. Jika kemudian
diperlukan aditivitas sebagai ukuran acak atau keteraturan lintasan, sifat itu
harus dibuktikan pada versi yang dipilih. Unit ini tidak menarik kembali
halaman Poisson biasa Random yang telah digantikan oleh komponen CTMC yang
koheren.

Dua saksi terpilih perlu dibaca dengan kualifikasi eksplisit.

1. Kalimat
   [“yang benar-benar diperlukan hanyalah suatu ruang ukuran”](../poisson/General.html#pro)
   memberi kerangka definisi setelah ukuran acak $N$ diasumsikan ada; ia bukan
   teorema keberadaan atau jaminan keterhinggaan lokal. Untuk konstruksi
   standar, ambil $\mu$ hingga-σ, misalnya
   $S=\bigcup_n S_n$ dengan $\mu(S_n)<\infty$; keterhinggaan lokal memerlukan
   $\mu(A)<\infty$ pada kelas himpunan lokal yang dinyatakan. Halaman tersebut sendiri secara
   eksplisit memasang $N(A)=\infty$ ketika $\mu(A)=\infty$, jadi ia tidak
   boleh diparafrasekan sebagai klaim bahwa semua hitungan hingga.
2. Teorema
   [karakterisasi proses Poisson](../quantecon/lectures/poisson.html#keunikan)
   didahului kalimat yang menanyakan proses penghitungan lain, tetapi kotak
   teoremanya sendiri hanya menyatakan bahwa proses “didukung pada
   $\mathbb Z_+$ dan dimulai dari 0, serta inkremennya stasioner dan
   independen”. Syarat tertulis itu belum cukup: jika $N$ proses Poisson, maka
   $M_t=2N_t$ adalah contoh tandingan; proses nol juga menolak kesimpulan
   $\lambda>0$. Satu perbaikan bersih ialah mengasumsikan secara eksplisit
   proses penghitungan sederhana yang kontinu stokastik, càdlàg, dan hanya
   mempunyai berhingga banyak lompatan pada setiap selang waktu terbatas.
   Hasilnya proses Poisson dengan laju $\lambda\ge0$; kesimpulan $\lambda>0$
   memerlukan syarat nontrivialitas.

Catatan untuk hukum bersyarat pada himpunan berukuran hingga dan untuk
inkremen Poisson tak homogen juga sudah berada dalam lapisan koreksi hilir,
yakni
`correction.o009.random.poisson.general.poisson-general-single-point-finite-measure`,
`correction.o009.random.poisson.general.poisson-general-binomial-finite-measure`,
`correction.o009.random.poisson.general.poisson-general-multinomial-finite-measure`,
dan
`correction.o009.random.poisson.general.nonhomogeneous-independent-increments`.
Unit ini tidak mengubah atau menghitung ulang hasil yang telah diperbaiki itu.

:::

::: {#audit-brown-dan-hukum-lintasan .bridge-section}

## Audit gerak Brown dan hukum lintasan

Unit [gerak Brown standar](../brown/Standard.html) menyatukan hukum Gaussian,
inkremen, dan kontinuitas. Ketiga lapisan itu harus dipisahkan ketika sebuah
argumen hanya mengendalikan distribusi berdimensi hingga.

> **Klaim uji (bukan kutipan sumber).** Jika semua distribusi berdimensi
> hingga $X_n$ konvergen ke distribusi berdimensi hingga proses kontinu $X$,
> maka $X_n\Rightarrow X$ pada $C[0,1]$.

Ambil $U\sim\operatorname{Unif}[0,1]$ dan, untuk $t\in[0,1]$, definisikan

$$
Z_n(t)=\bigl(1-n|t-U|\bigr)_+.
$$

Setiap lintasan $Z_n$ kontinu. Untuk waktu tetap $t_1,\ldots,t_k$,

$$
\mathbb P\!\left(\max_{1\le j\le k}Z_n(t_j)>0\right)
\le \sum_{j=1}^k\mathbb P(|U-t_j|<1/n)
\le \frac{2k}{n}.
$$

Jadi seluruh distribusi berdimensi hingga konvergen ke proses nol. Namun

$$
\|Z_n\|_\infty=1
$$

hampir pasti untuk setiap $n$. Karena norma supremum kontinu pada $C[0,1]$,
konvergensi lemah $Z_n\Rightarrow0$ di ruang itu mustahil. Yang hilang ialah
**keketatan** hukum lintasan. Bahkan, bila $n\ge2$ dan $1/n\le\delta$,
modulus kontinuitas
memenuhi

$$
w(Z_n,\delta)
=\sup_{|s-t|\le\delta}|Z_n(s)-Z_n(t)|
=1
$$

hampir pasti: dari puncak di $U$, bergerak sejauh $1/n$ ke salah satu sisi
yang masih berada dalam $[0,1]$.

Perbaikannya mempunyai dua gerbang. Pertama, buktikan keketatan hukum
$(X_n)$ pada $C[0,1]$ dan konvergensi distribusi berdimensi hingga menuju
proses kontinu $X$. Hukum Borel pada $C[0,1]$ ditentukan oleh evaluasi pada
himpunan waktu rapat terhitung, sehingga setiap limit subsekuensial yang ketat
harus mempunyai hukum $X$. Kedua, jika hasil itu dimasukkan ke fungsional
lintasan $F$, teorema pemetaan kontinu memerlukan

$$
\mathbb P(X\in D_F)=0,
$$

dengan $D_F$ himpunan titik diskontinuitas $F$.

Waktu pencapaian memberi peringatan konkret. Untuk

$$
T_a(f)=\inf\{t\in[0,1]:f(t)\ge a\},
\qquad \inf\varnothing=\infty,
$$

pemetaan $T_a$ tidak kontinu pada semua lintasan. Ambil
$f(t)=-(t-1/2)^2$ dan $f_m=f-1/m$. Maka
$\|f_m-f\|_\infty\to0$, tetapi $T_0(f)=1/2$ sedangkan
$T_0(f_m)=\infty$. Untuk limit gerak Brown, kontinuitas hampir pasti dari
fungsional yang dipilih harus dibuktikan dari sifat penyeberangan dan hukum
maksimumnya; ia bukan konsekuensi otomatis dari distribusi berdimensi hingga.

Ada audit lain yang berdekatan. Keluarga Gaussian terpusat dengan kovarians
$\min(s,t)$ menentukan distribusi berdimensi hingga gerak Brown. Kriteria
kontinuitas Kolmogorov—misalnya melalui

$$
\mathbb E|B_t-B_s|^4=3|t-s|^2
$$

—memberi keberadaan modifikasi kontinu. Ia tidak menyatakan bahwa setiap
modifikasi yang mempunyai distribusi berdimensi hingga sama sudah kontinu.
Perbedaan versi, modifikasi, dan hukum pada ruang lintasan telah dibuktikan di
[jembatan kedua](02-keterukuran-proses-dan-hukum-lintasan.html); bagian ini
tidak mengulang contoh di sana.

Secara khusus, paragraf
[gerak Brown sebagai limit gerak acak](../brown/Standard.html#wlk) membuktikan
limit Gaussian pada satu waktu tetap lalu secara hati-hati mengatakan bahwa
*kita dapat berharap* semua syarat proses limit dipenuhi. Harapan itu bukan bukti
konvergensi fungsional. Topologi ruang lintasan, konvergensi FDD, dan
keketatan tetap merupakan gerbang tambahan—tepat seperti contoh tandingan puncak
bergerak di atas. Sementara itu, lingkup filtrasi dan syarat waktu henti
berhingga pada sifat Markov kuat sudah diperbaiki melalui
`correction.o009.random.brown.standard.strong-markov-filtration-scope` dan
`correction.o009.random.brown.standard.strong-markov-finite-stopping-time`;
unit ini hanya mempertahankan jejak koreksinya.

:::

::: {#matriks-perbaikan-klaim .bridge-section}

## Matriks perbaikan klaim

Tabel berikut ialah alat baca ringkas. Kolom “perbaikan” menyatakan satu syarat
cukup yang sesuai dengan konteks kursus, bukan klasifikasi semua teorema yang
mungkin.

| Klaim uji terlalu luas | Hipotesis atau struktur yang hilang | Kesimpulan yang dapat dipakai setelah diperbaiki |
|---|---|---|
| $X_n\to X$ hampir pasti, jadi ekspektasi konvergen | keterintegralan seragam atau dominasi terintegralkan | konvergensi $L^1$, lalu konvergensi ekspektasi |
| semua versi peluang bersyarat membentuk ukuran pada tiap titik | kernel koheren; sasaran Borel standar; kelas penentu terhitung untuk keunikan serentak | satu distribusi bersyarat reguler, unik hampir di mana-mana sebagai ukuran |
| $\tau<\infty$ hampir pasti cukup bagi penghentian opsional | waktu terbatas, atau keluarga berhenti terintegralkan seragam, atau versi teorema dengan $\mathbb E\tau<\infty$ dan kendali inkremen | identitas/ketaksamaan penghentian yang dinyatakan oleh versi teorema itu |
| tak tereduksi berarti konvergen ke stasioner | pada rantai berhingga: aperiodisitas; pada ruang umum: syarat rekurensi/ergodisitas yang sesuai | konvergensi dalam mode dan kelas awal yang benar-benar dibuktikan |
| matriks intensitas formal selalu menentukan CTMC yang konservatif | domain, semigrup, sifat konservatif, dan sifat tidak meledak | semigrup Markov dan proses dalam kelas yang dinyatakan |
| hitungan Poisson hingga pada semua himpunan | intensitas hingga pada himpunan yang dihitung; intensitas lokal untuk hingga lokal | hitungan Poisson hingga pada kelas himpunan yang sah |
| konvergensi FDD berarti konvergensi di $C[0,1]$ | keketatan pada topologi lintasan | konvergensi lemah hukum lintasan |
| konvergensi lintasan boleh langsung dimasukkan ke waktu pencapaian | kontinuitas hampir pasti fungsional di bawah hukum limit | teorema pemetaan kontinu untuk fungsional tersebut |

Ketika satu baris digunakan dalam bukti, pembaca harus kembali menulis lima
kotak lengkap. Tabel ini tidak menggantikan pemeriksaan ruang, ukuran, versi,
dan kuantor yang sebenarnya.

:::

::: {#latihan-penguasaan-audit-hipotesis .bridge-section}

## Latihan penguasaan audit hipotesis

Ketiga latihan berikut melengkapi kuota integratif untuk contoh tandingan dan
pembacaan literatur. Pada setiap latihan, jawaban tidak cukup
dengan mengatakan “teorema tidak berlaku”; pembaca harus menunjuk hipotesis
yang hilang, langkah yang gagal, dan satu versi perbaikan yang benar.

::: {#unit.o009.original.mastery.hypothesis-audits.01 .mastery-sequence}

::: {#unit.o009.original.mastery.hypothesis-audits.01.exercise .exercise}
### Latihan 1 — keterbatasan $L^1$ bukan keterintegralan seragam

Sebuah teks menyatakan klaim berikut.

> Jika $X_n\to X$ hampir pasti dan
> $\sup_n\mathbb E|X_n|<\infty$, maka
> $\mathbb E[X_n]\to\mathbb E[X]$.

Pada ruang probabilitas $\Omega=(0,1]$ dengan ukuran Lebesgue, definisikan

$$
X_n(\omega)=n\mathbf1_{(0,1/n]}(\omega).
$$

1. Tentukan limit hampir pasti $X_n$ dan hitung
   $\mathbb E[X_n]$ serta $\mathbb E|X_n|$.
2. Tentukan apakah $X_n\to X$ dalam $L^1$.
3. Uji keterintegralan seragam langsung dari definisi ekor.
4. Identifikasi langkah limit-ekspektasi yang tidak sah dan nyatakan sebuah
   teorema perbaikan dengan hipotesis yang tepat.
:::

::: {#unit.o009.original.mastery.hypothesis-audits.01.hint.01 .hint}
**Petunjuk 1.** Untuk $\omega>0$ tetap, bandingkan $n$ dengan $1/\omega$.
Kemudian integralkan $X_n$ hanya pada penyangganya $(0,1/n]$.
:::

::: {#unit.o009.original.mastery.hypothesis-audits.01.hint.02 .hint}
**Petunjuk 2.** Dalam definisi

$$
\lim_{K\to\infty}\sup_n
\mathbb E\!\left[|X_n|\mathbf1_{\{|X_n|>K\}}\right]=0,
$$

pilih bilangan bulat $n>K$.
:::

::: {#unit.o009.original.mastery.hypothesis-audits.01.answer .answer}
**Jawaban ringkas.** Berlaku $X_n\to0$ hampir pasti, tetapi
$\mathbb E[X_n]=\mathbb E|X_n|=1$ untuk setiap $n$. Jadi tidak ada
konvergensi $L^1$ atau konvergensi ekspektasi. Keluarga $(X_n)$ tidak
terintegralkan seragam. Perbaikan yang sah ialah: konvergensi dalam
probabilitas bersama keterintegralan seragam menyiratkan konvergensi $L^1$,
dan karena itu ekspektasi konvergen.
:::

::: {#unit.o009.original.mastery.hypothesis-audits.01.solution .solution}
**Penyelesaian lengkap.** Untuk setiap $\omega>0$, jika $n>1/\omega$, maka
$1/n<\omega$ dan $X_n(\omega)=0$. Jadi $X_n\to X=0$ pada setiap titik ruang
ini. Namun

$$
\mathbb E[X_n]
=\int_0^{1/n}n\,d\omega
=1,
\qquad
\mathbb E|X_n|=1.
$$

Karena $X=0$,

$$
\mathbb E|X_n-X|=1
$$

untuk setiap $n$. Jadi $X_n$ tidak konvergen dalam $L^1$, dan
$\mathbb E[X_n]=1$ tidak konvergen ke $\mathbb E[X]=0$. Contoh ini bahkan
nonnegatif dan semua ekspektasinya terdefinisi; masalahnya bukan pembatalan
tanda.

Untuk $K>0$, pilih bilangan bulat $n>K$. Pada $(0,1/n]$ berlaku
$|X_n|=n>K$, sehingga

$$
\mathbb E\!\left[|X_n|\mathbf1_{\{|X_n|>K\}}\right]
=n\lambda((0,1/n])
=1.
$$

Dengan demikian, untuk setiap $K$,

$$
\sup_n\mathbb E\!\left[
|X_n|\mathbf1_{\{|X_n|>K\}}
\right]\ge1.
$$

Limit ekornya tidak nol, jadi keluarga itu tidak terintegralkan seragam.
Hipotesis $\sup_n\mathbb E|X_n|<\infty$ hanya memberi keterbatasan $L^1$;
ia tidak mencegah massa harapan berkumpul pada kejadian yang makin kecil.

Teorema Vitali memberi perbaikan yang tepat:

$$
X_n\xrightarrow{\mathbb P}X
\quad\text{dan}\quad
(X_n)_n\text{ terintegralkan seragam}
\quad\Longrightarrow\quad
\mathbb E|X_n-X|\longrightarrow0.
$$

Karena

$$
|\mathbb E[X_n]-\mathbb E[X]|
\le\mathbb E|X_n-X|,
$$

konvergensi ekspektasi kemudian mengikuti. Dominasi
$|X_n|\le Y$ oleh satu $Y$ terintegralkan juga cukup melalui teorema
konvergensi terdominasi, tetapi merupakan syarat yang lebih kuat. Lemma Fatou
pada contoh ini hanya memberi
$\mathbb E[X]\le\liminf_n\mathbb E[X_n]$, yaitu $0\le1$, bukan kesamaan.
:::

:::

::: {#unit.o009.original.mastery.hypothesis-audits.02 .mastery-sequence}

::: {#unit.o009.original.mastery.hypothesis-audits.02.exercise .exercise}
### Latihan 2 — waktu henti berhingga hampir pasti belum cukup

Misalkan $\xi_1,\xi_2,\ldots$ i.i.d. dengan

$$
\mathbb P(\xi_k=1)=\mathbb P(\xi_k=-1)=\tfrac12,
\qquad
S_n=\sum_{k=1}^n\xi_k,
\qquad S_0=0,
$$

dan $\mathcal F_n=\sigma(\xi_1,\ldots,\xi_n)$. Definisikan

$$
\tau=\inf\{n\ge0:S_n=1\}.
$$

Sebuah naskah mengklaim bahwa untuk setiap martingal terintegralkan dan
setiap waktu henti $\tau<\infty$ hampir pasti,

$$
\mathbb E[M_\tau]=\mathbb E[M_0].
$$

1. Dengan penghentian pada batas $-m$ dan $1$, buktikan bahwa
   $\tau<\infty$ hampir pasti.
2. Buktikan bahwa $\mathbb E[S_{\tau\wedge N}]=0$ bagi setiap $N$.
3. Tunjukkan bahwa $\mathbb E\tau=\infty$ dan bahwa keluarga
   $(S_{\tau\wedge N})_N$ tidak terintegralkan seragam.
4. Tunjuk tepat langkah yang gagal ketika $N\to\infty$, lalu nyatakan dua
   versi perbaikan penghentian opsional yang sah.
:::

::: {#unit.o009.original.mastery.hypothesis-audits.02.hint.01 .hint}
**Petunjuk 1.** Untuk $m\ge1$, ambil

$$
\sigma_m=\inf\{n:S_n\in\{-m,1\}\}.
$$

Persamaan beda untuk masalah kebangkrutan penjudi memberi
$\mathbb P_0(S_{\sigma_m}=1)=m/(m+1)$. Biarkan $m\to\infty$.
:::

::: {#unit.o009.original.mastery.hypothesis-audits.02.hint.02 .hint}
**Petunjuk 2.** Tulis

$$
S_{\tau\wedge N}
=\sum_{k=1}^N\xi_k\mathbf1_{\{\tau\ge k\}},
$$

dan gunakan $\{\tau\ge k\}\in\mathcal F_{k-1}$. Jika
$\mathbb E\tau<\infty$, jumlah ekspektasi nilai mutlak dari suku-suku deret
tak hingga sama dengan $\mathbb E\tau$.
:::

::: {#unit.o009.original.mastery.hypothesis-audits.02.answer .answer}
**Jawaban ringkas.** Waktu $\tau$ berhingga hampir pasti, tetapi
$\mathbb E\tau=\infty$. Untuk setiap $N$,
$\mathbb E[S_{\tau\wedge N}]=0$, sedangkan
$S_{\tau\wedge N}\to S_\tau=1$ hampir pasti. Keluarga yang dihentikan tidak
terintegralkan seragam. Versi yang sah, misalnya, memakai waktu henti
terbatas; atau mengasumsikan keluarga $(M_{\tau\wedge n})_n$
terintegralkan seragam. Bagi inkremen terbatas, $\mathbb E\tau<\infty$ juga
merupakan syarat cukup yang umum.
:::

::: {#unit.o009.original.mastery.hypothesis-audits.02.solution .solution}
**Penyelesaian lengkap.** Untuk $m\ge1$, gerak acak yang diserap di
$\{-m,1\}$ mempunyai fungsi harmonik untuk probabilitas pencapaian, dengan

$$
\mathbb P_0(S_{\sigma_m}=1)=\frac{m}{m+1}.
$$

Kejadian $\{S_{\sigma_m}=1\}$ termuat dalam $\{\tau<\infty\}$, sehingga

$$
\mathbb P(\tau<\infty)\ge\frac{m}{m+1}
$$

untuk setiap $m$. Membiarkan $m\to\infty$ memberi
$\mathbb P(\tau<\infty)=1$. Perhitungan kebangkrutan penjudi ini dapat diperoleh
langsung dari persamaan beda pada himpunan hingga; jika penghentian opsional
dipakai untuk menurunkannya, martingal yang dihentikan di dua batas bersifat
terbatas dan memenuhi versi teorema yang sah.

Karena $\tau\wedge N$ terbatas,

$$
S_{\tau\wedge N}
=\sum_{k=1}^{N}\xi_k\mathbf1_{\{\tau\ge k\}}.
$$

Kejadian $\{\tau\ge k\}$ diketahui pada waktu $k-1$, dan
$\mathbb E(\xi_k\mid\mathcal F_{k-1})=0$. Maka

$$
\begin{aligned}
\mathbb E[S_{\tau\wedge N}]
&=\sum_{k=1}^N
\mathbb E\!\left[
\mathbf1_{\{\tau\ge k\}}
\mathbb E(\xi_k\mid\mathcal F_{k-1})
\right]\\
&=0.
\end{aligned}
$$

Sekarang andaikan $\mathbb E\tau<\infty$. Karena $|\xi_k|=1$,

$$
\sum_{k=1}^{\infty}
\mathbb E\!\left[
|\xi_k|\mathbf1_{\{\tau\ge k\}}
\right]
=\sum_{k=1}^{\infty}\mathbb P(\tau\ge k)
=\mathbb E\tau
<\infty.
$$

Fubini kemudian mengizinkan pertukaran jumlah dan ekspektasi. Karena
$\tau<\infty$ hampir pasti,

$$
S_\tau
=\sum_{k=1}^{\infty}\xi_k\mathbf1_{\{\tau\ge k\}},
$$

sehingga

$$
\mathbb E[S_\tau]
=\sum_{k=1}^{\infty}
\mathbb E\!\left[
\xi_k\mathbf1_{\{\tau\ge k\}}
\right]
=0.
$$

Namun definisi $\tau$ memberi $S_\tau=1$, jadi ekspektasinya satu. Kontradiksi
ini membuktikan $\mathbb E\tau=\infty$.

Selanjutnya,
$S_{\tau\wedge N}\to S_\tau=1$ hampir pasti, tetapi semua ekspektasi di ruas
kiri sama dengan nol. Jika keluarga itu terintegralkan seragam, teorema Vitali
akan memaksa konvergensi $L^1$ dan konvergensi ekspektasi menuju satu. Jadi
keluarga tersebut tidak terintegralkan seragam. Langkah yang gagal bukan
penghentian pada $\tau\wedge N$, melainkan pelewatan $N\to\infty$ melalui
ekspektasi tanpa kendali ekor.

Dua perbaikan umum adalah:

1. jika $\tau$ terbatas, penghentian opsional berlaku langsung;
2. jika $(M_{\tau\wedge n})_n$ terintegralkan seragam dan konvergen hampir
   pasti ke $M_\tau$, maka ekspektasinya dapat dilewatkan ke limit.

Selain itu, jika $|M_n-M_{n-1}|\le C$ hampir pasti dan
$\mathbb E\tau<\infty$, maka

$$
|M_{\tau\wedge n}|
\le |M_0|+C\tau,
$$

sehingga dominasi terintegralkan memberi jalur aman lain. Setiap penggunaan
harus menyebut versi mana yang dipakai.
:::

:::

::: {#unit.o009.original.mastery.hypothesis-audits.03 .mastery-sequence}

::: {#unit.o009.original.mastery.hypothesis-audits.03.exercise .exercise}
### Latihan 3 — FDD, keketatan, dan fungsional waktu pencapaian

Misalkan $U\sim\operatorname{Unif}[0,1]$ dan definisikan proses kontinu

$$
Z_n(t)=\bigl(1-n|t-U|\bigr)_+,
\qquad 0\le t\le1.
$$

Sebuah artikel membuktikan konvergensi semua distribusi berdimensi hingga
menuju proses nol. Artikel itu lalu menyimpulkan konvergensi lemah dalam
$C[0,1]$ dan menerapkan teorema pemetaan kontinu pada waktu pertama mencapai
suatu aras.

1. Buktikan konvergensi seluruh distribusi berdimensi hingga menuju nol.
2. Audit kesimpulan pada $C[0,1]$ dengan norma supremum dan modulus
   kontinuitas.
3. Nyatakan hipotesis tambahan yang memperbaiki lompatan dari FDD ke hukum
   lintasan.
4. Berikan contoh yang menunjukkan bahwa fungsional waktu pencapaian tidak
   kontinu pada semua lintasan, lalu nyatakan gerbang teorema pemetaan kontinu
   yang masih harus diperiksa.
:::

::: {#unit.o009.original.mastery.hypothesis-audits.03.hint.01 .hint}
**Petunjuk 1.** Untuk $t_1,\ldots,t_k$ tetap, gunakan

$$
\mathbb P\!\left(\max_j Z_n(t_j)>0\right)
\le\sum_{j=1}^k\mathbb P(|U-t_j|<1/n).
$$
:::

::: {#unit.o009.original.mastery.hypothesis-audits.03.hint.02 .hint}
**Petunjuk 2.** Bandingkan konvergensi FDD dengan
$\|Z_n\|_\infty$ dan

$$
w(Z_n,\delta)
=\sup_{|s-t|\le\delta}|Z_n(s)-Z_n(t)|.
$$

Untuk diskontinuitas waktu pencapaian aras nol, pertimbangkan
$f(t)=-(t-1/2)^2$ dan $f_m=f-1/m$.
:::

::: {#unit.o009.original.mastery.hypothesis-audits.03.answer .answer}
**Jawaban ringkas.** Semua FDD $Z_n$ konvergen ke FDD proses nol, tetapi
$\|Z_n\|_\infty=1$ hampir pasti dan keluarga hukumnya tidak ketat pada
$C[0,1]$. Jadi tidak ada konvergensi lemah menuju nol di ruang itu. Perbaikan
memerlukan keketatan hukum lintasan serta identifikasi semua limit
subsekuensial melalui FDD. Setelah konvergensi ruang lintasan diperoleh,
fungsional waktu pencapaian tetap hanya dapat dipakai bila ia kontinu hampir
pasti di bawah hukum limit.
:::

::: {#unit.o009.original.mastery.hypothesis-audits.03.solution .solution}
**Penyelesaian lengkap.** Untuk waktu tetap $t_1,\ldots,t_k$,

$$
\begin{aligned}
\mathbb P\!\left(
(Z_n(t_1),\ldots,Z_n(t_k))\ne(0,\ldots,0)
\right)
&\le\sum_{j=1}^k\mathbb P(|U-t_j|<1/n)\\
&\le\frac{2k}{n}\longrightarrow0.
\end{aligned}
$$

Jadi setiap vektor berdimensi hingga konvergen dalam probabilitas, dan
karena itu dalam distribusi, ke vektor nol.

Setiap lintasan $Z_n$ kontinu dan mencapai nilai satu pada $t=U$. Maka

$$
\|Z_n\|_\infty=1
$$

hampir pasti untuk setiap $n$. Jika $Z_n\Rightarrow0$ dalam $C[0,1]$, pemetaan
kontinu $f\mapsto\|f\|_\infty$ akan memberi
$\|Z_n\|_\infty\Rightarrow0$, bertentangan dengan hukum yang terkonsentrasi
pada satu.

Kegagalan keketatan dapat dilihat langsung. Ambil $\delta>0$ dan
$n\ge2$ dengan $1/n\le\delta$. Dari titik puncak $U$, paling sedikit satu di
antara $U-1/n$ dan $U+1/n$ masih berada dalam $[0,1]$. Nilai $Z_n$ di titik
itu nol, sedangkan $Z_n(U)=1$. Jadi

$$
w(Z_n,\delta)=1
$$

hampir pasti. Untuk setiap $\delta$, supremum terhadap $n$ dari peluang
modulus besar tetap satu; kriteria keketatan berbasis modulus kontinuitas
gagal secara maksimal.

Perbaikan yang sah ialah membuktikan dua hal:

1. keluarga hukum $(X_n)$ ketat pada $C[0,1]$;
2. setiap FDD $X_n$ konvergen ke FDD suatu proses $X$ yang bernilai di
   $C[0,1]$.

Setiap limit subsekuensial lalu mempunyai FDD yang sama dengan $X$. Hukum
Borel pada $C[0,1]$ ditentukan oleh evaluasi pada himpunan waktu rapat
terhitung, sehingga limit subsekuensial tersebut mempunyai hukum $X$ dan
seluruh barisan konvergen lemah.

Sekarang definisikan, untuk aras $a$,

$$
T_a(f)=\inf\{t\in[0,1]:f(t)\ge a\},
\qquad \inf\varnothing=\infty.
$$

Fungsional ini tidak kontinu pada semua $f\in C[0,1]$. Untuk $a=0$, ambil

$$
f(t)=-(t-\tfrac12)^2,
\qquad
f_m(t)=f(t)-\frac1m.
$$

Berlaku $\|f_m-f\|_\infty=1/m\to0$, tetapi

$$
T_0(f)=\tfrac12,
\qquad
T_0(f_m)=\infty.
$$

Karena itu, bahkan setelah $X_n\Rightarrow X$ pada ruang lintasan dibuktikan,
teorema pemetaan kontinu untuk $T_a$ memerlukan

$$
\mathbb P(X\in D_{T_a})=0,
$$

dengan $D_{T_a}$ himpunan titik diskontinuitas $T_a$. Untuk limit gerak Brown,
sifat penyeberangan ketat dan hukum maksimum dapat menyediakan gerbang itu
dalam formulasi yang sesuai; FDD saja tidak menyediakannya.
:::

:::

:::

::: {#hak-dan-provenans-audit-hipotesis .bridge-section}

## Hak dan provenans

Unit **Audit hipotesis untuk proses stokastik**, termasuk ketiga latihan,
petunjuk, jawaban, dan penyelesaian di atas, merupakan materi asli berbahasa
Indonesia yang disusun untuk edisi ini dan dilisensikan terpisah di bawah
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), sejauh hak baru
timbul. ID hak komponennya ialah
`rights.o009.original.bridge.hypothesis-audits.cc-by-4.0`.

Penyusunan unit ini dibantu oleh **OpenAI Codex gpt-5.6-sol, Ultra.**
Identitas model tersebut tidak menggantikan kredit penulis sumber atau
kontributor manusia. Tautan ke Random Services, QuantEcon, dan tiga jembatan
sebelumnya berfungsi sebagai penunjuk konteks. Semua kalimat berlabel
**klaim uji** sengaja dirumuskan oleh unit ini sebagai bahan audit dan bukan
kutipan atau atribusi kepada sumber yang ditautkan.

Unit ini hanya mengutip beberapa frasa donor secara singkat, teratribusi, dan
tertaut untuk keperluan audit; ia tidak mereproduksi prosa donor secara
substansial dan tidak melisensikan ulang Random Services, QuantEcon,
Žitković, MathJax, atau komponen lain. Hak campuran
seluruh edisi tetap dijelaskan dalam `LICENSES.md` dan backend hak per
komponen. Unit ini independen dan tidak didukung atau disahkan oleh penulis
sumber atau lembaga mereka.

Secara khusus, unit ini tidak mengklaim bahwa syarat cukup yang dipilih selalu
minimal, bahwa setiap matriks intensitas formal menentukan CTMC yang tidak meledak,
bahwa FDD menentukan keteraturan versi yang dipilih, atau bahwa waktu henti
yang hanya berhingga hampir pasti cukup bagi penghentian opsional.

:::

:::
