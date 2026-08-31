---
title: "Distribusi bersyarat reguler dan disiplin versi"
lang: id-ID
author:
  - "Codex (penulisan materi asli atas arahan pengguna)"
authoring:
  course_id: "o009"
  unit_id: "unit.o009.original.bridge.regular-conditional-probability"
  target_locale: "id-ID"
  source_type: "original"
  rights_id: "rights.o009.original.bridge.regular-conditional-probability.cc-by-4.0"
  license: "CC-BY-4.0"
  model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."
---

::: {#unit.o009.original.bridge.regular-conditional-probability .original-bridge}

# Distribusi bersyarat reguler dan disiplin versi

::: {#tujuan-dan-kesenjangan-versi .bridge-section}

## Tujuan dan kesenjangan versi

Notasi

$$
\mathbb P(Y\in B\mid X=x)
$$

terlihat seperti sebuah bilangan yang tinggal dihitung. Pada ruang diskret,
kesan itu sering benar: jika $\mathbb P(X=x)>0$, kita membagi peluang
gabungan dengan $\mathbb P(X=x)$. Jika hukum $X$ tidak beratom—misalnya $X$
mempunyai kepadatan—maka $\mathbb P(X=x)=0$ untuk setiap $x$. Nilai di ruas
kiri tetap dapat diberi makna,
tetapi maknanya bukan rasio pada kejadian nol. Ia adalah nilai suatu **kernel
probabilitas bersyarat** yang telah dipilih sebagai satu versi.

Unit [nilai harapan bersyarat](../expect/Conditional2.html) membangun objek
bersyarat untuk satu peubah acak atau satu kejadian pada satu waktu. Unit
[kernel](../expect/Kernels.html) menjelaskan kalkulus kernel. Di antara kedua
unit itu masih ada pertanyaan penting:

1. kapan versi-versi untuk semua kejadian dapat dipilih secara serentak agar
   menjadi ukuran peluang pada setiap titik;
2. di ruang mana kernel semacam itu dijamin ada;
3. dalam arti apa kernel tersebut unik;
4. apa yang boleh dikatakan pada nilai pengondisian yang bermassa nol.

Jawabannya memerlukan pemisahan antara kesamaan hampir pasti dan kesamaan
titik demi titik. Jawabannya juga memerlukan hipotesis ruang Borel standar
pada sasaran yang tepat. Kita akan menyatakan teorema keberadaan, memberikan
arsitektur buktinya, menurunkan rumus disintegrasi, dan menguji notasi
bersyarat pada contoh diskret maupun kontinu.

Biarkan $(\Omega,\mathcal F,\mathbb P)$ menjadi ruang peluang dan
$\mathcal G\subseteq\mathcal F$ sebuah sub-sigma-aljabar. Tidak diasumsikan
bahwa $(\Omega,\mathcal F)$ Borel standar kecuali ketika hal itu dinyatakan
secara khusus. Dengan demikian, pembaca dapat melihat persis ruang mana yang
memikul hipotesis keberadaan.

:::

::: {#dari-nilai-harapan-ke-kernel .bridge-section}

## Dari nilai harapan bersyarat ke kernel

Ada tiga tingkat objek yang tidak boleh disamakan.

1. Untuk peubah acak integrabel $Z$, objek
   $\mathbb E[Z\mid\mathcal G]$ adalah kelas fungsi $\mathcal G$-terukur yang
   sama hampir pasti.
2. Untuk satu $B$ tetap, objek
   $\mathbb P(Y\in B\mid\mathcal G)$ adalah singkatan bagi
   $\mathbb E[\mathbf1_{\{Y\in B\}}\mid\mathcal G]$, lagi-lagi sebuah kelas
   kesamaan hampir pasti.
3. Sebuah distribusi bersyarat reguler harus memilih seluruh keluarga itu
   secara koheren sehingga $B\mapsto K(\omega,B)$ merupakan ukuran peluang
   untuk setiap $\omega$, bukan hanya untuk hampir setiap $\omega$ yang dapat
   bergantung pada $B$.

> **Definisi (distribusi bersyarat reguler).** Misalkan
> $Y:(\Omega,\mathcal F)\to(T,\mathcal T)$ terukur. Sebuah distribusi
> bersyarat reguler $Y$ terhadap $\mathcal G$ adalah kernel probabilitas
> $$
> K:(\Omega,\mathcal G)\rightsquigarrow(T,\mathcal T)
> $$
> dengan dua sifat berikut.
>
> - Untuk setiap $B\in\mathcal T$, peta $\omega\mapsto K(\omega,B)$ terukur
>   terhadap $\mathcal G$.
> - Untuk setiap $B\in\mathcal T$ dan $G\in\mathcal G$,
>   $$
>   \int_GK(\omega,B)\,\mathbb P(d\omega)
>   =\mathbb P\bigl(G\cap\{Y\in B\}\bigr).
>   $$
>
> Selain itu, untuk setiap $\omega$, pemetaan
> $B\mapsto K(\omega,B)$ harus berupa ukuran peluang pada $(T,\mathcal T)$.

Identitas integral menyatakan bahwa $K(\cdot,B)$ merupakan satu versi dari
$\mathbb P(Y\in B\mid\mathcal G)$. Syarat terakhir menyatukan versi-versi
tersebut menjadi satu kernel.

Pemilihan kejadian demi kejadian tidak cukup. Ambil
$\Omega=T=[0,1]$ dengan ukuran Lebesgue, $\mathcal G=\mathcal F$ Borel, dan
$Y(\omega)=\omega$. Untuk setiap $B\in\mathcal B([0,1])$, pilih

$$
Z_B(\omega)=
\begin{cases}
\mathbf1_{(0,1]}(\omega),&B=[0,1],\\
\mathbf1_B(\omega),&B\ne[0,1].
\end{cases}
$$

Untuk setiap $B$ tetap, $Z_B$ berbeda dari
$\mathbf1_{\{Y\in B\}}$ paling banyak pada titik tunggal $\{0\}$. Jadi $Z_B$
adalah versi yang sah dari peluang bersyarat kejadian tersebut. Namun
$Z_{[0,1]}(0)=0$. Pada $\omega=0$, pemetaan $B\mapsto Z_B(0)$ bahkan tidak
mempunyai massa total satu. Keluarga $(Z_B)_B$ bukan kernel.

Kita juga tidak boleh memperbaikinya dengan mengambil irisan semua kejadian
berpeluang satu yang muncul secara terpisah. Setiap
$[0,1]\setminus\{t\}$ berpeluang satu, tetapi

$$
\bigcap_{t\in[0,1]}([0,1]\setminus\{t\})=\varnothing.
$$

Irisan tak terhitung dari kejadian berpeluang satu dapat kehilangan seluruh
massanya. Teorema berikut bekerja karena ruang Borel standar menyediakan
struktur pembangkit terhitung dan konstruksi ukuran yang koheren; bukan karena
semua wakil per kejadian boleh diambil irisannya begitu saja.

:::

::: {#keberadaan-pada-sasaran-borel-standar .bridge-section}

## Keberadaan pada sasaran Borel standar

Sebuah ruang terukur $(T,\mathcal T)$ disebut **ruang Borel standar** apabila
ia isomorfik secara terukur dengan sebuah himpunan Borel dalam suatu ruang
Polish. Himpunan terhitung dengan sigma-aljabar diskret, $\mathbb R^d$ dengan
sigma-aljabar Borel, dan ruang lintasan Polish dengan sigma-aljabar Borelnya
adalah contoh utama.

> **Teorema (keberadaan distribusi bersyarat reguler).** Misalkan
> $(\Omega,\mathcal F,\mathbb P)$ ruang peluang sembarang,
> $\mathcal G\subseteq\mathcal F$, dan
> $Y:\Omega\to(T,\mathcal T)$ terukur. Jika $(T,\mathcal T)$ tidak kosong dan
> Borel standar, maka terdapat distribusi bersyarat reguler $Y$ terhadap
> $\mathcal G$, berupa kernel
> $$
> K:(\Omega,\mathcal G)\rightsquigarrow(T,\mathcal T)
> $$

Hipotesis Borel standar di sini dikenakan pada ruang nilai $Y$. Ruang dasar
$(\Omega,\mathcal F)$ tidak perlu Borel standar. Ini penting ketika
$\mathcal F$ telah dilengkapi oleh himpunan-himpunan nol atau ketika ruang
dasarnya berasal dari konstruksi abstrak.

Berikut arsitektur bukti yang menjelaskan fungsi hipotesis tersebut.

1. Karena $T$ Borel standar, ia dapat dikodekan melalui isomorfisme Borel
   $\varphi:T\to E$, dengan $E$ himpunan Borel dalam $[0,1]$. Ganti sementara
   $Y$ oleh $Z=\varphi(Y)$.
2. Untuk setiap rasional $q$, pilih satu versi
   $$
   F_q=\mathbb E[\mathbf1_{\{Z\le q\}}\mid\mathcal G].
   $$
   Hanya ada terhitung banyak $q$, sehingga kita boleh membuang satu gabungan
   nol agar ketaksamaan monoton, batas ujung, dan relasi yang diperlukan
   berlaku serentak pada seluruh $q$ rasional.
3. Di luar himpunan nol bersama itu, bentuk fungsi distribusi kanan-kontinu
   dari nilai-nilai rasional, misalnya melalui limit dari kanan. Fungsi ini
   menentukan satu ukuran peluang $\mu_\omega$ pada $[0,1]$. Pada himpunan nol,
   pasang satu ukuran titik tetap; perbaikan dilakukan pada seluruh ukuran,
   bukan secara terpisah untuk setiap $B$.
4. Keterukuran $\omega\mapsto\mu_\omega(B)$ mula-mula diperoleh pada kelas
   interval pembangkit yang terhitung. Teorema kelas monoton memperluasnya ke
   seluruh himpunan Borel. Identitas integral juga diperluas dari kelas
   pembangkit ke seluruh sigma-aljabar.
5. Karena $Z$ berada dalam $E$ hampir pasti, identitas bersyarat untuk $E$
   memberi $\mu_\omega(E)=1$ di luar satu himpunan nol lagi. Perbaiki ukuran
   pada himpunan nol itu dan dorong balik melalui $\varphi^{-1}$.

Langkah ketiga tidak boleh diganti dengan kalimat “pilih wakil pada sebuah
pembangkit.” Nilai pada pembangkit yang dipilih sembarang belum tentu
merupakan preukuran atau memenuhi aditivitas terhitung. Konstruksi fungsi
distribusi dan perbaikan satu ukuran utuh adalah bagian substantif dari bukti.

Kernel tersebut juga mengondisikan fungsi dari $Y$, bukan hanya indikator.

> **Proposisi (bentuk fungsi).** Jika $f:T\to[0,\infty]$ terukur, maka
> $$
> \omega\longmapsto\int_T f(y)K(\omega,dy)
> $$
> adalah versi dari $\mathbb E[f(Y)\mid\mathcal G]$, dengan nilai diperluas
> dan boleh bernilai $+\infty$. Jika $f$ bernilai real dan $f(Y)$ integrabel,
> integral bertanda
> tersebut berhingga mutlak hampir pasti. Tetapkan nilainya sama dengan nol
> pada himpunan nol terukur tempat $\int|f|\,dK=\infty$; fungsi yang didefinisikan
> di seluruh $\Omega$ itu adalah versi dari
> $\mathbb E[f(Y)\mid\mathcal G]$.

**Bukti.** Untuk indikator, klaim ini adalah definisi kernel bersyarat. Untuk
fungsi sederhana nonnegatif, gunakan linearitas. Ambil barisan fungsi
sederhana yang naik menuju $f$ dan gunakan konvergensi monoton pada integral
kernel maupun integral terhadap $\mathbb P$. Untuk $f$ real integrabel,
terapkan hasil nonnegatif pada $|f|$, $f^+$, dan $f^-$. Integral
$\int|f|\,dK$ berhingga hampir pasti. Di himpunan itu ambil selisih integral
bagian positif dan negatif; pada himpunan pengecualian yang berpeluang nol,
gunakan nilai nol seperti dalam pernyataan. $\square$

:::

::: {#kelas-penentu-dan-versi-serentak .bridge-section}

## Kelas penentu dan versi serentak

Keunikan bersyarat mempunyai tiga tingkat.

- Untuk satu $B$ tetap, dua versi dari
  $\mathbb P(Y\in B\mid\mathcal G)$ sama hampir pasti; himpunan nolnya boleh
  bergantung pada $B$.
- Untuk dua kernel bersyarat reguler dengan sasaran Borel standar, ada satu
  himpunan nol di luar mana kedua **ukuran** itu sama seluruhnya.
- Kesamaan pada setiap $\omega$, atau pada setiap nilai $x$ yang mungkin
  dipakai untuk mengondisikan, tidak mengikuti dari dua pernyataan tersebut.

> **Teorema (keunikan serentak).** Misalkan $K$ dan $L$ adalah dua distribusi
> bersyarat reguler $Y$ terhadap $\mathcal G$, dengan sasaran Borel
> standar $(T,\mathcal T)$. Maka ada $N\in\mathcal G$ dengan
> $\mathbb P(N)=0$ sedemikian sehingga
> $$
> K(\omega,\cdot)=L(\omega,\cdot)
> \qquad(\omega\notin N).
> $$

**Bukti.** Ruang Borel standar mempunyai sebuah sistem-$\pi$ terhitung
$\mathcal C$ yang membangkitkan $\mathcal T$ dan menentukan ukuran peluang;
kita boleh memastikan $T\in\mathcal C$. Untuk setiap $C\in\mathcal C$,
$K(\cdot,C)$ dan $L(\cdot,C)$ adalah dua versi nilai harapan bersyarat yang
sama. Maka ada $N_C\in\mathcal G$ dengan peluang nol tempat kesamaan mungkin
gagal. Bentuk

$$
N=\bigcup_{C\in\mathcal C}N_C.
$$

Gabungan ini terhitung, jadi $\mathbb P(N)=0$. Jika $\omega\notin N$, kedua
ukuran peluang $K(\omega,\cdot)$ dan $L(\omega,\cdot)$ sepakat pada
$\mathcal C$. Teorema sistem-$\pi$–$\lambda$ memperluas kesamaan ke seluruh
$\mathcal T$. $\square$

Kelas penentu terhitung dipakai untuk **keunikan** setelah kita sudah tahu
bahwa $K(\omega,\cdot)$ dan $L(\omega,\cdot)$ adalah ukuran. Ia tidak mengubah
sebuah keluarga wakil sembarang menjadi kernel. Perbedaan arah logika ini
adalah inti disiplin versi.

Jika sebuah kernel perlu diperbaiki pada $N$, pilih satu ukuran peluang tetap
$\rho$ pada $T$ dan definisikan

$$
\widetilde K(\omega,\cdot)=
\begin{cases}
K(\omega,\cdot),&\omega\notin N,\\
\rho(\cdot),&\omega\in N.
\end{cases}
$$

Karena $N\in\mathcal G$, hasilnya tetap kernel terukur dan seluruh identitas
integral tidak berubah. Mengganti nilai secara berbeda untuk setiap $B$ dapat
merusak normalisasi atau aditivitas dan karena itu bukan perbaikan yang sah.

:::

::: {#pengondisian-pada-peubah-acak .bridge-section}

## Pengondisian pada peubah acak

Sekarang misalkan

$$
X:\Omega\to(S,\mathcal S),
\qquad
Y:\Omega\to(T,\mathcal T)
$$

adalah peubah acak. Notasi “dengan syarat $X=x$” meminta kernel yang domainnya
adalah ruang nilai $X$, bukan ruang sampel $\Omega$.

> **Teorema (hukum bersyarat terhadap sebuah peubah acak).** Jika $S$ dan
> $T$ merupakan ruang Borel standar, terdapat kernel probabilitas
> $$
> Q:(S,\mathcal S)\rightsquigarrow(T,\mathcal T)
> $$
> sedemikian sehingga untuk setiap $A\in\mathcal S$ dan $B\in\mathcal T$,
> $$
> \mathbb P(X\in A,Y\in B)
> =\int_AQ(x,B)\,\mathbb P_X(dx).
> $$
> Secara ekuivalen, $Q(X,B)$ adalah sebuah versi dari
> $\mathbb P(Y\in B\mid\sigma(X))$ untuk setiap $B$.

Identitas ini disebut **disintegrasi** hukum gabungan $(X,Y)$ terhadap
marginal $\mathbb P_X$. Ia memberi arti ketat pada

$$
Q(x,B)=\mathbb P(Y\in B\mid X=x).
$$

Teorema dapat dibuktikan sebagai kasus teorema disintegrasi pada produk Borel
standar. Cara lain ialah mulai dari distribusi bersyarat reguler terhadap
$\sigma(X)$ dan memandang $\omega\mapsto K(\omega,\cdot)$ sebagai satu peta
terukur menuju ruang Borel standar $\mathcal P(T)$ dari ukuran peluang, yang
sigma-aljabarnya dibangkitkan oleh evaluasi pada sebuah kelas penentu
terhitung. Faktorkan **seluruh peta bernilai ukuran** itu melalui $X$ dengan
Doob–Dynkin. Memfaktorkan setiap $K(\cdot,B)$ secara terpisah tidak cukup untuk
membuktikan aditivitas terhitung. Hipotesis Borel standar pada $S$ dan $T$
memastikan bahwa faktorisasi bernilai ukuran serta struktur terukurnya
tersedia.

Jika $Q$ dan $R$ keduanya memenuhi identitas di atas, maka untuk $B$ tetap
$Q(\cdot,B)=R(\cdot,B)$ hampir di mana-mana terhadap $\mathbb P_X$. Kelas
penentu terhitung pada $T$ memberi satu himpunan
$M\in\mathcal S$ dengan $\mathbb P_X(M)=0$ sehingga

$$
Q(x,\cdot)=R(x,\cdot)
\qquad(x\notin M).
$$

Jadi kernel unik sebagai ukuran hanya $\mathbb P_X$-hampir di mana-mana.
Teorema tidak memilih nilai kanonik pada setiap $x$.

Untuk fungsi terukur nonnegatif $g:S\times T\to[0,\infty]$, bentuk fungsi
disintegrasi adalah

$$
\mathbb E[g(X,Y)]
=\int_S\left[\int_Tg(x,y)Q(x,dy)\right]\mathbb P_X(dx).
$$

Untuk $g$ bernilai real, rumus yang sama berlaku apabila $g(X,Y)$ integrabel:
integral dalam berhingga mutlak untuk $\mathbb P_X$-hampir setiap $x$ dan
didefinisikan sama dengan nol pada himpunan marginal nol tempat
$\int|g(x,y)|Q(x,dy)=\infty$. Pembuktiannya dimulai dari indikator persegi
panjang, diteruskan ke fungsi sederhana, lalu ke fungsi nonnegatif dengan
konvergensi monoton; kasus bertanda memakai bagian positif dan negatif.

:::

::: {#rumus-disintegrasi-dan-kepadatan .bridge-section}

## Rumus disintegrasi dan kepadatan

Pada kasus yang mempunyai kepadatan, kernel dapat ditulis eksplisit tanpa
menghilangkan disiplin nilai nol. Misalkan $\mu$ dan $\nu$ sigma-hingga dan
hukum gabungan $(X,Y)$ mempunyai kepadatan $p(x,y)$ terhadap ukuran produk
$\mu\otimes\nu$. Bentuk marginal

$$
p_X(x)=\int_Tp(x,y)\,\nu(dy).
$$

Karena $\int p_X\,d\mu=1$, himpunan
$D=\{x:0<p_X(x)<\infty\}$ mempunyai komplemen yang bermarginal nol. Pilih
satu hukum peluang tetap $\rho$ pada $T$, lalu definisikan

$$
Q(x,B)=
\begin{cases}
\displaystyle\int_B\frac{p(x,y)}{p_X(x)}\,\nu(dy),&x\in D,\\[1.2ex]
\rho(B),&x\notin D.
\end{cases}
$$

Untuk setiap $x$, $Q(x,\cdot)$ adalah ukuran peluang. Keterukuran terhadap
$x$ mengikuti dari Tonelli untuk integral kernel nonnegatif. Untuk
$A\in\mathcal S$ dan $B\in\mathcal T$,

$$
\begin{aligned}
\int_AQ(x,B)\,\mathbb P_X(dx)
&=\int_{A\cap D}
  \left[\int_B\frac{p(x,y)}{p_X(x)}\,\nu(dy)\right]
  p_X(x)\,\mu(dx)\\
&=\int_{A\times B}p(x,y)\,(\mu\otimes\nu)(d(x,y)).
\end{aligned}
$$

Bagian $D^c$ tidak berkontribusi terhadap integral marginal: tempat
$p_X=0$ bermassa marginal nol, sedangkan tempat $p_X=\infty$ bermassa
$\mu$ nol karena $p_X$ integrabel. Karena itu, hukum $\rho$ di bagian tersebut
dapat diganti dengan kernel terukur lain tanpa mengubah disintegrasi.
Kebebasan ini bukan cacat rumus; ia tepat mencerminkan keunikan hanya hampir
di mana-mana.

Untuk $0<p_X(x)<\infty$, fungsi

$$
q(y\mid x)=\frac{p(x,y)}{p_X(x)}
$$

disebut kepadatan bersyarat. Menulis rasio yang sama pada titik di luar $D$
menghasilkan bentuk tak terdefinisi atau pembagian oleh nol dan tidak
mendefinisikan hukum. Pada titik itu kita harus menyatakan versi kernel yang
dipilih.

:::

::: {#nilai-pada-titik-pengondisian-nol .bridge-section}

## Nilai pada titik pengondisian bermassa nol

Jika $X$ diskret dan $\mathbb P(X=x)>0$, disintegrasi memberi rumus biasa

$$
Q(x,B)
=\frac{\mathbb P(Y\in B,X=x)}{\mathbb P(X=x)}.
$$

Rumus ini menentukan $Q(x,\cdot)$ secara unik pada atom positif tersebut.
Sebaliknya, jika $\mathbb P(X=x)=0$, identitas disintegrasi tidak melihat
nilai kernel pada titik tunggal $\{x\}$. Nilai itu dapat dipilih karena alasan
kontinuitas, simetri, batas, atau kemudahan komputasi, tetapi alasan tambahan
tersebut bukan konsekuensi dari definisi probabilitas bersyarat saja.

Contoh paling tajam adalah $X=Y$ yang seragam pada $[0,1]$. Kernel alami

$$
Q(x,\cdot)=\delta_x
$$

menyatakan bahwa mengetahui $X=x$ menentukan $Y=x$. Tetapkan
$x_0=1/2$ dan ubah seluruh ukuran di satu titik:

$$
Q'(x,\cdot)=
\begin{cases}
\delta_x,&x\ne x_0,\\
\delta_0,&x=x_0.
\end{cases}
$$

Kedua objek adalah kernel Borel dan keduanya menghasilkan hukum diagonal yang
sama setelah diintegrasikan terhadap ukuran Lebesgue. Namun

$$
Q(x_0,\{x_0\})=1,
\qquad
Q'(x_0,\{x_0\})=0.
$$

Tidak ada kontradiksi: $\{x_0\}$ adalah himpunan nol untuk marginal $X$.
Notasi $\mathbb P(Y\in B\mid X=x_0)$ tanpa menyebut versi tidak menentukan
salah satu dari kedua nilai itu.

Perbedaan ini juga membatasi interpretasi simulasi. Algoritme yang memasukkan
$x$ tertentu akan memakai kernel yang dikodekan oleh program, termasuk
pilihannya pada nilai marginal nol. Kebenaran identitas disintegrasi tidak
sendiri menjamin bahwa pilihan titik tersebut kontinu, stabil secara numerik,
atau sesuai dengan limit model yang diinginkan.

:::

::: {#probabilitas-bersyarat-seluruh-eksperimen .bridge-section}

## Probabilitas bersyarat seluruh eksperimen

Kadang-kadang “probabilitas bersyarat reguler terhadap $\mathcal G$” berarti
sebuah kernel

$$
R:(\Omega,\mathcal G)\rightsquigarrow(\Omega,\mathcal F)
$$

yang memenuhi

$$
R(\cdot,A)
=\mathbb P(A\mid\mathcal G)
\quad\text{hampir pasti untuk setiap }A\in\mathcal F.
$$

Ini adalah kasus khusus distribusi bersyarat reguler dengan
$Y=\operatorname{id}_\Omega$. Teorema keberadaan sebelumnya dapat langsung
dipakai hanya jika ruang terukur sasaran $(\Omega,\mathcal F)$ sendiri Borel
standar. Fakta bahwa $Y$ yang lain bernilai di ruang Borel standar tidak
otomatis membuat ruang dasar Borel standar.

Penyelesaian sebuah sigma-aljabar Borel dengan semua bagian himpunan nol juga
tidak otomatis tetap menjadi ruang Borel standar sebagai ruang terukur.
Karena itu, klaim “probabilitas bersyarat reguler selalu ada untuk semua
kejadian $A$” memerlukan hipotesis tambahan pada $(\Omega,\mathcal F)$ atau
sebuah teorema lain yang dinyatakan secara eksplisit.

Ada kehati-hatian kedua. Untuk setiap $G\in\mathcal G$ tetap,
$R(\cdot,G)$ dan $\mathbf1_G$ adalah dua versi dari objek bersyarat yang sama,
sehingga keduanya sama hampir pasti. Namun satu himpunan nol yang bekerja
serentak untuk **semua** $G\in\mathcal G$ tidak boleh diklaim dari argumen ini
tanpa syarat keterhitungan yang memadai pada $\mathcal G$. Properti per kejadian,
versi serentak, dan properti titik demi titik tetap merupakan tiga tingkat
yang berbeda.

:::

::: {#audit-klaim-probabilitas-bersyarat .bridge-section}

## Audit klaim probabilitas bersyarat

Sebelum menerima sebuah rumus atau argumen tentang pengondisian, periksa
daftar berikut.

1. **Objek apa yang dikondisikan?** Nilai harapan satu fungsi, peluang satu
   kejadian, atau seluruh hukum peluang memerlukan tingkat koherensi berbeda.
2. **Di mana kernelnya hidup?** Kernel terhadap $\mathcal G$ berdomain
   $\Omega$; kernel dengan syarat $X=x$ berdomain ruang nilai $X$.
3. **Hipotesis keberadaan apa yang dipakai?** Untuk teorema dalam unit ini,
   ruang nilai peubah yang dikondisikan harus Borel standar. Probabilitas
   bersyarat untuk seluruh $\mathcal F$ membutuhkan syarat itu pada ruang
   dasar ketika memakai peta identitas.
4. **Apakah keluarga per kejadian sudah terbukti sebagai ukuran?** Keterukuran
   tiap koordinat $B$ dan kesamaan hampir pasti tidak membuktikan normalisasi
   atau aditivitas terhitung pada satu titik.
5. **Apakah himpunan nol digabungkan secara sah?** Hanya keluarga terhitung
   boleh digabungkan langsung. Kelas penentu terhitung memberi keunikan
   serentak bagi dua kernel yang sudah sah.
6. **Ukuran mana yang mengatur “hampir di mana-mana”?** Untuk $K(\omega,\cdot)$
   ukurannya $\mathbb P$; untuk $Q(x,\cdot)$ ukurannya marginal
   $\mathbb P_X$.
7. **Apakah titik pengondisian bermassa positif?** Rasio atomik hanya berlaku
   jika penyebut positif. Kepadatan bersyarat hanya ditentukan di tempat
   marginal positif.
8. **Apakah nilai pada himpunan nol diberi status yang jujur?** Nilai itu
   mungkin merupakan pilihan versi yang berguna, tetapi bukan nilai kanonik
   yang dipaksa oleh hukum gabungan.
9. **Apakah kernel diperbaiki sebagai satu ukuran utuh?** Pada himpunan nol,
   ganti $K(\omega,\cdot)$ dengan satu hukum peluang tetap; jangan menambal
   setiap $B$ secara independen.
10. **Apakah notasi menyembunyikan struktur tambahan?** Kontinuitas terhadap
    $x$, kepadatan, simetri, atau solusi persamaan stokastik dapat memilih versi
    istimewa, tetapi harus disebut sebagai informasi tambahan.

Daftar ini memperbaiki lingkup pernyataan informal dalam unit donor tanpa
mengubah byte sumbernya. Ia juga menghubungkan jembatan
[konstruksi Kolmogorov](01-konstruksi-kolmogorov.html) dan
[keterukuran proses](02-keterukuran-proses-dan-hukum-lintasan.html): struktur
Borel standar dan argumen keterhitungan bekerja di tempat tertentu, bukan
sebagai izin untuk mengambil irisan keluarga nol tak terhitung.

:::

::: {#latihan-penguasaan-probabilitas-bersyarat-reguler .bridge-section}

## Latihan penguasaan probabilitas bersyarat reguler

::: {#unit.o009.original.mastery.regular-conditional-probability.01 .mastery-sequence}

::: {#unit.o009.original.mastery.regular-conditional-probability.01.exercise .exercise}
### Latihan 1 — kernel pada keadaan berpeluang nol

Misalkan $X$ bernilai di $S=\{a,b,c\}$ dan $Y$ bernilai di $T=\{0,1\}$.
Satu-satunya massa gabungan yang positif adalah

$$
\begin{array}{c|cc}
 &Y=0&Y=1\\ \hline
X=a&1/6&1/3\\
X=b&1/4&1/4\\
X=c&0&0.
\end{array}
$$

1. Tentukan seluruh kernel $Q:S\rightsquigarrow T$ yang merupakan hukum
   bersyarat $Y$ dengan syarat $X$.
2. Verifikasi identitas disintegrasi untuk semua $A\subseteq S$ dan
   $B\subseteq T$.
3. Jelaskan tepat di mana kernel unik dan di mana ia bebas.
4. Sebagai perluasan, misalkan $Y$ bernilai di $\mathbb N_0$ dan
   $Z_n$ adalah versi dari
   $\mathbb P(Y=n\mid\mathcal G)$. Tunjukkan bagaimana satu perbaikan pada
   himpunan nol bersama menghasilkan kernel
   $K(\omega,A)=\sum_{n\in A}Z_n(\omega)$.
:::

::: {#unit.o009.original.mastery.regular-conditional-probability.01.hint.01 .hint}
**Petunjuk 1.** Hitung marginal $\mathbb P_X$. Pada $a$ dan $b$, gunakan
rasio atomik. Pada $c$, pilih sembarang parameter $\theta\in[0,1]$ untuk
$Q(c,\{1\})$.
:::

::: {#unit.o009.original.mastery.regular-conditional-probability.01.hint.02 .hint}
**Petunjuk 2.** Untuk perluasan terhitung, ambillah irisan kejadian berpeluang satu
tempat semua $Z_n\ge0$ dan $\sum_nZ_n=1$. Irisan ini sah karena indeks $n$
terhitung. Pada komplemennya, ganti seluruh barisan dengan satu distribusi
titik tetap.
:::

::: {#unit.o009.original.mastery.regular-conditional-probability.01.answer .answer}
**Jawaban ringkas.** Marginalnya ialah
$\mathbb P_X(a)=\mathbb P_X(b)=1/2$ dan $\mathbb P_X(c)=0$. Jadi
$Q(a,\{1\})=2/3$, $Q(b,\{1\})=1/2$, sedangkan
$Q(c,\{1\})=\theta$ boleh sembarang dalam $[0,1]$. Nilai pada $c$ hilang dari
semua integral terhadap $\mathbb P_X$. Pada sasaran terhitung, perbaikan
serentak seluruh massa atom menghasilkan kernel dengan menjumlahkan massa
pada $A$.
:::

::: {#unit.o009.original.mastery.regular-conditional-probability.01.solution .solution}
**Penyelesaian lengkap.** Dari tabel,

$$
\mathbb P_X(a)=\frac16+\frac13=\frac12,
\qquad
\mathbb P_X(b)=\frac14+\frac14=\frac12,
\qquad
\mathbb P_X(c)=0.
$$

Pada atom positif, rumus rasio memaksa

$$
Q(a,\{0\})=\frac{1/6}{1/2}=\frac13,
\quad
Q(a,\{1\})=\frac23,
$$

dan

$$
Q(b,\{0\})=Q(b,\{1\})=\frac12.
$$

Pada $c$, pilih $\theta\in[0,1]$ dan pasang
$Q(c,\{1\})=\theta$, $Q(c,\{0\})=1-\theta$. Nilai pada $\varnothing$ dan
$T$ ditentukan oleh aksioma ukuran. Karena $S$ dan $T$ diskret hingga, fungsi
$x\mapsto Q(x,B)$ terukur untuk setiap $B$.

Untuk $A\subseteq S$ dan $B\subseteq T$,

$$
\int_AQ(x,B)\,\mathbb P_X(dx)
=\sum_{x\in A}Q(x,B)\mathbb P_X(x).
$$

Suku $x=c$ selalu nol. Untuk $x=a,b$, definisi rasio memberi
$Q(x,B)\mathbb P_X(x)=\mathbb P(X=x,Y\in B)$. Menjumlahkan terhadap
$x\in A$ menghasilkan $\mathbb P(X\in A,Y\in B)$. Jadi setiap pilihan
$\theta$ adalah kernel bersyarat yang sah untuk hukum gabungan yang sama.
Kernel dipaksa pada $a,b$ dan bebas
pada $c$, tepat sesuai keunikan $\mathbb P_X$-hampir di mana-mana.

Untuk perluasan, ambil wakil $\mathcal G$-terukur $Z_n$ dari
$\mathbb E[\mathbf1_{\{Y=n\}}\mid\mathcal G]$. Setiap $Z_n\ge0$ hampir pasti.
Selain itu, oleh konvergensi monoton bersyarat,

$$
\sum_{n=0}^{\infty}Z_n
=\mathbb E\left[\sum_{n=0}^{\infty}
\mathbf1_{\{Y=n\}}\middle|\mathcal G\right]
=1
\quad\text{hampir pasti}.
$$

Karena indeksnya terhitung, ada satu $N\in\mathcal G$ berpeluang nol di luar
mana semua ketaknegatifan dan identitas jumlah berlaku. Pada $N$, ganti seluruh
barisan dengan $(1,0,0,\ldots)$. Sekarang, untuk setiap $\omega$, barisan itu
adalah distribusi peluang pada $\mathbb N_0$. Definisikan

$$
K(\omega,A)=\sum_{n\in A}Z_n(\omega).
$$

Pemetaan ini terukur dalam $\omega$ sebagai limit jumlah parsial dan merupakan
ukuran peluang dalam $A$. Untuk $G\in\mathcal G$, Tonelli memberi

$$
\int_GK(\omega,A)\,d\mathbb P
=\sum_{n\in A}\int_GZ_n\,d\mathbb P
=\sum_{n\in A}\mathbb P(G\cap\{Y=n\})
=\mathbb P(G\cap\{Y\in A\}).
$$

Jadi $K$ adalah distribusi bersyarat reguler pada sasaran terhitung.
:::

:::

::: {#unit.o009.original.mastery.regular-conditional-probability.02 .mastery-sequence}

::: {#unit.o009.original.mastery.regular-conditional-probability.02.exercise .exercise}
### Latihan 2 — kepadatan pada segitiga

Pasangan $(X,Y)$ mempunyai kepadatan gabungan

$$
p(x,y)=2\,\mathbf1_{\{0<x<y<1\}}
$$

terhadap ukuran Lebesgue pada $\mathbb R^2$.

1. Hitung kepadatan marginal $p_X$.
2. Bangun kernel Borel $Q(x,dy)$ untuk hukum $Y$ dengan syarat $X=x$, termasuk
   nilainya untuk $x\notin(0,1)$.
3. Verifikasi identitas disintegrasi untuk semua himpunan Borel $A,B$.
4. Hitung satu versi dari $\mathbb E[Y\mid X=x]$ dan jelaskan status nilainya
   pada $x=1$.
:::

::: {#unit.o009.original.mastery.regular-conditional-probability.02.hint.01 .hint}
**Petunjuk 1.** Untuk $0<x<1$, integralkan $2$ terhadap
$y\in(x,1)$. Kepadatan bersyaratnya konstan pada interval tersebut.
:::

::: {#unit.o009.original.mastery.regular-conditional-probability.02.hint.02 .hint}
**Petunjuk 2.** Di luar $(0,1)$, pilih satu ukuran titik tetap, misalnya
$\delta_0$. Untuk disintegrasi, integral terhadap $\mathbb P_X$ hanya membaca
$0<x<1$; gunakan Tonelli untuk menukar integral.
:::

::: {#unit.o009.original.mastery.regular-conditional-probability.02.answer .answer}
**Jawaban ringkas.** Marginalnya
$p_X(x)=2(1-x)\mathbf1_{(0,1)}(x)$. Untuk $0<x<1$,
$Q(x,dy)=\mathbf1_{(x,1)}(y)\,dy/(1-x)$; di luar interval itu, kita boleh
memakai $\delta_0$. Maka
$\mathbb E[Y\mid X=x]=(1+x)/2$ pada $(0,1)$. Nilai pada $x=1$ adalah pilihan
versi; untuk kernel yang dipilih ia sama dengan nol.
:::

::: {#unit.o009.original.mastery.regular-conditional-probability.02.solution .solution}
**Penyelesaian lengkap.** Untuk $0<x<1$,

$$
p_X(x)=\int_{\mathbb R}2\mathbf1_{\{x<y<1\}}\,dy
=2(1-x),
$$

dan $p_X(x)=0$ di luar interval itu. Integral totalnya
$\int_0^1 2(1-x)dx=1$, sesuai normalisasi hukum gabungan.

Definisikan, untuk $B\in\mathcal B(\mathbb R)$,

$$
Q(x,B)=
\begin{cases}
\displaystyle\frac{\lambda(B\cap(x,1))}{1-x},&0<x<1,\\[1.2ex]
\delta_0(B),&x\notin(0,1).
\end{cases}
$$

Untuk setiap $x$, ini ukuran peluang. Untuk $B$ tetap, fungsi
$x\mapsto\lambda(B\cap(x,1))$ terukur karena dapat ditulis sebagai
$\int\mathbf1_B(y)\mathbf1_{\{x<y<1\}}dy$ dan Tonelli memberi keterukuran
parameter. Jadi $Q$ adalah kernel Borel.

Untuk $A,B$ Borel,

$$
\begin{aligned}
\int_AQ(x,B)\,\mathbb P_X(dx)
&=\int_{A\cap(0,1)}
\frac{\lambda(B\cap(x,1))}{1-x}\,2(1-x)\,dx\\
&=\int_A\int_B2\mathbf1_{\{0<x<y<1\}}\,dy\,dx\\
&=\mathbb P(X\in A,Y\in B).
\end{aligned}
$$

Karena itu $Q$ adalah hukum bersyarat yang dicari. Untuk $0<x<1$,

$$
\int y\,Q(x,dy)
=\frac1{1-x}\int_x^1y\,dy
=\frac{1+x}{2}.
$$

Pada $x=1$, kernel pilihan kita ialah $\delta_0$, sehingga integralnya nol.
Mengubah $Q(1,\cdot)$ menjadi hukum peluang lain akan mengubah nilai titik itu
tanpa mengubah disintegrasi, sebab $\mathbb P_X(\{1\})=0$. Jadi rumus
$(1+x)/2$ pada $(0,1)$ ditentukan hampir di mana-mana, sedangkan perpanjangan
ke $x=1$ memerlukan pilihan versi tambahan.
:::

:::

::: {#unit.o009.original.mastery.regular-conditional-probability.03 .mastery-sequence}

::: {#unit.o009.original.mastery.regular-conditional-probability.03.exercise .exercise}
### Latihan 3 — dua versi pada satu nilai nol

Pada $([0,1],\mathcal B,\lambda)$, ambil $X(\omega)=Y(\omega)=\omega$ dan
$x_0=1/2$. Definisikan

$$
Q(x,\cdot)=\delta_x,
\qquad
Q'(x,\cdot)=
\begin{cases}
\delta_x,&x\ne x_0,\\
\delta_0,&x=x_0.
\end{cases}
$$

1. Buktikan bahwa $Q$ dan $Q'$ adalah kernel Borel.
2. Verifikasi bahwa keduanya memenuhi identitas disintegrasi untuk hukum
   gabungan $(X,Y)$.
3. Berikan sebuah $B$ yang membuat $Q(x_0,B)\ne Q'(x_0,B)$.
4. Untuk sasaran Borel standar umum, buktikan bahwa dua kernel yang mewakili
   distribusi bersyarat yang sama tetap harus sama sebagai ukuran di luar satu
   himpunan marginal nol.
:::

::: {#unit.o009.original.mastery.regular-conditional-probability.03.hint.01 .hint}
**Petunjuk 1.** Untuk $B$ Borel, $Q(x,B)=\mathbf1_B(x)$. Kernel kedua berbeda
hanya melalui indikator titik tunggal $\{x_0\}$. Dalam integral Lebesgue,
perubahan pada titik tunggal hilang.
:::

::: {#unit.o009.original.mastery.regular-conditional-probability.03.hint.02 .hint}
**Petunjuk 2.** Untuk bagian umum, pilih sistem-$\pi$ penentu yang terhitung.
Gabungkan himpunan nol tempat kedua kernel berbeda pada setiap anggota sistem,
lalu pakai teorema sistem-$\pi$–$\lambda$ pada titik di luar gabungan itu.
:::

::: {#unit.o009.original.mastery.regular-conditional-probability.03.answer .answer}
**Jawaban ringkas.** Kedua kernel Borel karena evaluasi
$x\mapsto\mathbf1_B(x)$ terukur dan perubahan dilakukan pada titik Borel
tunggal. Keduanya mengintegralkan $\mathbf1_B(x)$ terhadap Lebesgue, sebab titik tunggal
$x_0$ tidak berkontribusi. Untuk $B=\{x_0\}$, nilai masing-masing satu dan
nol. Pada sasaran Borel standar, kelas penentu terhitung menyatukan kesamaan
per kejadian menjadi kesamaan seluruh ukuran di luar satu himpunan nol.
:::

::: {#unit.o009.original.mastery.regular-conditional-probability.03.solution .solution}
**Penyelesaian lengkap.** Untuk $B\in\mathcal B([0,1])$,

$$
Q(x,B)=\delta_x(B)=\mathbf1_B(x),
$$

yang Borel dalam $x$. Sementara itu,

$$
Q'(x,B)
=\mathbf1_{\{x\ne x_0\}}\mathbf1_B(x)
 +\mathbf1_{\{x=x_0\}}\mathbf1_B(0),
$$

juga Borel. Untuk setiap $x$, kedua pemetaan terhadap $B$ merupakan ukuran
peluang, jadi keduanya kernel Borel.

Hukum gabungan $(X,Y)$ terkonsentrasi pada diagonal. Untuk $A,B$ Borel,

$$
\mathbb P(X\in A,Y\in B)=\lambda(A\cap B).
$$

Dengan $Q$,

$$
\int_AQ(x,B)\,\lambda(dx)
=\int_A\mathbf1_B(x)\,dx
=\lambda(A\cap B).
$$

Kernel $Q'$ berbeda dari $Q$ hanya pada $x_0$, sehingga integralnya sama.
Jadi keduanya adalah hukum bersyarat $Y$ dengan syarat $X$. Untuk
$B=\{x_0\}$,

$$
Q(x_0,B)=\delta_{x_0}(\{x_0\})=1,
\qquad
Q'(x_0,B)=\delta_0(\{x_0\})=0.
$$

Sekarang misalkan $K$ dan $L$ adalah dua kernel menuju ruang Borel standar
$(T,\mathcal T)$ yang mewakili distribusi bersyarat yang sama. Pilih
sistem-$\pi$ penentu terhitung
$\mathcal C$ yang memuat $T$. Untuk setiap $C\in\mathcal C$, identitas
disintegrasi menyatakan bahwa $K(\cdot,C)$ dan $L(\cdot,C)$ adalah dua versi
fungsi bersyarat yang sama. Maka terdapat himpunan marginal nol $N_C$ tempat
keduanya mungkin berbeda. Gabungan

$$
N=\bigcup_{C\in\mathcal C}N_C
$$

tetap marginal nol. Untuk $x\notin N$, ukuran peluang $K(x,\cdot)$ dan
$L(x,\cdot)$ sepakat pada $\mathcal C$. Teorema sistem-$\pi$–$\lambda$
memberi kesamaan pada seluruh $\mathcal T$. Dengan demikian kedua kernel sama
sebagai ukuran di luar satu himpunan marginal nol, tetapi contoh $Q,Q'$
menunjukkan bahwa kesamaan titik demi titik tidak dapat dituntut.
:::

:::

:::

::: {#hak-dan-provenans-probabilitas-bersyarat .bridge-section}

## Hak dan provenans

Unit **Distribusi bersyarat reguler dan disiplin versi**, termasuk ketiga
latihan, petunjuk, jawaban, dan penyelesaian di atas, merupakan materi asli
berbahasa Indonesia yang disusun untuk edisi ini dan dilisensikan terpisah di
bawah [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), sejauh hak
baru timbul. ID hak komponennya ialah
`rights.o009.original.bridge.regular-conditional-probability.cc-by-4.0`.

Penyusunan unit ini dibantu oleh **OpenAI Codex gpt-5.6-sol, Ultra.** Identitas
model tersebut tidak menggantikan kredit penulis sumber atau kontributor
manusia. Unit ini memperjelas lingkup teorema dan menyatukan prasyarat yang
sudah diperkenalkan di bagian Random Services serta jembatan asli sebelumnya;
ia tidak menyalin prosa donor dan tidak melisensikan ulang Random Services,
QuantEcon, Žitković, MathJax, atau komponen lain. Hak campuran seluruh edisi
tetap dijelaskan dalam `LICENSES.md` dan backend hak per komponen.

Unit ini independen dan tidak didukung atau disahkan oleh penulis Random
Services, QuantEcon, lembaga mereka, atau penulis sumber lain. Secara khusus,
ia tidak mengklaim bahwa keluarga versi per kejadian selalu membentuk kernel,
bahwa nilai bersyarat pada titik marginal nol bersifat kanonik, atau bahwa
ruang terukur sembarang otomatis mempunyai probabilitas bersyarat reguler
untuk seluruh kejadian.

:::

:::
