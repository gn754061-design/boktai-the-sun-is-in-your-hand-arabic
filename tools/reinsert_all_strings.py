import struct
import json
from pathlib import Path
from arabic_encoder import encode_arabic_string

ROM_PATH = Path(r"C:\Users\reva4\Desktop\work_boktai_ar\Boktai - The Sun Is in Your Hand (USA).gba")
STRINGS_JSON = Path(r"C:\Users\reva4\Desktop\work_boktai_ar\dump\roundtrip\strings.json")

def reinsert_strings(translations_map={}):
    """
    translations_map: dict mapping string_id (int) -> translated_string (str)
    If a string_id is not in translations_map, its original string is preserved.
    """
    rom = bytearray(ROM_PATH.read_bytes())
    with open(STRINGS_JSON, "r", encoding="utf-8") as f:
        items = json.load(f)

    string_index_start = 0x00e17af0
    string_data_start = 0x00e1be1c
    max_orig_data_end = 0x00e41d44
    max_orig_capacity = max_orig_data_end - string_data_start # 155,432 bytes

    # Encode all strings
    encoded_blobs = []
    total_size = 0
    for item in items:
        sid = item["id"]
        if sid in translations_map:
            text = translations_map[sid]
            # Use Arabic encoder (handles shaping, BiDi, tags)
            raw = encode_arabic_string(text) + b"\x00"
        else:
            # Preserve original bytes byte-identically
            orig_text = item["text"]
            # Convert string back to original bytes (ASCII + \x00)
            raw = bytearray()
            for c in orig_text:
                raw.append(ord(c))
            raw.append(0x00)
        encoded_blobs.append(raw)
        total_size += len(raw)

    print(f"Total strings to insert: {len(encoded_blobs)}")
    print(f"Total string data size: {total_size} bytes (Capacity in-place: {max_orig_capacity} bytes)")

    # Strategy: In-place if total_size <= max_orig_capacity
    # Otherwise relocate to 0x00eda850 (1.17 MB free space)
    if total_size <= max_orig_capacity:
        target_data_start = string_data_start
        print(f"Writing strings IN-PLACE at 0x{target_data_start:06x}...")
    else:
        target_data_start = 0x00eda850
        print(f"Strings exceed original capacity! RELOCATING to free space at 0x{target_data_start:06x}...")
        # Update off_3 in offset_block (0x00e17ae0)
        # off_3 is at offset_block + 8
        offset_block = 0x00e17ae0
        new_off_3 = target_data_start - offset_block
        new_off_4 = new_off_3 + total_size
        struct.pack_into("<I", rom, offset_block + 8, new_off_3)
        struct.pack_into("<I", rom, offset_block + 12, new_off_4)
        print(f"Updated offset_block: off_3=0x{new_off_3:x}, off_4=0x{new_off_4:x}")

    # Pack strings and build new index table
    current_off = 0
    for i, blob in enumerate(encoded_blobs):
        # Update pointer in index table
        struct.pack_into("<I", rom, string_index_start + i * 4, current_off)
        # Write blob to target data location
        rom[target_data_start + current_off : target_data_start + current_off + len(blob)] = blob
        current_off += len(blob)

    ROM_PATH.write_bytes(rom)
    print(f"Successfully reinserted {len(encoded_blobs)} strings! Last offset: 0x{target_data_start + current_off:06x}")
    return True

if __name__ == "__main__":
    # Test zero-diff reinsertion
    print("Testing zero-diff reinsertion...")
    reinsert_strings({})
