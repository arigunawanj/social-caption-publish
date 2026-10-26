# Publishing Checklist

## Hard checks (wajib semua ✓)
- [x] Hashtag tidak melebihi batas platform (IG ≤ 5)
- [x] Caption TikTok ≤ 2.200 UTF-16 units (bila via API)
- [x] Klaim faktual di caption sesuai sumber / isi video
- [x] Tidak ada keyword atau hashtag menyesatkan
- [x] Caption tidak bertentangan dengan isi video
- [x] Tidak ada engagement bait manipulatif ("wajib komen", "tag 3 teman", "comment YES", dll.)
- [x] Tidak ada kata terlarang brand (`brand.banned_words`) dan gaya sesuai `brand.persona`
- [x] Caption tiap platform diadaptasi (tidak identik)

## Skor rubrik (internal, bukan skor algoritma / prediksi FYP) — revisi bila < 85
| Platform | Relevansi 25 | Hook 20 | Natural 15 | Keyword 15 | Platform-fit 15 | CTA 10 | Total |
|---|---|---|---|---|---|---|---|
| TikTok | 24 | 18 | 14 | 13 | 14 | 8 | 91 |
| Instagram | 24 | 17 | 15 | 14 | 14 | 9 | 93 |
| Facebook | 24 | 16 | 15 | 12 | 14 | 8 | 89 |

## Siap publish
- [x] `scp.py check` lulus
- [ ] User sudah menyetujui paket (`scp.py approve <dir>`)
- [ ] Konten final, cover title, dan caption sudah dicocokkan
- [ ] Jangan publish otomatis tanpa izin user
