# Probabilitas Teoretis-Ukuran dan Proses Stokastik — Bahasa Indonesia

Repositori ini memuat edisi bahasa Indonesia yang sedang diproduksi untuk
peran kurikulum **O009/D30**. Pembaca yang telah diverifikasi tersedia di
[GitHub Pages](https://kokunoyumeto.github.io/measure-theoretic-probability-stochastic-processes-id/).

Status saat ini: **aktif dan belum merupakan korpus lengkap**. Sepuluh batas
pembaca telah diterbitkan: 15 unit teori Random dan dua laboratorium yang dapat
dijalankan ulang. Sumber lengkap delapan bab *Continuous Time Markov Chains*
dari QuantEcon, pasangan 25 latihan/25 solusi, notebook, aset terpilih, dan
lingkungan Python luringnya juga telah dibekukan dan diverifikasi; terjemahan
komponen tersebut belum dimulai. Unit selanjutnya diterjemahkan secara berurutan.
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
disimpan di repositori. Wheelhouse Python 180 MB dipertahankan secara lokal;
lock ber-hash dan manifest setiap wheel dicatat di repositori.

```text
python scripts/build_first_boundary.py
python scripts/build_first_boundary.py --check
python scripts/build_backend.py
python scripts/verify_published_site.py build/site
python scripts/verify_quantecon_authority.py --check
python scripts/freeze_quantecon_environment.py --resolver tmp/quantecon-resolve-env/Scripts/python.exe --replay tmp/quantecon-offline-replay --output authority/quantecon/environment --check
python scripts/verify_quantecon_native_build.py --check
```

## Hak dan atribusi

Tidak ada klaim lisensi tunggal untuk seluruh gabungan. Komponen Random,
potongan donor Žitković, MathJax, terjemahan/adaptasi, dan materi asli memiliki
hak yang dicatat terpisah. Lihat [LICENSES.md](LICENSES.md), atribusi pada setiap
unit, serta rekaman mesin di `backend/`.

Ini adalah edisi independen dan tidak didukung atau disahkan oleh para penulis
sumber maupun lembaga mereka.
