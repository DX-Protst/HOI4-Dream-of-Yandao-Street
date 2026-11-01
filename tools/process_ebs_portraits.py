import os
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

def crop_and_resize(img, target_w, target_h):
    w, h = img.size
    target_aspect = target_w / target_h
    current_aspect = w / h
    
    if current_aspect > target_aspect:
        # Image is wider than target aspect: crop width
        new_w = int(h * target_aspect)
        offset_x = (w - new_w) // 2
        cropped = img.crop((offset_x, 0, offset_x + new_w, h))
    else:
        # Image is taller than target aspect: crop height
        new_h = int(w / target_aspect)
        offset_y = (h - new_h) // 2
        cropped = img.crop((0, offset_y, w, offset_y + new_h))
        
    return cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)

def main():
    gfx_entries = []

    for item in MAPPINGS:
        src_path = os.path.join(BRAIN_DIR, item["file"])
        img = Image.open(src_path).convert("RGBA")
        
        # 156x210 leader large
        large_img = crop_and_resize(img, 156, 210)
        large_path = os.path.join(OUT_DIR, f"{item['base_name']}_156x210.png")
        large_img.save(large_path, format="PNG")
        
        # 78x105 advisor small
        small_img = crop_and_resize(img, 78, 105)
        small_path = os.path.join(OUT_DIR, f"{item['base_name']}_small_78x105.png")
        small_img.save(small_path, format="PNG")
        
        print(f"[OK] Processed: {item['base_name']} (large: 156x210, small: 78x105)")
        
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
    print("[OK] Written interface/EBS_characters.gfx successfully with all 9 leaders!")

if __name__ == '__main__':
    main()
