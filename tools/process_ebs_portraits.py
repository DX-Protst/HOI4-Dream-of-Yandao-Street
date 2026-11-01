import os
from PIL import Image

BRAIN_DIR = r"C:\Users\10431\.gemini\antigravity\brain\bcf94466-2063-40f3-abf4-5a33f63af215"
OUT_DIR = "gfx/leaders/EBS"
os.makedirs(OUT_DIR, exist_ok=True)

MAPPINGS = [
    {
        "char_id": "EBS_leader_chen_zhuanyuan",
        "file": "chen_baosheng_hoi4_portrait_1793517258775.jpg",
        "base_name": "portrait_EBS_leader_chen_zhuanyuan"
    },
    {
        "char_id": "EBS_huai_zonggong",
        "file": "huai_jinpeng_hoi4_portrait_1793517296704.jpg",
        "base_name": "portrait_EBS_huai_zonggong"
    },
    {
        "char_id": "EBS_zhou_zongdao",
        "file": "zhou_ji_hoi4_portrait_1793517296234.jpg",
        "base_name": "portrait_EBS_zhou_zongdao"
    },
    {
        "char_id": "EBS_wang_sichang",
        "file": "hoi4_portrait_wang_dengfeng_1793517304480.jpg",
        "base_name": "portrait_EBS_wang_sichang"
    },
    {
        "char_id": "EBS_wang_zongguan",
        "file": "hoi4_leader_wang_shengzhan_clean_1793517324679.jpg",
        "base_name": "portrait_EBS_wang_zongguan"
    },
    {
        "char_id": "EBS_xi_teshi",
        "file": "xi_huisuo_portrait_1793517304502.jpg",
        "base_name": "portrait_EBS_xi_teshi"
    },
    {
        "char_id": "EBS_dongbei_council",
        "file": "hoi4_dongbei_schools_leader_1793517312932.jpg",
        "base_name": "portrait_EBS_dongbei_council"
    },
    {
        "char_id": "EBS_enlightened_teachers",
        "file": "hoi4_northern_teachers_union_leader_1793517312562.jpg",
        "base_name": "portrait_EBS_enlightened_teachers"
    },
    {
        "char_id": "EBS_haidian_council",
        "file": "hoi4_haidian_aristocrat_leader_1793517314986.jpg",
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
    
    print(f"[OK] Processed: {item['base_name']} (large & small)")
    
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
print("[OK] Written interface/EBS_characters.gfx successfully!")
