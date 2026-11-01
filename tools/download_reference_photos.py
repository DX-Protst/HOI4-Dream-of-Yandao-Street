import os
import urllib.request
from PIL import Image

OUT_DIR = "tools/reference_photos"
os.makedirs(OUT_DIR, exist_ok=True)

TARGETS = [
    {
        "char_id": "EBS_leader_chen_zhuanyuan",
        "name": "chen_baosheng",
        "display_name": "陈宝生",
        "url": "https://upload.wikimedia.org/wikipedia/commons/6/64/Chen_Baosheng_2019.jpg"
    },
    {
        "char_id": "EBS_huai_zonggong",
        "name": "huai_jinpeng",
        "display_name": "怀进鹏",
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/e0/Minister_of_Education_Huai_Jinpeng.jpg"
    },
    {
        "char_id": "EBS_zhou_zongdao",
        "name": "zhou_ji",
        "display_name": "周济",
        "url": "https://img1.baidu.com/it/u=266753790,1040479182&fm=253&fmt=auto&app=138&f=BMP?w=500&h=345"
    },
    {
        "char_id": "EBS_wang_sichang",
        "name": "wang_dengfeng",
        "display_name": "王登峰",
        "url": "https://img0.baidu.com/it/u=3789659770,2565982613&fm=253&fmt=auto&app=138&f=JPEG?w=751&h=500"
    },
    {
        "char_id": "EBS_wang_zongguan",
        "name": "wang_shengzhan",
        "display_name": "王胜战",
        "url": "https://img0.baidu.com/it/u=598112280,3215176140&fm=253&fmt=auto&app=120&f=JPEG?w=606&h=361"
    },
    {
        "char_id": "EBS_xi_teshi",
        "name": "xi_huisuo",
        "display_name": "郗会锁",
        "url": "http://t14.baidu.com/it/u=119218056,3054373423&fm=224&app=112&f=JPEG?w=500&h=500"
    },
    {
        "char_id": "EBS_dongbei_council",
        "name": "zhang_xueliang",
        "display_name": "张学良 (东三省名校联合公社)",
        "url": "https://upload.wikimedia.org/wikipedia/commons/9/9b/Chang_Shueliang.jpg"
    },
    {
        "char_id": "EBS_haidian_council",
        "name": "liu_pengzhi",
        "display_name": "刘彭芝 (海淀贵胄校董会)",
        "url": "https://img0.baidu.com/it/u=3500892502,1737700043&fm=253&fmt=auto?w=1079&h=713"
    },
    {
        "char_id": "EBS_enlightened_teachers",
        "name": "gu_mingyuan",
        "display_name": "顾明远 (北方开明教师联合会)",
        "url": "https://img1.baidu.com/it/u=3036608704,482254091&fm=253&fmt=auto&app=120&f=JPEG?w=750&h=500"
    }
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://image.baidu.com/'
}

print("[*] Downloading real reference photos from the web...")

for t in TARGETS:
    out_path = os.path.join(OUT_DIR, f"{t['name']}.jpg")
    try:
        req = urllib.request.Request(t['url'], headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
            with open(out_path, 'wb') as f:
                f.write(content)
        
        # Verify image
        im = Image.open(out_path)
        im.load()
        # Convert and re-save as clean RGB JPEG
        im.convert("RGB").save(out_path, "JPEG", quality=95)
        print(f"[OK] Downloaded & Verified: {t['display_name']} -> {out_path} (size: {im.size})")
    except Exception as e:
        print(f"[!] Failed to download {t['display_name']}: {e}")
