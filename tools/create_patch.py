import os
import struct
import zlib
from pathlib import Path

ORIG_ROM = Path(r"C:\Users\reva4\Desktop\Boktai - The Sun Is in Your Hand (USA)\Boktai - The Sun Is in Your Hand (USA)\Boktai - The Sun Is in Your Hand (USA).gba")
WORK_ROM = Path(r"C:\Users\reva4\Desktop\work_boktai_ar\Boktai - The Sun Is in Your Hand (USA).gba")
PATCH_DIR = Path(r"C:\Users\reva4\Desktop\work_boktai_ar\patch")
PATCH_DIR.mkdir(parents=True, exist_ok=True)

orig = ORIG_ROM.read_bytes()
work = WORK_ROM.read_bytes()

assert len(orig) == len(work), "ROM sizes differ!"

def create_ips(orig_data, work_data, out_path):
    # IPS format:
    # "PATCH" header
    # Records: [3-byte offset, 2-byte size, data...]
    # "EOF" trailer
    res = bytearray(b"PATCH")
    i = 0
    n = len(orig_data)
    while i < n:
        if orig_data[i] == work_data[i]:
            i += 1
            continue
        # Found diff start
        start = i
        while i < n and orig_data[i] != work_data[i] and (i - start) < 0xFFFF:
            i += 1
        length = i - start
        
        # 3-byte offset
        res.append((start >> 16) & 0xFF)
        res.append((start >> 8) & 0xFF)
        res.append(start & 0xFF)
        # 2-byte size
        res.append((length >> 8) & 0xFF)
        res.append(length & 0xFF)
        # Data
        res.extend(work_data[start:i])
    
    res.extend(b"EOF")
    Path(out_path).write_bytes(res)
    print(f"Created IPS patch: {out_path} ({len(res)} bytes)")

def create_bps(orig_data, work_data, out_path):
    # Standard BPS format (Flips / Beat)
    # Magic: 'BPS1'
    # Source size, Target size, Metadata size
    def encode_vli(val):
        b = bytearray()
        while True:
            x = val & 0x7F
            val >>= 7
            if val == 0:
                b.append(0x80 | x)
                break
            b.append(x)
            val -= 1
        return bytes(b)

    def cmd_len_action(length, action):
        # BPS command byte: bits 0-1 = length code, bits 2-7 = action.
        # code 0 => a varint(length-1) follows; code 1..3 => length 2..4.
        if 2 <= length <= 4:
            return bytes([(action << 2) | (length - 1)])
        return bytes([(action << 2)]) + encode_vli(length - 1)

    out = bytearray(b"BPS1")
    out.extend(encode_vli(len(orig_data)))
    out.extend(encode_vli(len(work_data)))
    out.extend(encode_vli(0)) # no metadata

    i = 0
    n = len(orig_data)

    while i < n:
        if orig_data[i] == work_data[i]:
            # SourceRead
            start = i
            while i < n and orig_data[i] == work_data[i]:
                i += 1
            out.extend(cmd_len_action(i - start, 0))
        else:
            # TargetRead
            start = i
            while i < n and orig_data[i] != work_data[i]:
                i += 1
            out.extend(cmd_len_action(i - start, 1))
            out.extend(work_data[start:i])

    # Checksums (source CRC32, target CRC32, patch CRC32) + BPS1 magic
    crc_src = zlib.crc32(orig_data) & 0xFFFFFFFF
    crc_tgt = zlib.crc32(work_data) & 0xFFFFFFFF
    out.extend(struct.pack("<II", crc_src, crc_tgt))
    crc_patch = zlib.crc32(out) & 0xFFFFFFFF
    out.extend(struct.pack("<I", crc_patch))
    out.extend(b"BPS1")

    Path(out_path).write_bytes(out)
    print(f"Created BPS patch: {out_path} ({len(out)} bytes)")

create_ips(orig, work, PATCH_DIR / "boktai_arabic.ips")
create_bps(orig, work, PATCH_DIR / "boktai_arabic.bps")
