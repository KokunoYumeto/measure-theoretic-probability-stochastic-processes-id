---
lang: id-ID
title: "Martingal mundur dan pelupaan kuantitatif pada rantai Markov reversibel"
license: CC-BY-4.0
model_disclosure: "OpenAI Codex gpt-5.6-sol, Ultra."
---

# Martingal mundur dan pelupaan kuantitatif pada rantai Markov reversibel {#id-mtp-masteri-martingal-05}

## Prasyarat {#id-mtp-masteri-martingal-05-prasyarat}

Pembaca diharapkan menguasai nilai harapan bersyarat, sifat menara, rantai Markov homogen pada ruang keadaan berhingga, distribusi stasioner, kesetimbangan terperinci, norma \(L^2\), serta teorema konvergensi martingal mundur.

## Capaian pembelajaran {#id-mtp-masteri-martingal-05-capaian}

Setelah menyelesaikan latihan ini, pembaca dapat:

1. mengenali nilai harapan bersyarat terhadap filtrasi yang menurun sebagai martingal mundur;
2. mengubah pembalikan waktu rantai Markov reversibel menjadi identitas operator yang eksplisit;
3. menurunkan laju pelupaan \(L^2\) dan batas probabilitas dari celah spektral; dan
4. membuktikan trivialitas aljabar-\(\sigma\) ekor tanpa menggunakan waktu henti atau teorema penghentian opsional.

## Latihan {#id-mtp-masteri-martingal-05-latihan}

Misalkan \((X_n)_{n\ge 0}\) adalah rantai Markov stasioner pada himpunan berhingga \(E\), dengan matriks transisi \(P\) dan distribusi stasioner \(\pi\) yang memenuhi \(\pi(x)>0\) untuk setiap \(x\in E\). Operator transisi bekerja pada fungsi \(h:E\to\mathbb R\) melalui

\[
 (Ph)(x)=\sum_{y\in E}P(x,y)h(y).
\]

Andaikan rantai reversibel,

\[
 \pi(x)P(x,y)=\pi(y)P(y,x),\qquad x,y\in E,
\]

dan terdapat \(\rho\in[0,1)\) sehingga

\[
 \|Ph\|_{2,\pi}\le \rho\|h\|_{2,\pi}
 \quad\text{untuk setiap }h\text{ dengan }\pi(h)=0,
 \tag{1}
\]

dengan

\[
 \pi(h)=\sum_{x\in E}\pi(x)h(x),
 \qquad
 \|h\|_{2,\pi}^2=\sum_{x\in E}\pi(x)h(x)^2.
\]

Untuk \(n\ge0\), definisikan aljabar-\(\sigma\) masa depan

\[
 \mathcal G_n=\sigma(X_n,X_{n+1},X_{n+2},\ldots),
 \qquad
 \mathcal G_\infty=\bigcap_{n\ge0}\mathcal G_n.
\]

Ambil \(f:E\to\mathbb R\) dengan \(\pi(f)=0\), lalu tetapkan

\[
 Y_n=\mathbb E[f(X_0)\mid\mathcal G_n].
\]

Kerjakan semua bagian berikut.

1. Buktikan bahwa \((Y_n,\mathcal G_n)_{n\ge0}\) adalah martingal mundur dan bahwa
   \[
   Y_n=(P^nf)(X_n).
   \tag{2}
   \]
2. Buktikan batas kuantitatif
   \[
   \mathbb E(Y_n^2)\le \rho^{2n}\|f\|_{2,\pi}^2,
   \qquad
   \mathbb P(|Y_n|\ge t)
   \le \min\!\left\{1,\frac{\rho^{2n}\|f\|_{2,\pi}^2}{t^2}\right\}
   \quad(t>0).
   \tag{3}
   \]
   Identifikasikan limit hampir pastinya dan limit \(L^2\) dari \(Y_n\).
3. Buktikan bahwa \(\mathcal G_\infty\) trivial modulo himpunan nol: untuk setiap \(A\in\mathcal G_\infty\), berlaku \(\mathbb P(A)\in\{0,1\}\).
4. Khusus untuk \(E=\{0,1\}\), ambil
   \[
   P=
   \begin{pmatrix}
   1-a & a\\
   b & 1-b
   \end{pmatrix},
   \qquad a,b\in(0,1).
   \]
   Dengan \(p=a/(a+b)\), \(\lambda=1-a-b\), dan \(f(x)=x-p\), tentukan \(Y_n\), \(\mathbb E(Y_n^2)\), serta \(\mathbb P(|Y_n|\ge t)\) secara eksak.

## Petunjuk 1 {#id-mtp-masteri-martingal-05-petunjuk-1}

Mulailah dari inklusi \(\mathcal G_{n+1}\subseteq\mathcal G_n\) dan sifat menara. Untuk (2), gunakan dua fakta secara berurutan: masa lalu dan masa depan saling bebas bersyarat pada \(X_n\), lalu pembalikan waktu rantai stasioner reversibel memiliki matriks transisi yang sama dengan \(P\).

## Petunjuk 2 {#id-mtp-masteri-martingal-05-petunjuk-2}

Untuk \(j\in E\), hitung langsung

\[
 \mathbb E[f(X_0)\mid X_n=j]
 =\frac{1}{\pi(j)}\sum_{i\in E}\pi(i)P^n(i,j)f(i).
\]

Kesetimbangan terperinci juga berlaku untuk \(P^n\). Setelah memperoleh (2), gunakan stasioneritas \(X_n\sim\pi\), iterasi (1), dan pertidaksamaan Chebyshev.

## Petunjuk 3 {#id-mtp-masteri-martingal-05-petunjuk-3}

Untuk trivialitas ekor, ambil \(A\in\mathcal G_\infty\), \(B\in\mathcal F_m:=\sigma(X_0,\ldots,X_m)\), dan \(n>m\). Definisikan

\[
 q_n(x)=\mathbb P(A\mid X_n=x),
 \qquad r=\mathbb P(A).
\]

Tunjukkan bahwa \(\pi(q_n)=r\) dan

\[
 \mathbb E[\mathbf 1_A\mid\mathcal F_m]
 =P^{\,n-m}q_n(X_m).
\]

Terapkan (1) pada \(q_n-r\), kemudian biarkan \(n\to\infty\). Terakhir, perluas independensi dari semua kejadian silinder ke \(\sigma(X_0,X_1,\ldots)\) dengan teorema kelas monoton.

## Jawaban ringkas {#id-mtp-masteri-martingal-05-jawaban}

Keluarga \((\mathcal G_n)\) menurun dan sifat menara memberi \(\mathbb E(Y_n\mid\mathcal G_{n+1})=Y_{n+1}\). Reversibilitas memberi

\[
 Y_n=(P^nf)(X_n).
\]

Akibatnya,

\[
 \|Y_n\|_2=\|P^nf\|_{2,\pi}
 \le\rho^n\|f\|_{2,\pi},
\]

sehingga \(Y_n\to0\) hampir pasti dan dalam \(L^2\), serta (3) mengikuti dari Chebyshev. Kontraksi yang sama menunjukkan bahwa setiap kejadian ekor independen dari setiap blok berhingga; jadi kejadian itu independen dari dirinya sendiri dan berpeluang 0 atau 1.

Dalam kasus dua keadaan,

\[
 Y_n=\lambda^n(X_n-p),
 \qquad
 \mathbb E(Y_n^2)=\lambda^{2n}p(1-p),
\]

dan, untuk \(t>0\),

\[
 \mathbb P(|Y_n|\ge t)
 =(1-p)\mathbf 1_{\{|\lambda|^np\ge t\}}
 +p\mathbf 1_{\{|\lambda|^n(1-p)\ge t\}}.
\]

## Solusi lengkap {#id-mtp-masteri-martingal-05-solusi}

### 1. Struktur martingal mundur dan rumus pembalikan waktu

Jelas bahwa \(\mathcal G_{n+1}\subseteq\mathcal G_n\). Peubah \(Y_n\) terukur terhadap \(\mathcal G_n\) dan terintegralkan karena \(E\) berhingga. Dengan sifat menara,

\[
 \mathbb E[Y_n\mid\mathcal G_{n+1}]
 =\mathbb E\!\left[
   \mathbb E[f(X_0)\mid\mathcal G_n]
   \mathrel{\Big|}\mathcal G_{n+1}
 \right]
 =\mathbb E[f(X_0)\mid\mathcal G_{n+1}]
 =Y_{n+1}.
\]

Jadi, \((Y_n,\mathcal G_n)\) adalah martingal mundur.

Untuk \(n\ge1\), sifat Markov menyatakan bahwa, bersyarat pada \(X_n\), masa lalu \(\sigma(X_0,\ldots,X_{n-1})\) dan masa depan \(\sigma(X_{n+1},X_{n+2},\ldots)\) saling bebas. Oleh karena itu,

\[
 Y_n=\mathbb E[f(X_0)\mid X_n].
\tag{4}
\]

Untuk \(n=0\), identitas yang sama berlaku langsung karena
\(Y_0=f(X_0)=P^0f(X_0)\).

Untuk \(j\in E\), stasioneritas dan rumus Bayes memberikan

\[
\begin{aligned}
 \mathbb E[f(X_0)\mid X_n=j]
 &=\sum_{i\in E}f(i)
   \frac{\mathbb P(X_0=i,X_n=j)}{\mathbb P(X_n=j)}\\
 &=\frac{1}{\pi(j)}
   \sum_{i\in E}f(i)\pi(i)P^n(i,j).
\end{aligned}
\tag{5}
\]

Kesetimbangan terperinci untuk \(P\) menyiratkan kesetimbangan terperinci untuk setiap pangkatnya:

\[
 \pi(i)P^n(i,j)=\pi(j)P^n(j,i).
\]

Memasukkannya ke (5) menghasilkan

\[
 \mathbb E[f(X_0)\mid X_n=j]
 =\sum_{i\in E}P^n(j,i)f(i)
 =(P^nf)(j).
\]

Bersama (4), ini membuktikan (2).

### 2. Pelupaan kuantitatif dan identifikasi limit

Karena \(X_n\sim\pi\), identitas (2) memberi

\[
 \mathbb E(Y_n^2)
 =\sum_{x\in E}\pi(x)(P^nf(x))^2
 =\|P^nf\|_{2,\pi}^2.
\]

Rata-rata \(\pi\) dipertahankan oleh \(P\), sehingga \(\pi(P^kf)=\pi(f)=0\) untuk setiap \(k\). Karena itu, (1) dapat diiterasikan:

\[
 \|P^nf\|_{2,\pi}
 \le\rho^n\|f\|_{2,\pi}.
\]

Setelah dikuadratkan, diperoleh bagian pertama (3). Pertidaksamaan Chebyshev memberi

\[
 \mathbb P(|Y_n|\ge t)
 \le \frac{\mathbb E(Y_n^2)}{t^2}
 \le \frac{\rho^{2n}\|f\|_{2,\pi}^2}{t^2};
\]

menggabungkannya dengan batas trivial 1 menghasilkan bagian kedua (3).

Teorema konvergensi martingal mundur menyatakan bahwa

\[
 Y_n\longrightarrow
 Y_\infty:=\mathbb E[f(X_0)\mid\mathcal G_\infty]
\]

hampir pasti dan dalam \(L^2\). Di sisi lain, batas norma di atas menyatakan \(Y_n\to0\) dalam \(L^2\). Keunikan limit dalam probabilitas lalu memberi

\[
 \mathbb E[f(X_0)\mid\mathcal G_\infty]=0
 \quad\text{hampir pasti},
\]

dan \(Y_n\to0\) baik hampir pasti maupun dalam \(L^2\).

### 3. Trivialitas aljabar-\(\sigma\) ekor

Ambil \(A\in\mathcal G_\infty\), tetapkan \(r=\mathbb P(A)\), dan definisikan, untuk setiap \(n\),

\[
 q_n(x)=\mathbb P(A\mid X_n=x),\qquad x\in E.
\]

Karena \(0\le q_n\le1\) dan \(X_n\sim\pi\),

\[
 \pi(q_n)=\mathbb E[q_n(X_n)]=\mathbb P(A)=r,
 \qquad
 \|q_n-r\|_{2,\pi}\le1.
 \tag{6}
\]

Tetapkan \(m\ge0\), ambil \(B\in\mathcal F_m:=\sigma(X_0,\ldots,X_m)\), dan pilih sembarang \(n>m\). Karena \(A\in\mathcal G_\infty\subseteq\mathcal G_n\), sifat Markov memberi

\[
 \mathbb E[\mathbf1_A\mid\mathcal F_n]=q_n(X_n).
\]

Dengan mengondisikan sekali lagi pada \(\mathcal F_m\),

\[
 \mathbb E[\mathbf1_A\mid\mathcal F_m]
 =\mathbb E[q_n(X_n)\mid\mathcal F_m]
 =P^{\,n-m}q_n(X_m).
 \tag{7}
\]

Gunakan (7), lalu kurangi \(\mathbb P(B)r\):

\[
\begin{aligned}
 \left|\mathbb P(A\cap B)-r\mathbb P(B)\right|
 &=\left|
   \mathbb E\!\left[
      \mathbf1_B P^{\,n-m}(q_n-r)(X_m)
   \right]
 \right|\\
 &\le \|\mathbf1_B\|_2
       \|P^{\,n-m}(q_n-r)(X_m)\|_2\\
 &\le \rho^{\,n-m}\|q_n-r\|_{2,\pi}\\
 &\le \rho^{\,n-m}.
\end{aligned}
\tag{8}
\]

Ruas kiri (8) tidak bergantung pada \(n\), sedangkan ruas kanan menuju nol. Jadi \(A\) independen dari setiap \(\mathcal F_m\). Karena kejadian-kejadian dalam \(\bigcup_m\mathcal F_m\) membentuk aljabar yang membangkitkan

\[
 \mathcal F_\infty^{\mathrm{jalur}}
 :=\sigma(X_0,X_1,\ldots),
\]

teorema kelas monoton memperluas independensi itu ke seluruh \(\mathcal F_\infty^{\mathrm{jalur}}\). Namun \(A\in\mathcal G_\infty\subseteq\mathcal F_\infty^{\mathrm{jalur}}\). Dengan memilih kejadian kedua juga \(A\), diperoleh

\[
 \mathbb P(A)=\mathbb P(A\cap A)=\mathbb P(A)^2.
\]

Maka \(\mathbb P(A)\in\{0,1\}\), sebagaimana diminta.

### 4. Perhitungan eksak untuk rantai dua keadaan

Distribusi stasionernya adalah

\[
 \pi(1)=p=\frac{a}{a+b},
 \qquad
 \pi(0)=1-p=\frac{b}{a+b}.
\]

Ruang fungsi yang bermean nol terhadap \(\pi\) berdimensi satu. Untuk \(f(x)=x-p\), perhitungan langsung memberi

\[
 Pf=\lambda f,
 \qquad \lambda=1-a-b.
\]

Karena \(a,b\in(0,1)\), berlaku \(|\lambda|<1\); dalam (1) dapat diambil \(\rho=|\lambda|\). Dari (2),

\[
 Y_n=(P^nf)(X_n)=\lambda^n(X_n-p).
\]

Selanjutnya, \(\mathbb E[(X_n-p)^2]=p(1-p)\), sehingga

\[
 \mathbb E(Y_n^2)=\lambda^{2n}p(1-p).
\]

Terakhir, \(X_n=0\) dengan probabilitas \(1-p\) dan \(X_n=1\) dengan probabilitas \(p\). Pada kedua kejadian itu, berturut-turut,

\[
 |Y_n|=|\lambda|^np
 \quad\text{dan}\quad
 |Y_n|=|\lambda|^n(1-p).
\]

Jadi, untuk setiap \(t>0\), probabilitas eksaknya adalah

\[
 \boxed{
 \mathbb P(|Y_n|\ge t)
 =(1-p)\mathbf1_{\{|\lambda|^np\ge t\}}
 +p\mathbf1_{\{|\lambda|^n(1-p)\ge t\}}
 }.
\]

Kasus eksplisit ini memperlihatkan bahwa laju geometrik bukan sekadar artefak pembuktian: untuk fungsi observasi yang merupakan fungsi eigen, faktor \(|\lambda|^n\) tepat.

## Hak dan provenans {#id-mtp-masteri-martingal-05-hak-provenans}

Latihan, susunan subsoal, petunjuk, jawaban, dan solusi ini ditulis secara orisinal dalam bahasa Indonesia (id-ID) untuk materi penguasaan ini. Landasan teorinya adalah definisi serta teorema konvergensi martingal mundur pada [teori martingal mundur](../theory/martingales/Backwards.html); konstruksi pelupaan spektral, pembuktian trivialitas ekor, dan spesialisasi dua keadaan di atas bukan salinan dari contoh pada sumber tersebut. Materi ini tidak menggunakan teorema penghentian opsional.

Hak cipta © 2026 para kontributor. Dilisensikan berdasarkan [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.id). Anda boleh membagikan dan mengadaptasi materi ini untuk tujuan apa pun dengan atribusi yang sesuai, pranala lisensi, dan penandaan perubahan.
