#!/usr/bin/env python3
# roundtrip.py - encoding gate: dump -> re-insert -> byte-identical for Boktai 1 U string data.
# Boktai text = plain ASCII: byte b (0x00-0xFF) <-> chr(b) identity.
# 0x00 = string terminator (appended by inserter, stripped by dumper).
# Works on the work copy only.
import sys, json, struct
from pathlib import Path

sys.path.insert(0, r"C:\Users\reva4\.venvs\gt-venv\Lib\site-packages")

ROM = r"C:\Users\reva4\Desktop\work_boktai_ar\Boktai - The Sun Is in Your Hand (USA).gba"
OUT = Path(r"C:\Users\reva4\Desktop\work_boktai_ar/dump/roundtrip")

BASE = 0x08000000
SCRIPT_IDS = {0xa41e, 0x41f5, 0x49bc}

# خريطة هوية كاملة لكل بايت 0x00-0xFF (<-> chr(b))، مغطاة بالجدول إن وجد
decode = {b: chr(b) for b in range(0x100)}
encode = {chr(b): b for b in range(0x100)}

# تطبق charset_us.tbl كطبقة توثيقية (لا تغير الهوية للحروف المطبوعة)
TBL = r"C:\Users\reva4\Desktop\work_boktai_ar/charset_us.tbl"
try:
    with open(TBL, "rb") as f:
        for line in f:
            line = line.rstrip(b"\n").decode("utf-8")
            if not line or line[0] in "#./*" or "=" not in line:
                continue
            k, v = line.split("=", 1)
            bb = bytes.fromhex(k)
            if len(bb) == 1:
                decode[bb[0]] = v
                encode[v] = bb[0]
except FileNotFoundError:
    pass

def ru32(rom, p):
    return struct.unpack_from("<I", rom, p)[0]

def main():
    rom = bytearray(open(ROM, "rb").read())
    mft = 0x085b02c4
    start = mft - BASE
    entries = []
    for x in struct.iter_unpack("<HHI", rom[start:start + 11 * 8]):
        entries.append({"id1": x[0], "id2": x[1], "ptr": x[2]})
    last = None
    for e in sorted(entries, key=lambda x: x["ptr"], reverse=True):
        e["end"] = last
        last = e["ptr"]

    target = None
    for e in entries:
        if e["id1"] in SCRIPT_IDS:
            target = e
            break
    if target is None:
        print("scripts file not found"); sys.exit(1)
    print("scripts file: id1=%04x ptr=%08x end=%s" % (
        target["id1"], target["ptr"], hex(target["end"]) if target["end"] else "None"))

    p = target["ptr"] - BASE
    p += 4
    while True:
        sid = ru32(rom, p); ptr = ru32(rom, p + 4); p += 8
        if sid == 0 and (ptr & 0x00ffffff) == 0:
            break
    offset_block = p
    off_1 = ru32(rom, p); p += 4
    off_2 = ru32(rom, p); p += 4
    off_3 = ru32(rom, p); p += 4
    off_4 = ru32(rom, p); p += 4

    string_index_start = offset_block + off_2
    string_data_start = offset_block + off_3
    n = (string_data_start - string_index_start) // 4
    print("string_index_start=%08x string_data_start=%08x n_strings=%d index_size=%d" % (
        string_index_start, string_data_start, n, string_data_start - string_index_start))

    results = []
    all_ok = True
    for i in range(n):
        ptr = ru32(rom, string_index_start + i * 4)
        s_off = ptr & 0x7fffffff
        abs_start = string_data_start + s_off
        if i + 1 < n:
            ptr2 = ru32(rom, string_index_start + (i + 1) * 4)
            abs_end = string_data_start + (ptr2 & 0x7fffffff)
        else:
            abs_end = string_data_start
        raw = bytes(rom[abs_start:abs_end])
        if raw and raw[-1] == 0:
            text_bytes = raw[:-1]
            terminator = raw[-1:]
        else:
            text_bytes = raw
            terminator = b""
        chars = []
        ok = True
        for b in text_bytes:
            ch = decode.get(b)
            if ch is None:
                ch = "<ESC=%02x>" % b
                ok = False
            chars.append(ch)
        s = "".join(chars)
        buf = bytearray()
        miss = []
        for ch in s:
            if ch in encode:
                buf.append(encode[ch])
            else:
                miss.append(ch); all_ok = False
        buf += terminator
        match = (bytes(buf) == raw)
        if not match:
            all_ok = False
        results.append({
            "id": i, "abs_start": abs_start, "abs_end": abs_end,
            "len": len(raw), "text": s, "ok": ok, "match": match,
        })
        if i < 3 or not match:
            print("id=%4d off=%08x len=%4d match=%s ok=%s  %s" % (
                i, abs_start, len(raw), match, ok, repr(s[:60])))
        if miss:
            print("    missing encode for:", [repr(c) for c in miss[:5]])

    print("\ntotal strings:", len(results))
    print("all decodable:", all(r["ok"] for r in results))
    print("re-encode byte-identical:", all(r["match"] for r in results))
    print("encoding gate:", "PASS" if (all_ok and all(r["match"] for r in results)) else "FAIL")

    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "strings.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("saved:", OUT / "strings.json")

if __name__ == "__main__":
    main()
