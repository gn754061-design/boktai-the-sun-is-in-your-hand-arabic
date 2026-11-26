import os
import struct
from pathlib import Path

ROM_PATH = Path(r"C:\Users\reva4\Desktop\work_boktai_ar\Boktai - The Sun Is in Your Hand (USA).gba")
GFX_DIR = Path(r"C:\Users\reva4\Desktop\work_boktai_ar\dump\gfx")
GFX_DIR.mkdir(parents=True, exist_ok=True)

rom = ROM_PATH.read_bytes()

# MFT 0x4679 at 0xe09484 (size 17920 bytes)
off = 0xe09484
size = 17920
gfx_data = rom[off:off+size]

dump_file = GFX_DIR / "mft_4679.bin"
dump_file.write_bytes(gfx_data)
print(f"Dumped MFT 0x4679 ({len(gfx_data)} bytes) to {dump_file}")

# Verify round-trip reinsertion
reloaded = dump_file.read_bytes()
assert reloaded == gfx_data, "Byte mismatch on reload!"

# Test write to work copy
work_rom = bytearray(rom)
work_rom[off:off+size] = reloaded
assert work_rom[off:off+size] == rom[off:off+size], "Reinsertion mismatch!"

print("Graphics dump/re-insertion round-trip PASSED: byte-identical.")
