# ROMHACK.md — Boktai: The Sun Is in Your Hand (USA) → Arabic

## Project
- Target: Boktai - The Sun Is in Your Hand (USA) [Game Boy Advance]
- Path (work copy): C:\Users\reva4\Desktop\work_boktai_ar\Boktai - The Sun Is in Your Hand (USA).gba
- Original (untouched): C:\Users\reva4\Desktop\Boktai - The Sun Is in Your Hand (USA)\Boktai - The Sun Is in Your Hand (USA)\Boktai - The Sun Is in Your Hand (USA).gba
- Source language: English → Target language: Arabic
- Platform/engine: GBA (ARM7TDMI), Konami / KCEJ GCL bytecode & script engine

## Fingerprints (Original clean ROM — preserved untouched)
- Size: 16777216 bytes (0x1000000, 16.0 MB)
- SHA1: 7164326283df46a3941ec7b6ceca889cbc40e660
- MD5 : ff75c62ab690410cc8fca24204d783e9
- CRC32: e715ac45  ← matches documented clean Boktai 1 USA

## Header (GBA cart, flat address space)
- Title: BOKTAI
- Game Code: U3IE
- Entry point: 0xea00002e
- Map: file offset 0x000000 <=> GBA address 0x08000000
- Substrate: cartridge image (flat), no filesystem

## Project Gates Status

### Gate 1: Recon — PASSED
- MFT file table located at `0x085b02c4` (file offset `0x005b02c4`).
- All 11 MFT resource files identified, bounded, and indexed.
- Clean ROM verified and kept untouched; all modifications applied to work copy.

### Gate 2: Encoding — PASSED
- Script file located at MFT ID `0x41f5` / file offset `0x00e0da84`.
- Structure: script headers → offset block (`0x00e17ae0`) → string pointer index (`0x00e17af0`) → string data (`0x00e1be1c`).
- 4,299 strings dumped, verified, and re-inserted byte-identically via `scripts/roundtrip.py`.
- Base character table: `charset_us.tbl`.

### Gate 3: Accents (Arabic Font + Charset + RTL Engine) — PASSED
- Font architecture:
  - Font container at MFT ID `0x6d24` / ROM `0x00ba54c8` (`dump/font.bin`).
  - Primary font (8x16 4bpp, 64 bytes/glyph) starts at offset `0x28` (`0x00ba54f0`).
  - Dual text engines identified: typewriter engine (`0x08130bd8`) and instant engine (`0x08130aa4`).
- Single-byte engine patch:
  - NOP-ed signed branches at `0x130bb6`, `0x130bea`, and `0x130c9e` (`blt` → `mov r8, r8`).
  - Unlocked full range `0x20..0xFF` for direct single-byte 8x16 glyph addressing.
- Arabic font generation:
  - 133 Arabic presentation forms (Isolated, Initial, Medial, Final + Ligatures لا, لأ, لإ, لآ + Punctuation ؟ ، ؛ « ») mapped to `0x7B..0xFF` (`charset_ar.tbl`).
  - High-readability anti-aliased 8x16 4bpp glyphs generated and injected into `dump/font_ar.bin` and ROM.
- Reshaping & BiDi RTL:
  - Arabic shaping and line-by-line right-to-left reordering implemented in `scripts/arabic_encoder.py`.
  - Full GCL tag protection (`<NAME>`, `<LABEL>`, `<WAIT>`, etc.) and button icons (`\x80\xXX`).
- Emulator verification:
  - Proof captured in mGBA showing Arabic rendering live on screen.
  - Full proofs saved at `dump/screenshots/proof_arabic_glyph.png` and `dump/screenshots/proof_arabic_sentence.png`.

### Gate 4: Space — PASSED
- String pointer table: 4,299 32-bit pointers at `0x00e17af0`.
- In-place string capacity: `0x00e1be1c` to `0x00e41d44` = 155,432 bytes (~151.8 KB).
- ROM free space: 1,202,096 bytes (1.17 MB) of contiguous empty padding from `0x00eda850` to `0x01000000`.
- Cartridge expansion headroom: up to 32 MB supported by GBA hardware.
- Strategy: In-place 1-byte encoding packing; dynamic relocation to `0x00eda850` via `off_3` if needed.

### Gate 5: Graphics — PASSED
- MFT archive formats reverse engineered.
- Dump and reinsertion roundtrip verified byte-identically (`scripts/gfx_roundtrip.py` → `dump/gfx/mft_4679.bin`).

### Gate 6: Glossary — PASSED
- Comprehensive bilingual glossary established with strict character length limits:
  - Files: `docs/glossary.json` and `docs/glossary.md`.
  - Categories: Characters, Weapons & Equipment, Concepts & Lore, and System/UI terms.

### Gate 7: Translation & Reinsertion — PASSED
- 4,286 of 4,299 strings contain Arabic (6 non-Arabic, 7 empty) — verified by
  decoding the pointer table at `0x00e17af0` against `charset_ar.tbl`.
- Patched output verified in mGBA; build hash recorded.
- Patched ROM: 16,777,216 bytes, CRC32 `261340EC`, SHA1
  `9d3c2bf295a68479e6714cd37036958bd0c37b3a`.
- Distribution patches verified against the clean source (CRC32 `e715ac45`):
  - `patch/boktai_arabic.ips` — 9,569 records, applies cleanly.
  - `patch/boktai_arabic.bps` — regenerated with a spec-compliant encoder and
    verified (source `e715ac45`, target `261340EC`, patch CRC valid).

## Rules Observed
- Original ROM untouched at all times.
- Work ROM copy modified with verified atomic scripts.
- No third-party LLMs used for translation.
- UTF-8 Python scripts used exclusively.
