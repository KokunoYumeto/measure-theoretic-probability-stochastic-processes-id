<a id="id-mtp-masteri-martingal-03-04-root"></a>

# Penguasaan Martingal: Masalah 03–04

**Bahasa:** id-ID  
**Prasyarat umum:** nilai harapan bersyarat, filtrasi, martingal yang terintegralkan secara kuadrat, waktu henti, teorema penghentian opsional, dan perubahan ukuran melalui rasio kemungkinan.  
**Capaian umum:** membangun martingal dari informasi yang tersisa, memakai kompensator variasi kuadratik pada waktu henti, serta menghitung galat dan durasi uji sekuensial secara eksak.

**Hak dan asal-usul.** © 2026 kontributor Interlanguage. Materi ini dilisensikan di bawah [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). Masalah 03 dan 04 beserta penyelesaiannya merupakan karya asli untuk berkas ini; keduanya tidak diterjemahkan atau disalin dari contoh sumber. Istilah dasar mengikuti bab lokal tentang martingal dan waktu henti.

**Provenans model:** OpenAI Codex gpt-5.6-sol, Ultra.

---

<a id="id-mtp-martingal-03-root"></a>

## Masalah 03 — Rata-rata yang belum teramati

**Prasyarat:** permutasi acak, nilai harapan bersyarat, martingal dalam \(L^2\), kompensator, dan penghentian opsional pada waktu terbatas.  
**Capaian:** mengenali martingal “informasi tersisa”, menghitung variasi kuadratik terprediksi, dan mengaudit aturan berhenti adaptif secara eksak.

<a id="id-mtp-martingal-03-exercise"></a>

### Soal

Ambil bilangan deterministik \(x_1,\ldots,x_N\in\mathbb R\), dengan \(N\ge2\), dan pilih \(\pi\) secara seragam dari semua permutasi \(\{1,\ldots,N\}\). Definisikan
\[
X_k=x_{\pi(k)},\qquad
\mathcal F_n=\sigma\bigl(\pi(1),\ldots,\pi(n)\bigr),
\]
serta rata-rata nilai yang belum terungkap
\[
R_n=\frac{\sum_{k=n+1}^{N}X_k}{N-n},
\qquad 0\le n\le N-1.
\]

1. Buktikan bahwa \((R_n,\mathcal F_n)_{0\le n\le N-1}\) adalah martingal.
2. Untuk \(0\le n\le N-2\), tetapkan \(m=N-n\) dan
   \[
   v_n=\frac{1}{m(m-1)^2}
   \sum_{j\notin\{\pi(1),\ldots,\pi(n)\}}(x_j-R_n)^2.
   \]
   Buktikan bahwa
   \[
   K_n=(R_n-R_0)^2-\sum_{j=0}^{n-1}v_j,
   \qquad 0\le n\le N-1,
   \]
   adalah martingal. Simpulkan bahwa, untuk setiap waktu henti \(\rho\le N-1\),
   \[
   \mathbb E R_\rho=R_0,
   \qquad
   \mathbb E(R_\rho-R_0)^2
   =\mathbb E\!\left[\sum_{j=0}^{\rho-1}v_j\right].
   \]
3. Terapkan hasil tersebut pada populasi berlabel yang nilainya \((-3,-1,2,2)\). Definisikan
   \[
   \tau=\min\Bigl(
   \{n\in\{1,2,3\}:R_n\notin(-1,1)\}\cup\{3\}
   \Bigr).
   \]
   Tentukan hukum \(R_\tau\) secara eksak, lalu verifikasi kedua identitas pada bagian 2.

<a id="id-mtp-martingal-03-hint-1"></a>

### Petunjuk 1

Jika terdapat \(m=N-n\) nilai tersisa, maka pengungkapan berikutnya seragam di antara nilai-nilai itu. Karena itu,
\(
\mathbb E(X_{n+1}\mid\mathcal F_n)=R_n.
\)

<a id="id-mtp-martingal-03-hint-2"></a>

### Petunjuk 2

Tuliskan
\[
R_{n+1}=\frac{mR_n-X_{n+1}}{m-1},
\qquad
R_{n+1}-R_n=\frac{R_n-X_{n+1}}{m-1}.
\]
Kuadratkan persamaan kedua dan kondisikan pada \(\mathcal F_n\).

<a id="id-mtp-martingal-03-hint-3"></a>

### Petunjuk 3

Untuk bagian konkret, ada \(4!/2!=12\) urutan nilai yang berbeda dan semuanya berpeluang \(1/12\). Hentikan setiap urutan segera setelah rata-rata sisa keluar dari \((-1,1)\), atau pada waktu 3.

<a id="id-mtp-martingal-03-answer"></a>

### Jawaban ringkas

Proses \(R\) dan \(K\) adalah martingal. Untuk populasi \((-3,-1,2,2)\),
\[
\begin{array}{c|ccccc}
r&-3&-2&-1&1&2\\ \hline
\mathbb P(R_\tau=r)&\frac16&\frac16&\frac1{12}&\frac14&\frac13
\end{array}
\]
sehingga
\[
\mathbb E R_\tau=0=R_0,
\qquad
\mathbb E(R_\tau-R_0)^2=\frac{23}{6}
=\mathbb E\!\left[\sum_{j=0}^{\tau-1}v_j\right].
\]

<a id="id-mtp-martingal-03-solution"></a>

### Solusi lengkap

Setelah \(n\) pengungkapan, terdapat \(m=N-n\) indeks tersisa. Bersyarat pada \(\mathcal F_n\), indeks \(\pi(n+1)\) seragam pada himpunan tersebut. Jadi
\[
\mathbb E(X_{n+1}\mid\mathcal F_n)
=\frac1m\sum_{j\notin\{\pi(1),\ldots,\pi(n)\}}x_j
=R_n.
\]
Jumlah nilai tersisa sebelum pengungkapan adalah \(mR_n\). Sesudah \(X_{n+1}\) dikeluarkan, rata-ratanya menjadi
\[
R_{n+1}=\frac{mR_n-X_{n+1}}{m-1}.
\]
Oleh karena itu,
\[
\mathbb E(R_{n+1}\mid\mathcal F_n)
=\frac{mR_n-\mathbb E(X_{n+1}\mid\mathcal F_n)}{m-1}
=R_n.
\]
Semua peubah hanya mengambil nilai dalam suatu himpunan hingga, sehingga integrabilitas tidak menjadi masalah; ini membuktikan bagian 1.

Definisikan \(D_{n+1}=R_{n+1}-R_n\). Dari identitas di atas,
\[
D_{n+1}=\frac{R_n-X_{n+1}}{m-1},
\qquad
\mathbb E(D_{n+1}\mid\mathcal F_n)=0,
\]
dan
\[
\mathbb E(D_{n+1}^2\mid\mathcal F_n)
=\frac{1}{m(m-1)^2}
  \sum_{j\notin\{\pi(1),\ldots,\pi(n)\}}(x_j-R_n)^2
=v_n.
\]
Karena \(R_n-R_0\) terukur terhadap \(\mathcal F_n\),
\[
\begin{aligned}
\mathbb E\bigl((R_{n+1}-R_0)^2\mid\mathcal F_n\bigr)
&=(R_n-R_0)^2
  +2(R_n-R_0)\mathbb E(D_{n+1}\mid\mathcal F_n)
  +\mathbb E(D_{n+1}^2\mid\mathcal F_n)\\
&=(R_n-R_0)^2+v_n.
\end{aligned}
\]
Maka \(K\) adalah martingal. Waktu \(\rho\le N-1\) terbatas, sehingga penghentian opsional pada \(R\) dan \(K\) memberi
\[
\mathbb E R_\rho=\mathbb E R_0=R_0,
\qquad
0=\mathbb E K_\rho
=\mathbb E(R_\rho-R_0)^2
 -\mathbb E\!\left[\sum_{j=0}^{\rho-1}v_j\right].
\]

Sekarang ambil populasi \((-3,-1,2,2)\). Jumlahnya nol, jadi \(R_0=0\). Aturan yang mendefinisikan \(\tau\) hanya memakai \(R_1,\ldots,R_n\) untuk memutuskan apakah berhenti sebelum atau pada \(n\); jadi \(\tau\) adalah waktu henti dan \(\tau\le3\).

Kedua belas urutan nilai mempunyai peluang yang sama. Penghitungan menurut nilai terminal memberi
\[
\begin{array}{c|ccccc}
R_\tau&-3&-2&-1&1&2\\ \hline
\text{banyak urutan}&2&2&1&3&4.
\end{array}
\]
Sebagai pemeriksaan terhadap penghentian dini: tiga urutan yang dimulai dengan \(-3\) berhenti pada \(R_1=1\); urutan yang dimulai dengan \((-1,-3)\) berhenti pada \(R_2=2\); dan dua urutan yang dimulai dengan \((2,2)\) berhenti pada \(R_2=-2\). Enam urutan lain mencapai waktu 3 dan memberikan frekuensi terminal selebihnya yang tercantum pada tabel. Dengan demikian hukum pada jawaban ringkas berlaku. Akhirnya,
\[
\mathbb E R_\tau
=-3\!\left(\frac16\right)-2\!\left(\frac16\right)
-\frac1{12}+\frac14+2\!\left(\frac13\right)=0,
\]
dan
\[
\mathbb E R_\tau^2
=9\!\left(\frac16\right)+4\!\left(\frac16\right)
+\frac1{12}+\frac14+4\!\left(\frac13\right)
=\frac{23}{6}.
\]
Identitas martingal yang telah dibuktikan kemudian memberikan
\(
\mathbb E\sum_{j=0}^{\tau-1}v_j=23/6
\), tanpa perlu menghitung setiap lintasan kompensator secara terpisah.

---

<a id="id-mtp-martingal-04-root"></a>

## Masalah 04 — Uji rasio kemungkinan yang berhenti tepat di batas

**Prasyarat:** turunan Radon–Nikodym pada filtrasi, martingal rasio kemungkinan, waktu henti, dan penghentian opsional.  
**Capaian:** memperoleh probabilitas galat dan ekspektasi ukuran sampel suatu uji sekuensial tanpa aproksimasi pelampauan batas (*overshoot*).

<a id="id-mtp-martingal-04-exercise"></a>

### Soal

Pada ruang kanonik \(\{0,1\}^{\mathbb N}\), misalkan \(X_1,X_2,\ldots\) adalah koordinat, \(S_n=\sum_{k=1}^nX_k\), dan \(\mathcal F_n=\sigma(X_1,\ldots,X_n)\). Pertimbangkan dua ukuran peluang:
\[
H_0:\quad \mathbb P_0(X_k=1)=\frac13,
\qquad
H_1:\quad \mathbb P_1(X_k=1)=\frac23,
\]
dengan koordinat i.i.d. di bawah masing-masing ukuran. Definisikan
\[
L_n=\frac{d\mathbb P_1|_{\mathcal F_n}}
          {d\mathbb P_0|_{\mathcal F_n}}
=2^{2S_n-n},
\qquad
Y_n=\log_2L_n=2S_n-n.
\]
Untuk \(a,b\in\mathbb N_+\), hentikan pengamatan pada
\[
\tau=\inf\{n\ge0:Y_n\in\{-a,b\}\}.
\]
Pilih \(H_1\) jika \(Y_\tau=b\), dan pilih \(H_0\) jika \(Y_\tau=-a\).

1. Buktikan bahwa \((L_n,\mathcal F_n)\) adalah martingal di bawah \(\mathbb P_0\), serta \(\mathbb E_i\tau<\infty\) untuk \(i=0,1\).
2. Hitung secara eksak galat tipe I
   \(\alpha=\mathbb P_0(Y_\tau=b)\)
   dan galat tipe II
   \(\beta=\mathbb P_1(Y_\tau=-a)\).
3. Hitung \(\mathbb E_0\tau\) dan \(\mathbb E_1\tau\). Evaluasi semua hasil untuk \((a,b)=(2,3)\).

<a id="id-mtp-martingal-04-hint-1"></a>

### Petunjuk 1

Di bawah \(\mathbb P_0\), faktor \(L_{n+1}/L_n\) bernilai \(2\) dengan peluang \(1/3\) dan \(1/2\) dengan peluang \(2/3\). Nilai harapan bersyarat faktor itu adalah 1.

<a id="id-mtp-martingal-04-hint-2"></a>

### Petunjuk 2

Karena loncatan \(Y\) selalu \(\pm1\), tidak ada pelampauan batas (*overshoot*) dan
\(2^{-a}\le L_{\tau\wedge n}\le2^b\).
Gunakan \(\mathbb E_0L_\tau=1\), lalu gunakan
\[
\mathbb P_1(A)=\mathbb E_0[L_\tau\mathbf1_A],
\qquad A\in\mathcal F_\tau.
\]

<a id="id-mtp-martingal-04-hint-3"></a>

### Petunjuk 3

Di bawah \(\mathbb P_0\), proses \(Y_n+n/3\) adalah martingal; di bawah \(\mathbb P_1\), proses \(Y_n-n/3\) adalah martingal. Hentikan kedua proses itu pada \(\tau\).

<a id="id-mtp-martingal-04-answer"></a>

### Jawaban ringkas

Dengan \(D=2^{a+b}-1\),
\[
\alpha=\frac{2^a-1}{D},
\qquad
\beta=\frac{2^b-1}{D},
\]
dan
\[
\mathbb E_0\tau=3\bigl[a-(a+b)\alpha\bigr],
\qquad
\mathbb E_1\tau=3\bigl[b-(a+b)\beta\bigr].
\]
Untuk \((a,b)=(2,3)\),
\[
\alpha=\frac3{31},\qquad
\beta=\frac7{31},\qquad
\mathbb E_0\tau=\frac{141}{31},\qquad
\mathbb E_1\tau=\frac{174}{31}.
\]

<a id="id-mtp-martingal-04-solution"></a>

### Solusi lengkap

Untuk satu pengamatan,
\[
\frac{L_{n+1}}{L_n}
=\begin{cases}
2,&X_{n+1}=1,\\[2mm]
\frac12,&X_{n+1}=0.
\end{cases}
\]
Karena \(X_{n+1}\) independen dari \(\mathcal F_n\) di bawah \(\mathbb P_0\),
\[
\mathbb E_0\!\left(\frac{L_{n+1}}{L_n}\,\middle|\,\mathcal F_n\right)
=\frac13(2)+\frac23\left(\frac12\right)=1.
\]
Jadi \(L\) adalah martingal nonnegatif di bawah \(\mathbb P_0\).

Selanjutnya, ambil \(m=a+b\). Dari setiap keadaan di antara kedua batas, rangkaian \(m\) buah nol pasti membawa \(Y\) ke \(-a\) sebelum blok selesai. Di bawah masing-masing ukuran, peluang bersyarat terjadinya rangkaian itu sedikitnya
\(c=(1/3)^m>0\). Dengan sifat independen pada blok berturut-turut,
\[
\mathbb P_i(\tau>km)\le(1-c)^k,
\qquad k\ge0,\quad i\in\{0,1\}.
\]
Akibatnya \(\tau<\infty\) hampir pasti dan
\(
\mathbb E_i\tau\le m\sum_{k\ge0}(1-c)^k=m/c<\infty
\).

Loncatan \(Y\) adalah \(+1\) atau \(-1\), sehingga \(Y_\tau\) tepat sama dengan \(b\) atau \(-a\). Lebih lanjut,
\[
2^{-a}\le L_{\tau\wedge n}\le2^b.
\]
Penghentian opsional pada \(\tau\wedge n\), disusul penerapan teorema konvergensi terdominasi, memberikan \(\mathbb E_0L_\tau=1\). Maka
\[
1=2^b\alpha+2^{-a}(1-\alpha),
\]
sehingga
\[
\alpha
=\frac{1-2^{-a}}{2^b-2^{-a}}
=\frac{2^a-1}{2^{a+b}-1}.
\]

Untuk melakukan perubahan ukuran pada waktu acak, jika \(A\in\mathcal F_\tau\), maka
\(A\cap\{\tau=n\}\in\mathcal F_n\). Karena \(L_n=d\mathbb P_1/d\mathbb P_0\) pada \(\mathcal F_n\), penjumlahan terhadap \(n\) memberi
\[
\mathbb P_1(A)=\mathbb E_0[L_\tau\mathbf1_A].
\]
Ambil \(A=\{Y_\tau=-a\}\). Pada \(A\), \(L_\tau=2^{-a}\), jadi
\[
\beta=2^{-a}(1-\alpha)
=\frac{2^b-1}{2^{a+b}-1}.
\]

Di bawah \(\mathbb P_0\), inkremen \(Y\) mempunyai rata-rata
\[
\frac13(1)+\frac23(-1)=-\frac13,
\]
sedangkan di bawah \(\mathbb P_1\) rata-ratanya \(+1/3\). Karena \(\mathbb E_i\tau<\infty\), penghentian proses
\(Y_n+n/3\) di bawah \(\mathbb P_0\) dan
\(Y_n-n/3\) di bawah \(\mathbb P_1\) sah. Secara eksplisit, terapkan dahulu pada \(\tau\wedge n\); lalu gunakan \(|Y_{\tau\wedge n}|\le\max(a,b)\) dan \(\tau\wedge n\to\tau\) dalam \(L^1\). Diperoleh
\[
\mathbb E_0Y_\tau=-\frac13\mathbb E_0\tau,
\qquad
\mathbb E_1Y_\tau=\frac13\mathbb E_1\tau.
\]
Karena
\[
\mathbb E_0Y_\tau=b\alpha-a(1-\alpha),
\qquad
\mathbb E_1Y_\tau=b(1-\beta)-a\beta,
\]
maka
\[
\mathbb E_0\tau=3\bigl[a-(a+b)\alpha\bigr],
\qquad
\mathbb E_1\tau=3\bigl[b-(a+b)\beta\bigr].
\]
Substitusi \(a=2\), \(b=3\), dan \(2^{a+b}-1=31\) menghasilkan
\[
\alpha=\frac3{31},\quad
\beta=\frac7{31},\quad
\mathbb E_0\tau=3\left(2-5\frac3{31}\right)=\frac{141}{31},\quad
\mathbb E_1\tau=3\left(3-5\frac7{31}\right)=\frac{174}{31}.
\]
