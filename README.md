# Probabilitas Teoretis-Ukuran dan Proses Stokastik — Bahasa Indonesia

Edisi Bahasa Indonesia yang lengkap tentang probabilitas teoretis-ukuran dan proses stokastik: terjemahan 27 halaman
terpilih dari *Random* karya Kyle Siegrist dan delapan unit *Continuous Time Markov Chains* karya Thomas J. Sargent dan
John Stachurski (QuantEcon) beserta 25 latihan dan 25 solusi, ditambah empat jembatan rigor asli, lima laboratorium
yang dapat dijalankan ulang, 36 masalah penguasaan dengan petunjuk, jawaban, dan penyelesaian lengkap, serta dua
formulir penilaian kumulatif dengan pedoman penskoran. Tersedia sebagai pembaca HTML luring dan backend modular.

[Baca daring](https://kokunoyumeto.github.io/measure-theoretic-probability-stochastic-processes-id/)

## Cara pembuatan

Terjemahan, adaptasi, dan materi asli dikerjakan oleh AI: OpenAI Codex gpt-5.6-sol, Ultra. Pembaca HTML dibangun
berulang dengan hasil identik (161 berkas, 7.796.646 byte, manifest SHA-256
`494dc1684132e96563b24a35dcfbd531a4278d4e6614b2cd9f3e04cf8a9be23d`). Backend modular ber-ID stabil memuat 8.871
rekaman (2.538 entitas, 6.333 segmen, 3.256 relasi) tanpa ID ganda, relasi menggantung, atau kegagalan pemeriksaan
(manifest `001edf5160e066adf0af7c0d673ba1a1d0382be2f9c12662ad9148f2f3bef91d`).

## Status

Edisi lengkap (checkpoint 38, 31 Agustus 2026). Kursus O006/C140 dipakai sebagai prasyarat hukum bilangan besar dan
teorema limit pusat tanpa menyalin isinya. PDF A4 (447 halaman) dibangun dari permukaan HTML yang sama dengan
`scripts/build_reader_pdf.py`. Masih mungkin ada kesalahan.

## Isi

- [Pembaca daring](https://kokunoyumeto.github.io/measure-theoretic-probability-stochastic-processes-id/); salinannya ada di `build/site/` (bagian martingal, rantai Markov, dan gerak Brown).
- `source/`: teori Random (`theory/`), komponen QuantEcon (`quantecon/`), jembatan asli (`original/`), laboratorium
  (`labs/`), masalah penguasaan (`mastery/`), formulir penilaian (`assessments/`), dan aplikasi luring (`apps/`).
- `backend/`: backend modular; `authority/`: sumber yang dibekukan (`random/`, `quantecon/`, `zitkovic/`); `qa/`,
  `00_control/`, dan `scripts/`: pemeriksaan, kontrol, dan skrip build.

## Sumber dan atribusi

- Kyle Siegrist, *Random* (Random Services): teori dan tiga halaman ikhtisar (martingal, rantai Markov, gerak Brown);
  URL, jumlah byte, dan SHA-256 dicatat di `authority/random/`.
- Thomas J. Sargent dan John Stachurski, *Continuous Time Markov Chains*, QuantEcon, commit
  `8b06e0aa5a438692445b2c896f9d238c5a7d5eb7`.
- Gordan Žitković, *stochastic-book*, commit `e2b35ad91a3689454ae6455e8ffc510a90760c0d`: potongan donor
  laboratorium.
- MathJax 3.1.2 (MathJax Consortium).
- Edisi ini independen dan tidak didukung atau disahkan oleh penulis sumber, Random Services, QuantEcon, atau lembaga
  mereka.

## Lisensi

Hak campuran per komponen: Random mempertahankan kedua saksi lisensi resminya (CC BY 2.0 dan CC BY 1.0); komponen
QuantEcon dan adaptasinya CC BY-SA 4.0; byte donor Žitković CC0 1.0; MathJax Apache-2.0; terjemahan, adaptasi, koreksi,
laboratorium, jembatan, masalah penguasaan, formulir penilaian, dan materi asli lainnya CC BY 4.0 sejauh hak baru
timbul. Tidak ada lisensi tunggal atas seluruh gabungan. Rincian: [LICENSES.md](LICENSES.md).
