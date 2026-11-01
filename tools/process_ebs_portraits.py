import os
import cv2
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

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

# Extract clean paper note template from vanilla
fadden = Image.open('tools/recent_portrait_AST_arthur_fadden_small.png')
f_arr = np.array(fadden)
note_poly = np.array([[30, 36], [56, 37], [54, 65], [28, 64]], dtype=np.int32)
note_only = np.zeros_like(f_arr)
cv2.fillPoly(note_only, [note_poly], (1, 1, 1, 1))
note_mask_dilated = cv2.dilate(note_only[:, :, 0], cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)))
clean_note_arr = np.zeros_like(f_arr)
clean_note_arr[note_mask_dilated > 0] = f_arr[note_mask_dilated > 0]
note_img = Image.fromarray(clean_note_arr)

cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(cascade_path)

def smart_zoom_head_crop_large(src_path):
    cv_img = cv2.imread(src_path)
    h_img, w_img = cv_img.shape[:2]
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
    
    if len(faces) == 0:
        fx, fy, fw, fh = w_img // 4, int(h_img * 0.15), w_img // 2, int(h_img * 0.35)
    else:
        faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
        fx, fy, fw, fh = faces[0]
        
    cx = fx + fw / 2.0
    cy = fy + fh / 2.0
    
    crop_h = min(h_img, int(fh * 1.95))
    crop_h = max(660, min(820, crop_h))
    crop_w = int(crop_h * (156.0 / 210.0))
    
    top = int(cy - crop_h * 0.38)
    left = int(cx - crop_w / 2.0)
    
    top = max(0, min(h_img - crop_h, top))
    left = max(0, min(w_img - crop_w, left))
        
    bottom = top + crop_h
    right = left + crop_w
    
    pil_img = Image.open(src_path).convert("RGBA")
    return pil_img.crop((left, top, right, bottom))

def create_canonical_advisor_small(src_path):
    cv_img = cv2.imread(src_path)
    h_img, w_img = cv_img.shape[:2]
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
    if len(faces) > 0:
        faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
        fx, fy, fw, fh = faces[0]
    else:
        fx, fy, fw, fh = w_img // 4, int(h_img * 0.15), w_img // 2, int(h_img * 0.35)

    cx = fx + fw / 2.0
    cy = fy + fh / 2.0

    card_w = 34
    card_h = 49
    crop_h = int(fh * 1.85)
    crop_w = int(crop_h * (card_w / card_h))
    top = max(0, min(h_img - crop_h, int(cy - crop_h * 0.38)))
    left = max(0, min(w_img - crop_w, int(cx - crop_w / 2.0)))

    pil_src = Image.open(src_path).convert("RGBA")
    crop = pil_src.crop((left, top, left + crop_w, top + crop_h))
    photo = crop.resize((card_w, card_h), Image.Resampling.LANCZOS)

    framed_photo = Image.new("RGBA", (card_w + 2, card_h + 2), (18, 18, 18, 255))
    framed_photo.paste(photo, (1, 1))

    # Rotate 3.5 degrees (canonical HOI4 advisor card tilt)
    rotated_card = framed_photo.rotate(3.5, expand=True, resample=Image.Resampling.BICUBIC)

    # Soft drop shadow
    r_alpha = np.array(rotated_card.split()[-1])
    s_arr = np.zeros((rotated_card.size[1], rotated_card.size[0], 4), dtype=np.uint8)
    s_arr[:, :, 3] = (r_alpha * 0.70).astype(np.uint8)
    shadow = Image.fromarray(s_arr).filter(ImageFilter.GaussianBlur(radius=2.5))

    canvas = Image.new("RGBA", (65, 67), (0, 0, 0, 0))
    pos_x = 6
    pos_y = 4
    canvas.paste(shadow, (pos_x + 2, pos_y + 3), shadow)
    canvas.paste(rotated_card, (pos_x, pos_y), rotated_card)
    canvas.paste(note_img, (0, 0), note_img)
    return canvas

def main():
    gfx_entries = []

    print("[*] Processing all 9 leader large portraits and canonical 65x67 advisor small portraits...")
    for item in MAPPINGS:
        src_path = os.path.join(BRAIN_DIR, item["file"])
        
        # 1. 156x210 Leader Large
        large_crop = smart_zoom_head_crop_large(src_path)
        large_img = large_crop.resize((156, 210), Image.Resampling.LANCZOS)
        large_path = os.path.join(OUT_DIR, f"{item['base_name']}_156x210.png")
        large_img.save(large_path, format="PNG")
        
        # 2. Canonical 65x67 Advisor Small (HOI4 official idea/advisor format)
        small_advisor = create_canonical_advisor_small(src_path)
        
        # Save as canonical _small_65x67.png and update legacy _small_78x105.png for safety
        small_65_path = os.path.join(OUT_DIR, f"{item['base_name']}_small_65x67.png")
        small_advisor.save(small_65_path, format="PNG")
        
        legacy_path = os.path.join(OUT_DIR, f"{item['base_name']}_small_78x105.png")
        small_advisor.save(legacy_path, format="PNG")
        
        print(f"[OK] {item['base_name']}: Large (156x210) & Canonical Advisor (65x67)")
        
        gfx_entries.append(f"""\tspriteType = {{
\t\tname = "GFX_{item['base_name']}"
\t\ttexturefile = "gfx/leaders/EBS/{item['base_name']}_156x210.png"
\t}}
\tspriteType = {{
\t\tname = "GFX_{item['base_name']}_small"
\t\ttexturefile = "gfx/leaders/EBS/{item['base_name']}_small_65x67.png"
\t}}""")

    # Write interface/EBS_characters.gfx
    gfx_content = "spriteTypes = {\n" + "\n".join(gfx_entries) + "\n}\n"
    with open("interface/EBS_characters.gfx", "w", encoding="utf-8") as f:
        f.write(gfx_content)
    print("[OK] Written interface/EBS_characters.gfx successfully with 65x67 canonical advisor portraits!")

if __name__ == '__main__':
    main()
