import os
import cv2
from PIL import Image

BRAIN_DIR = r"C:\Users\10431\.gemini\antigravity\brain\bcf94466-2063-40f3-abf4-5a33f63af215"
OUT_DIR = "gfx/leaders/EBS"
os.makedirs(OUT_DIR, exist_ok=True)

MAPPINGS = [
    {
        "char_id": "EBS_leader_chen_zhuanyuan",
        "file": "hoi4_portrait_chen_baosheng_clean_1793525564997.jpg",
        "base_name": "portrait_EBS_leader_chen_zhuanyuan"
    },
    {
        "char_id": "EBS_huai_zonggong",
        "file": "hoi4_portrait_huai_jinpeng_clean_1793525601514.jpg",
        "base_name": "portrait_EBS_huai_zonggong"
    },
    {
        "char_id": "EBS_zhou_zongdao",
        "file": "hoi4_portrait_zhou_ji_clean_1793525612025.jpg",
        "base_name": "portrait_EBS_zhou_zongdao"
    },
    {
        "char_id": "EBS_wang_sichang",
        "file": "hoi4_portrait_wang_dengfeng_clean_1793537067378.jpg",
        "base_name": "portrait_EBS_wang_sichang"
    },
    {
        "char_id": "EBS_wang_zongguan",
        "file": "hoi4_portrait_wang_shengzhan_clean_1793537078363.jpg",
        "base_name": "portrait_EBS_wang_zongguan"
    },
    {
        "char_id": "EBS_xi_teshi",
        "file": "hoi4_portrait_xi_huisuo_clean_1793537091683.jpg",
        "base_name": "portrait_EBS_xi_teshi"
    },
    {
        "char_id": "EBS_dongbei_council",
        "file": "hoi4_portrait_zhang_xueliang_clean_1793537097800.jpg",
        "base_name": "portrait_EBS_dongbei_council"
    },
    {
        "char_id": "EBS_enlightened_teachers",
        "file": "hoi4_portrait_gu_mingyuan_clean_1793537112546.jpg",
        "base_name": "portrait_EBS_enlightened_teachers"
    },
    {
        "char_id": "EBS_haidian_council",
        "file": "hoi4_portrait_liu_pengzhi_clean_1793537100430.jpg",
        "base_name": "portrait_EBS_haidian_council"
    }
]

cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(cascade_path)

def smart_zoom_head_crop(img_path):
    cv_img = cv2.imread(img_path)
    h_img, w_img = cv_img.shape[:2]
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
    
    if len(faces) == 0:
        # Fallback to standard top-focused crop
        fx, fy, fw, fh = w_img // 4, int(h_img * 0.15), w_img // 2, int(h_img * 0.35)
    else:
        # Pick largest face
        faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
        fx, fy, fw, fh = faces[0]
        
    cx = fx + fw / 2.0
    cy = fy + fh / 2.0
    
    # Target crop height: roughly 1.95 * fh (so head/face occupies ~50-55% of portrait)
    crop_h = min(h_img, int(fh * 1.95))
    crop_h = max(660, min(820, crop_h))
    crop_w = int(crop_h * (156.0 / 210.0))
    
    # Place face center at ~38% from top of crop frame
    top = int(cy - crop_h * 0.38)
    left = int(cx - crop_w / 2.0)
    
    # Clamp to boundaries
    if top < 0:
        top = 0
    if top + crop_h > h_img:
        top = h_img - crop_h
    if left < 0:
        left = 0
    if left + crop_w > w_img:
        left = w_img - crop_w
        
    bottom = top + crop_h
    right = left + crop_w
    
    pil_img = Image.open(img_path).convert("RGBA")
    cropped = pil_img.crop((left, top, right, bottom))
    return cropped

def main():
    gfx_entries = []

    print("[*] Performing smart face-zoomed crop on all 9 leader portraits...")
    for item in MAPPINGS:
        src_path = os.path.join(BRAIN_DIR, item["file"])
        cropped = smart_zoom_head_crop(src_path)
        
        # 156x210 leader large
        large_img = cropped.resize((156, 210), Image.Resampling.LANCZOS)
        large_path = os.path.join(OUT_DIR, f"{item['base_name']}_156x210.png")
        large_img.save(large_path, format="PNG")
        
        # 78x105 advisor small
        small_img = cropped.resize((78, 105), Image.Resampling.LANCZOS)
        small_path = os.path.join(OUT_DIR, f"{item['base_name']}_small_78x105.png")
        small_img.save(small_path, format="PNG")
        
        print(f"[OK] Zoomed Head Cropped: {item['base_name']} (large: 156x210, small: 78x105)")
        
        gfx_entries.append(f"""\tspriteType = {{
\t\tname = "GFX_{item['base_name']}"
\t\ttexturefile = "gfx/leaders/EBS/{item['base_name']}_156x210.png"
\t}}
\tspriteType = {{
\t\tname = "GFX_{item['base_name']}_small"
\t\ttexturefile = "gfx/leaders/EBS/{item['base_name']}_small_78x105.png"
\t}}""")

    # Write interface/EBS_characters.gfx
    gfx_content = "spriteTypes = {\n" + "\n".join(gfx_entries) + "\n}\n"
    with open("interface/EBS_characters.gfx", "w", encoding="utf-8") as f:
        f.write(gfx_content)
    print("[OK] Written interface/EBS_characters.gfx successfully with all 9 face-zoomed leaders!")

if __name__ == '__main__':
    main()
