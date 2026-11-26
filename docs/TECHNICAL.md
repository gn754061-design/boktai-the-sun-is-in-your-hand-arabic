# Technical Documentation — Boktai Arabic Translation

This document records the reverse-engineering and modification facts of the
Arabic translation of *Boktai: The Sun Is in Your Hand* (GBA, USA). It is
provided for verification, reproducibility, and bug-reporting.

---

## 1. Project Identity

| Field | Value |
|---|---|
| Target | Boktai: The Sun Is in Your Hand (USA) |
| Platform | Game Boy Advance (ARM7TDMI) |
| Game Code | `U3IE` |
| Cartridge title | `BOKTAI` |
| Engine | Konami / KCEJ GCL bytecode + script engine |
| Source language | English |
| Target language | Arabic |

### Source ROM (clean, unmodified)

| Property | Value |
|---|---|
| Size | 16,777,216 bytes (0x1000000) |
| CRC32 | `E715AC45` |
| MD5 | `FF75C62AB690410CC8FCA24204D783E9` |
| SHA-1 | `7164326283DF46A3941EC7B6CECA889CBC40E660` |

The clean source ROM was never modified. All changes were applied to a work
copy and then diffed into a patch.

### Patched ROM (output)

| Property | Value |
|---|---|
| Size | 16,777,216 bytes |
| CRC32 | `261340EC` |
| SHA-1 | `9D3C2BF295A68479E6714CD37036958BD0C37B3A` |

---

## 2. Memory Map (GBA flat address space)

| Item | File offset | GBA address |
|---|---|---|
| ROM base | `0x000000` | `0x08000000` |
| Text engine (typewriter) | `0x0130BD8` | `0x08130BD8` |
| Text engine (instant) | `0x0130AA4` | `0x08130AA4` |
| MFT file table | `0x05B02C4` | `0x085B02C4` |
| Font container (MFT `0x6D24`) | `0x0BA54C8` | `0x08BA54C8` |
| Primary font glyphs | `0x0BA54F0` | `0x08BA54F0` |
| Script file (MFT `0x41F5`) | `0x00E0DA84` | `0x08E0DA84` |
| String pointer table | `0x00E17AF0` | `0x08E17AF0` |
| String data | `0x00E1BE1C` | `0x08E1BE1C` |
| In-place string capacity | `0x00E1BE1C..0x00E41D44` | 155,432 bytes |
| ROM free space | `0x00EDA850..0x01000000` | 1,202,096 bytes |

---

## 3. Modifications Applied

### 3.1 Text engine (single-byte unlock)

The original engine treats bytes `>= 0x80` as a signed value and branches to a
Kanji routine. Three signed branches were NOP-ed so the engine falls through to
the direct single-byte 8×16 font lookup, unlocking the full range `0x20..0xFF`:

| File offset | Original | Patched | Effect |
|---|---|---|---|
| `0x130BB6` | `B3 DB` (`blt`) | `C0 46` (`mov r8, r8`) | Unlock range |
| `0x130BEA` | `3D DB` (`blt`) | `C0 46` (`mov r8, r8`) | Unlock range |
| `0x130C9E` | `E3 DB` (`blt`) | `C0 46` (`mov r8, r8`) | Unlock range |

### 3.2 Arabic font

- Container: `0x0BA54C8` (MFT resource `0x6D24`).
- Glyph format: 8×16, 4bpp, 64 bytes per glyph.
- Glyph slot = byte − 0x20; offset = `0x28 + slot × 64`.
- Arabic presentation forms are mapped to `0x7B..0xFF` (see `charset_ar.tbl`),
  including Isolated / Initial / Medial / Final forms, the lam-alef ligatures,
  and Arabic punctuation `؟ ، ؛ « »`.
- Glyphs are generated as clean 1-bit pixel art (ink = color 1, background =
  color 4) and packed in standard GBA 4bpp tile order.

### 3.3 Text

- String pointer table at `0x00E17AF0` (4,299 × 32-bit offsets).
- String data at `0x00E1BE1C`.
- 4,286 of 4,299 strings contain Arabic text (6 non-Arabic, 7 empty).
- Arabic shaping and RTL reordering are performed at build time (pre-shaped
  presentation forms), so no runtime reshaping is required.
- Control codes and markup (e.g. `<UVMOJI>`, `<NAME>`, `<LABEL>`, `<WAIT>`,
  button icons) are preserved.

### 3.4 Diff summary

166,969 bytes differ between the clean source and the patched ROM, coalesced
into 8 ranges:

| Range | Size | Area |
|---|---|---|
| `0x130BB6–0x130BEB` | 54 B | Text engine NOPs |
| `0x130C9E–0x130C9F` | 2 B | Text engine NOP |
| `0xBA5539–0xBA8CE6` | ~8.6 KB | Arabic font glyphs |
| `0xE17AF3–0xE41803` | 171,281 B | Pointer table + translated strings |

---

## 4. Verification Gates

| Gate | Result |
|---|---|
| Clean source hash verified | PASS |
| Byte-identical dump/reinsert round-trip | PASS |
| IPS applies to source → patched ROM | PASS |
| BPS applies to source → patched ROM | PASS |
| Patched output SHA-1 matches expected | PASS |
| Source ROM left untouched | PASS |
| In-emulator rendering (mGBA) | PASS (per build record) |

---

## 5. Reproducibility

The build is driven by these scripts (not included in this release):

- `scripts/build_arabic_system.py` — font injection + RTL engine patch.
- `scripts/build_full_translations.py` — text translation and injection.
- `scripts/create_patch.py` — patch generation.
- `scripts/roundtrip.py` — byte-identical round-trip gate.

To rebuild, the clean source ROM must be present and match the hash in §1.

---

## 6. Known Limitations

- The translation is pre-shaped (visual order); it does not perform runtime
  BiDi. Mixed Arabic/Latin strings rely on the build-time ordering.
- The font covers the Arabic presentation forms used by the translation; rare
  characters outside the mapped set fall back to placeholder glyphs.
- Latin text is not re-encoded; the game's original Latin strings are replaced
  by Arabic, and a few proper nouns may remain in Latin form.
- Save data created by the original (English) ROM is not guaranteed to load in
  the translated ROM. Start a new save.

---

*Boktai © Konami/KCEJ. This translation is a non-commercial fan work.*