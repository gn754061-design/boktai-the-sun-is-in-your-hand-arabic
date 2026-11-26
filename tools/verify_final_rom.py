import subprocess
import time
import glob
import os
import shutil
import ctypes

user32 = ctypes.windll.user32
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
VK_F12 = 0x7B
VK_RETURN = 0x0D
K_A = ord('J')

FINAL_ROM = r"C:\Users\reva4\Desktop\work_boktai_ar\build\Boktai - The Sun Is in Your Hand (Arabic).gba"
MGBA_PATH = r"C:\Program Files\mGBA\mGBA.exe"
SHOTS_DIR = r"C:\Users\reva4\Desktop\game\MLSS_AR\work\mgba_shots"

for p in glob.glob(os.path.join(SHOTS_DIR, '*.png')):
    try: os.remove(p)
    except: pass

print(f"Launching mGBA with final built ROM: {FINAL_ROM}")
proc = subprocess.Popen([MGBA_PATH, FINAL_ROM])

hwnds = []
def cb(h, _):
    if user32.IsWindowVisible(h):
        buf = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(h, buf, 256)
        if 'mGBA' in buf.value: hwnds.append(h)
    return True

for _ in range(20):
    user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)(cb), 0)
    if hwnds: break
    time.sleep(0.5)

top = hwnds[0]
all_targets = [top]
def child_cb(ch, _):
    all_targets.append(ch)
    return True
user32.EnumChildWindows(top, ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)(child_cb), 0)

def post_key(vk, hold=0.15, delay=0.3):
    sc = user32.MapVirtualKeyW(vk, 0)
    lp_down = 1 | (sc << 16)
    lp_up = 1 | (sc << 16) | (1 << 30) | (1 << 31)
    for t in all_targets:
        user32.PostMessageW(t, WM_KEYDOWN, vk, lp_down)
    time.sleep(hold)
    for t in all_targets:
        user32.PostMessageW(t, WM_KEYUP, vk, lp_up)
    time.sleep(delay)

def take_shot():
    sc = user32.MapVirtualKeyW(VK_F12, 0)
    lp_down = 1 | (sc << 16)
    lp_up = 1 | (sc << 16) | (1 << 30) | (1 << 31)
    for t in all_targets:
        user32.PostMessageW(t, WM_KEYDOWN, VK_F12, lp_down)
    time.sleep(0.05)
    for t in all_targets:
        user32.PostMessageW(t, WM_KEYUP, VK_F12, lp_up)
    time.sleep(0.3)

# FF through logos
post_key(0x09, delay=0.1)
time.sleep(1.5)
post_key(0x09, delay=0.2)

# Start -> A -> A
post_key(VK_RETURN, delay=0.8)
post_key(K_A, delay=0.8)
post_key(K_A, delay=0.8)

time.sleep(1.0)
take_shot()

proc.terminate()
time.sleep(1)
try: proc.kill()
except: pass

shots = sorted(glob.glob(os.path.join(SHOTS_DIR, '*.png')))
if shots:
    dest = r"C:\Users\reva4\Desktop\work_boktai_ar\dump\screenshots\final_rom_verify.png"
    shutil.copy2(shots[-1], dest)
    print(f"Captured verification screenshot of final ROM: {dest}")
else:
    print("No shot captured.")
