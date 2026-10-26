#!/usr/bin/env python3
"""
scp.py — CLI skill social-caption-publish (Python 3, tanpa dependensi eksternal)

  init    <dir> [--force] [--brand NAME] [--handle @x] [--lang id] [--region ID]
                  siapkan <dir>/publishing/ dari template
  check   <dir>   validasi caption & hashtag TikTok, Instagram Reels, Facebook Reels → publishing/caption-qc.md
  approve <dir> [--note ..]   catat persetujuan user (hanya setelah user setuju) → publishing/approval.json
  utf16   "<teks>"            hitung panjang UTF-16 (batas caption TikTok Content Posting API)

<dir> = folder project/konten mana pun (video, carousel, foto). Tidak terikat brand atau tool produksi tertentu.
"""
import argparse, hashlib, json, re, shutil, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def die(msg, code=1):
    print(f"✗ {msg}")
    sys.exit(code)

PUB_FILES = ["tiktok-caption.md", "instagram-caption.md", "facebook-caption.md", "hashtags-research.md",
             "publishing-checklist.md", "content-metadata.json"]
# Aturan terverifikasi (lihat references/caption-guide.md untuk sumber & tanggal)
PUB_RULES = {
    "tiktok":    {"file": "tiktok-caption.md",    "max_tags": None, "preset": (3, 5), "max_utf16": 2200},
    "instagram": {"file": "instagram-caption.md", "max_tags": 5,    "preset": (1, 5), "max_utf16": None},
    "facebook":  {"file": "facebook-caption.md",  "max_tags": None, "preset": (0, 3), "max_utf16": None},
}
PUB_GENERIC = {"fyp", "foryou", "foryoupage", "fy", "viral", "reels", "explore", "explorepage", "trending", "xyzbca", "fypシ"}
PUB_BAIT = [r"wajib\s+komen", r"spam\s+komen", r"komen\s+(yang\s+)?banyak", r"follow\s+dulu\s+baru", r"like\s+dulu", r"tag\s+\d+\s+teman",
            r"jangan\s+di-?skip", r"auto\s+fyp", r"pasti\s+fyp", r"dijamin\s+viral",
            # English
            r"comment\s+[\"']?(yes|1|below\s+to\s+win)", r"smash\s+(that|the)\s+like", r"like\s+(and|&)\s+share\s+(if|or)", r"tag\s+\d+\s+friends",
            r"spam\s+the\s+comments", r"share\s+(this\s+)?or\s+(bad\s+luck|you)", r"guaranteed\s+(viral|fyp)", r"don'?t\s+scroll"]
PUB_SECTIONS = ["Caption final", "Keyword", "Hashtag", "Alasan", "Cover title", "CTA", "Alternatif hook", "Terakhir verifikasi"]


def utf16_len(text):
    return len(text.encode("utf-16-le")) // 2


def pub_caption(md):
    m = re.search(r"```caption\n(.*?)```", md, re.S)
    return m.group(1).strip() if m else None


def cmd_check(a):
    d = Path(a.dir).resolve(); out = d / "publishing" if (d / "publishing").exists() or d.name != "publishing" else d
    if not out.exists():
        die("publishing/ belum ada — jalankan `scp.py init <dir>` dulu.")
    errs, warns, caps = [], [], {}
    add = lambda lvl, plat, msg: (errs if lvl == "error" else warns).append(f"[{plat}] {msg}")
    meta = {}
    try:
        meta = json.loads((out / "content-metadata.json").read_text())
    except Exception as e:
        add("error", "meta", f"content-metadata.json tidak valid: {e}")
    brand = meta.get("brand") or {}
    if not brand.get("name"):
        add("warn", "brand", "brand.name kosong di content-metadata.json (isi dari brief; modul ini netral brand)")
    if not brand.get("language"):
        add("error", "brand", "brand.language belum diisi (bahasa caption)")
    banned = [w for w in brand.get("banned_words", []) if w]
    for plat, rule in PUB_RULES.items():
        f = out / rule["file"]
        if not f.exists():
            add("error", plat, f"{rule['file']} tidak ada"); continue
        md = f.read_text()
        cap = pub_caption(md)
        if not cap or "{" in cap and "}" in cap and "TODO" in cap.upper():
            add("error", plat, "caption final belum diisi (blok ```caption)"); continue
        caps[plat] = cap
        tags = re.findall(r"(?<!\w)#([\w\u00C0-\u024F]+)", cap)
        n = len(tags); lo, hi = rule["preset"]
        if rule["max_tags"] is not None and n > rule["max_tags"]:
            add("error", plat, f"{n} hashtag > batas platform {rule['max_tags']}")
        elif not (lo <= n <= hi):
            add("warn", plat, f"{n} hashtag di luar preset internal {lo}–{hi} (bukan aturan platform)")
        if len(set(t.lower() for t in tags)) < n:
            add("error", plat, "hashtag duplikat")
        gen = [t for t in tags if t.lower() in PUB_GENERIC]
        if gen:
            add("error", plat, f"hashtag generik/tidak relevan: {', '.join('#' + g for g in gen)}")
        if rule["max_utf16"] and utf16_len(cap) > rule["max_utf16"]:
            add("error", plat, f"caption {utf16_len(cap)} UTF-16 units > {rule['max_utf16']} (batas Content Posting API)")
        for w in banned:
            if re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", cap, re.I):
                add("error", plat, f"kata terlarang brand: '{w}'")
        for pat in PUB_BAIT:
            if re.search(pat, cap, re.I):
                add("error", plat, f"engagement bait terdeteksi: /{pat}/")
        emo = len(re.findall(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", cap))
        if emo > 4:
            add("warn", plat, f"{emo} emoji — terlalu banyak (maks ±3)")
        first = cap.split("\n", 1)[0]
        if len(first) > 120:
            add("warn", plat, "kalimat pertama (hook) terlalu panjang, > 120 karakter")
        for sec in PUB_SECTIONS:
            if sec.lower() not in md.lower():
                add("error", plat, f"bagian '{sec}' tidak ada")
        if re.search(r"Terakhir verifikasi[^\n]*\{", md):
            add("error", plat, "tanggal verifikasi aturan belum diisi")
        pm = meta.get("platforms", {}).get(plat, {})
        sc = (pm.get("score") or {}).get("total")
        if sc is None:
            add("error", plat, "skor rubrik belum diisi di content-metadata.json")
        elif sc < 85:
            add("error", plat, f"skor rubrik {sc}/100 < 85 → revisi caption")
        mt = [t.lower().lstrip("#") for t in pm.get("hashtags", [])]
        if mt and sorted(mt) != sorted(t.lower() for t in tags):
            add("error", plat, "hashtag di caption ≠ hashtag di content-metadata.json")
        if not pm.get("hard_checks_passed"):
            add("error", plat, "hard checks belum dikonfirmasi (hard_checks_passed=true setelah dicek manual)")
    vals = list(caps.values())
    for i in range(len(vals)):
        for j in range(i + 1, len(vals)):
            if re.sub(r"\s+", " ", vals[i]) == re.sub(r"\s+", " ", vals[j]):
                add("error", "semua", "caption identik antar platform — wajib diadaptasi")
    hr = (out / "hashtags-research.md").read_text() if (out / "hashtags-research.md").exists() else ""
    for plat, cap in caps.items():
        for t in re.findall(r"(?<!\w)#([\w\u00C0-\u024F]+)", cap):
            if f"#{t}".lower() not in hr.lower():
                add("error", plat, f"#{t} tidak punya alasan di hashtags-research.md")
    rep = [f"# Caption QC — {d.name}", "", f"_{datetime.now().isoformat(timespec='seconds')}_", "",
           f"**{'LULUS' if not errs else 'GAGAL'}** — {len(errs)} error, {len(warns)} warning", "",
           "Skor rubrik = alat editorial internal, bukan skor algoritma platform / prediksi FYP.", ""]
    for plat, cap in caps.items():
        tags = re.findall(r"(?<!\w)#\w+", cap)
        rep.append(f"- {plat}: {utf16_len(cap)} UTF-16 units · {len(tags)} hashtag · skor {meta.get('platforms', {}).get(plat, {}).get('score', {}).get('total', '?')}")
    rep += [""] + [f"- ✗ {e}" for e in errs] + [f"- ! {w}" for w in warns]
    (out / "caption-qc.md").write_text("\n".join(rep) + "\n")
    print("\n".join(rep[4:]))
    print(f"→ publishing/caption-qc.md" + ("" if errs else f" · tampilkan paket ke user → setelah setuju: scp.py approve {a.dir}"))
    if errs:
        sys.exit(1)


def cmd_init(a):
    d = Path(a.dir).resolve(); out = d / "publishing"; out.mkdir(parents=True, exist_ok=True)
    for f in PUB_FILES:
        if a.force or not (out / f).exists():
            shutil.copy(ROOT / "templates" / "publishing" / f, out / f)
    mp = out / "content-metadata.json"
    m = json.loads(mp.read_text())
    b = m.setdefault("brand", {})
    for k, v in {"name": a.brand, "handle": a.handle, "language": a.lang, "region": a.region}.items():
        if v: b[k] = v
    mp.write_text(json.dumps(m, indent=2, ensure_ascii=False))
    print(f"✓ {out}\n  1) isi brand profile di content-metadata.json  2) tulis 3 caption + hashtags-research.md  3) scp.py check {a.dir}")


def cmd_approve(a):
    out = Path(a.dir).resolve() / "publishing"
    rep = out / "caption-qc.md"
    if not rep.exists() or "**LULUS**" not in rep.read_text():
        die("caption QC belum LULUS — jalankan scp.py check sampai lulus, tampilkan ke user, baru approve.")
    h = hashlib.sha1()
    for f in PUB_FILES:
        p = out / f
        if p.exists(): h.update(p.read_bytes())
    (out / "approval.json").write_text(json.dumps({"approved_at": datetime.now().isoformat(timespec="seconds"),
        "snapshot": h.hexdigest()[:12], "note": a.note or ""}, indent=2, ensure_ascii=False))
    print("✓ approved — paket siap publish (publikasi tetap dilakukan user / atas izin eksplisit user)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("init"); p.add_argument("dir"); p.add_argument("--force", action="store_true")
    p.add_argument("--brand"); p.add_argument("--handle"); p.add_argument("--lang"); p.add_argument("--region"); p.set_defaults(fn=cmd_init)
    p = sp.add_parser("check"); p.add_argument("dir"); p.set_defaults(fn=cmd_check)
    p = sp.add_parser("approve"); p.add_argument("dir"); p.add_argument("--note"); p.set_defaults(fn=cmd_approve)
    p = sp.add_parser("utf16"); p.add_argument("text"); p.set_defaults(fn=lambda a: print(utf16_len(a.text)))
    a = ap.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
