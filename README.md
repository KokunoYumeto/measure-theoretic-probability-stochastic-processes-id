# Probabilitas Teoretis-Ukuran dan Proses Stokastik — Bahasa Indonesia

Repositori ini memuat edisi bahasa Indonesia yang sedang diproduksi untuk
peran kurikulum **O009/D30**. Pembaca yang telah diverifikasi tersedia di
[GitHub Pages](https://kokunoyumeto.github.io/measure-theoretic-probability-stochastic-processes-id/).

Status saat ini: **aktif dan belum merupakan korpus lengkap**. Batas pembaca
pertama memuat unit kekonvergenan kejadian dan peubah acak, sebuah laboratorium
Monte Carlo yang dapat dijalankan ulang, serta latihan penguasaan dengan
petunjuk, jawaban, dan solusi. Unit selanjutnya diterjemahkan secara berurutan.
Modul pengambilan sampel, hukum bilangan besar, dan teorema limit pusat dari
jalur O006/C140 dipakai sebagai prasyarat bersama dan tidak diduplikasi di sini.

## Isi repositori

- `source/`: sumber pembaca dan laboratorium id-ID yang dapat diedit.
- `backend/`: indeks modular JSONL/CSV dengan ID netral-lokal, relasi, hak, dan
  ikatan hash.
- `authority/`: cuplikan sumber dan saksi hak yang dibatasi; arsip besar dan
  runtime lokal sengaja tidak dimasukkan ke Git.
- `scripts/`: pembeku otoritas, pembangun, dan pemeriksa deterministik.
- `build/site/`: pembaca HTML luring yang telah diverifikasi dan diterbitkan.
- `00_control/`: tujuan, keputusan, kursor, log QA, dan bukti pemulihan.

## Reproduksi batas pembaca

Lingkungan yang dibekukan tercatat dalam `00_control/RUNTIME_LOCK.json`.
Pembangunan lokal memakai Python, Pandoc, dan R 4.6.1; runtime/installer R tidak
disimpan di repositori.

```text
python scripts/build_first_boundary.py
python scripts/build_first_boundary.py --check
python scripts/build_backend.py
python scripts/verify_published_site.py build/site
```

## Hak dan atribusi

Tidak ada klaim lisensi tunggal untuk seluruh gabungan. Komponen Random,
potongan donor Žitković, MathJax, terjemahan/adaptasi, dan materi asli memiliki
hak yang dicatat terpisah. Lihat [LICENSES.md](LICENSES.md), atribusi pada setiap
unit, serta rekaman mesin di `backend/`.

Ini adalah edisi independen dan tidak didukung atau disahkan oleh para penulis
sumber maupun lembaga mereka.

