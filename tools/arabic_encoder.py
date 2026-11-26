import re
import arabic_reshaper
from bidi.algorithm import get_display
from pathlib import Path

TBL_PATH = Path(r"C:\Users\reva4\Desktop\work_boktai_ar\charset_ar.tbl")
char_to_byte = {}
byte_to_char = {}

with open(TBL_PATH, "r", encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        b = int(k, 16)
        char_to_byte[v] = b
        byte_to_char[b] = v

TAG_REGEX = re.compile(r"(<[^>]+>|\x80[\x00-\xff])")

def reshape_text(text):
    if not text:
        return ""
    # Use arabic_reshaper
    reshaped = arabic_reshaper.reshape(text)
    # Reorder RTL with bidi
    visual = get_display(reshaped)
    return visual

def encode_arabic_line(line):
    # Split line into tokens: tags vs regular text
    tokens = TAG_REGEX.split(line)
    # tokens will alternate between text and tags
    # For Arabic text tokens, reshape and reverse them
    reshaped_tokens = []
    for tok in tokens:
        if not tok:
            continue
        if TAG_REGEX.match(tok):
            reshaped_tokens.append(tok)
        else:
            # Check if has Arabic
            if any('\u0600' <= c <= '\u06FF' or '\uFB50' <= c <= '\uFDFF' or '\uFE70' <= c <= '\uFEFF' for c in tok):
                reshaped_tokens.append(reshape_text(tok))
            else:
                reshaped_tokens.append(tok)
    
    # If the line contains Arabic, the order of top-level tokens in an RTL line
    # e.g., if line is '<LABEL>المعلم أوتينكو:</LABEL>' -> tag stays first or at start, but content inside is reshaped
    # If multiple text segments with tags between them, reverse token order if it's an Arabic sentence
    has_ar = any('\u0600' <= c <= '\u06FF' for c in line)
    if has_ar and len(reshaped_tokens) > 1 and not (reshaped_tokens[0].startswith("<") and reshaped_tokens[-1].startswith("</")):
        # If not an XML wrapper, reverse top-level tokens so Arabic reading order is RTL
        # e.g. "مرحباً <NAME> شكراً" -> "شكراً <NAME> مرحباً"
        reshaped_tokens = reshaped_tokens[::-1]
        
    return "".join(reshaped_tokens)

def encode_arabic_string(text):
    lines = text.split("\n")
    processed_lines = [encode_arabic_line(l) for l in lines]
    full_str = "\n".join(processed_lines)
    
    res = bytearray()
    i = 0
    while i < len(full_str):
        m = TAG_REGEX.match(full_str[i:])
        if m:
            tag_str = m.group(0)
            res.extend(tag_str.encode("latin-1"))
            i += len(tag_str)
            continue
        c = full_str[i]
        if c == "\n":
            res.append(0x0A)
        elif c in char_to_byte:
            res.append(char_to_byte[c])
        elif ord(c) < 0x80:
            res.append(ord(c))
        else:
            res.append(0x20)
        i += 1
    return bytes(res)

if __name__ == "__main__":
    t = '<LABEL>المعلم أوتينكو:</LABEL>\n"اليوم هو الأحد،\nيوم الشمس العظيم!"'
    enc = encode_arabic_string(t)
    print("Encoded successfully:", len(enc), "bytes")
    print(enc.hex(" "))
