"""
HOI4 Leader & Advisor Portrait Pipeline:
- ComfyUI Text-to-Image (tools/workflows/钢铁雄心.json) + Chroma Key + Despill
- Image-to-Image / Reference Photo Framing (--from-image)
- Standard Clausewitz Leader Large (156x210) & Canonical Political Advisor Small (65x67)
- Mandatory VRAM Auto-Cleanup (Auto-Kill by default)

Used by the hoi4-portrait-generator Skill for Hearts of Iron IV.
"""

import os
import sys
import json
import time
import argparse
import subprocess
import urllib.request
import urllib.error
import numpy as np
from PIL import Image, ImageFilter
import cv2
import psutil

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) in ("tools", "scripts") else SCRIPT_DIR

LOCAL_WORKFLOW_PATHS = [
    os.path.join(PROJECT_ROOT, "tools", "workflows", "钢铁雄心.json"),
    os.path.join(SCRIPT_DIR, "workflows", "钢铁雄心.json"),
    os.path.join(PROJECT_ROOT, ".agents", "skills", "hoi4-portrait-generator", "resources", "钢铁雄心.json"),
    r"C:\Program Files\Comfyui-WF-2026.8.8\Comfyui-WF-2026.8.8\ComfyUI\user\default\workflows\钢铁雄心.json"
]

NOTE_ASSET_PATHS = [
    os.path.join(PROJECT_ROOT, "tools", "assets", "vanilla_advisor_note.png"),
    os.path.join(PROJECT_ROOT, ".agents", "skills", "hoi4-portrait-generator", "resources", "vanilla_advisor_note.png"),
    os.path.join(SCRIPT_DIR, "assets", "vanilla_advisor_note.png"),
    os.path.join(SCRIPT_DIR, "resources", "vanilla_advisor_note.png")
]

COMFY_ROOT = r"C:\Program Files\Comfyui-WF-2026.8.8\Comfyui-WF-2026.8.8"
COMFY_PYTHON = os.path.join(COMFY_ROOT, "python", "python.exe")
COMFY_MAIN = os.path.join(COMFY_ROOT, "ComfyUI", "main.py")
COMFY_OUTPUT_DIR = os.path.join(COMFY_ROOT, "ComfyUI", "output")
COMFY_API_URL = "http://127.0.0.1:8188"

# Aspect ratio presets
ASPECT_RATIO_PRESETS = {
    "1:1": "1:1 (Square)",
    "square": "1:1 (Square)",
    "1:1 (Square)": "1:1 (Square)",
    
    "2:3": "2:3 (Portrait Photo)",
    "2:3 (Portrait Photo)": "2:3 (Portrait Photo)",
    
    "3:2": "3:2 (Photo)",
    "3:2 (Photo)": "3:2 (Photo)",
    
    "3:4": "3:4 (Portrait Standard)",
    "3:4 (Portrait Standard)": "3:4 (Portrait Standard)",
    
    "4:3": "4:3 (Standard)",
    "4:3 (Standard)": "4:3 (Standard)",
    
    "9:16": "9:16 (Portrait Widescreen)",
    "9:16 (Portrait Widescreen)": "9:16 (Portrait Widescreen)",
    
    "16:9": "16:9 (Widescreen)",
    "16:9 (Widescreen)": "16:9 (Widescreen)",
    "widescreen": "16:9 (Widescreen)",
    
    "21:9": "21:9 (Ultrawide)",
    "21:9 (Ultrawide)": "21:9 (Ultrawide)"
}

face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(face_cascade_path)

def resolve_aspect_ratio(ratio_input):
    """Normalize user ratio string to ComfyUI ResolutionSelector option."""
    key = str(ratio_input).strip()
    if key in ASPECT_RATIO_PRESETS:
        return ASPECT_RATIO_PRESETS[key]
    for k, v in ASPECT_RATIO_PRESETS.items():
        if key.lower() == k.lower():
            return v
    print(f"[!] Warning: Unknown ratio '{ratio_input}'. Fallback to 1:1.")
    return "1:1 (Square)"

def kill_comfyui():
    """Kill all ComfyUI processes listening on 8188 or running main.py."""
    print("[*] Releasing GPU VRAM: Terminating ComfyUI process(es)...")
    killed_count = 0

    # 1. Kill by listening port 8188
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == psutil.CONN_LISTEN and conn.laddr.port == 8188:
                if conn.pid and conn.pid != os.getpid():
                    try:
                        p = psutil.Process(conn.pid)
                        print(f"    - Killing PID {conn.pid} ({p.name()})...")
                        p.kill()
                        killed_count += 1
                    except Exception:
                        pass
    except Exception:
        pass

    # 2. Kill by command line detection (ComfyUI / main.py)
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmd = p.info.get('cmdline') or []
            cmd_str = " ".join(cmd).lower()
            if 'comfyui' in cmd_str and 'main.py' in cmd_str and p.info['pid'] != os.getpid():
                print(f"    - Killing ComfyUI background PID {p.info['pid']}...")
                p.kill()
                killed_count += 1
        except Exception:
            pass

    # 3. Windows PowerShell fallback safeguard
    if os.name == 'nt':
        try:
            subprocess.run([
                "powershell", "-NoProfile", "-Command",
                "Get-NetTCPConnection -LocalPort 8188 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
            ], capture_output=True, timeout=5)
        except Exception:
            pass

    if killed_count > 0:
        print(f"[OK] Successfully terminated {killed_count} ComfyUI process(es). GPU VRAM 100% freed!")
    else:
        print("[OK] ComfyUI process is not running. VRAM is already clean.")

def ensure_comfyui_running():
    """Ensure ComfyUI server is running and accessible on port 8188."""
    try:
        req = urllib.request.urlopen(f"{COMFY_API_URL}/system_stats", timeout=2)
        if req.getcode() == 200:
            print("[OK] ComfyUI server is already running and responsive.")
            return
    except Exception:
        pass

    print("[!] ComfyUI server is not responding. Starting background service...")
    cmd = [
        COMFY_PYTHON,
        COMFY_MAIN,
        "--listen", "127.0.0.1",
        "--port", "8188",
        "--disable-auto-launch"
    ]
    flags = 0
    if os.name == 'nt':
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

    subprocess.Popen(cmd, cwd=os.path.dirname(COMFY_MAIN), creationflags=flags)
    
    print("[*] Waiting for ComfyUI to finish initializing custom nodes...")
    for _ in range(60):
        time.sleep(2)
        try:
            req = urllib.request.urlopen(f"{COMFY_API_URL}/system_stats", timeout=2)
            if req.getcode() == 200:
                print("[OK] ComfyUI server started successfully.")
                return
        except Exception:
            continue
    raise TimeoutError("Failed to start ComfyUI server within 120 seconds.")

def load_note_asset():
    """Load the official HOI4 advisor memo note layer."""
    for p in NOTE_ASSET_PATHS:
        if os.path.exists(p):
            return Image.open(p).convert("RGBA")
    # Fallback blank note
    note = Image.new("RGBA", (65, 67), (0, 0, 0, 0))
    draw = ImageDraw.Draw(note)
    draw.polygon([(30, 36), (56, 37), (54, 65), (28, 64)], fill=(234, 214, 182, 255), outline=(140, 120, 95, 255))
    return note

def smart_face_crop(pil_img, target_aspect=156.0/210.0, zoom_factor=1.9):
    """Smart face detection and centering for portrait composition."""
    cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGBA2BGR)
    h_img, w_img = cv_img.shape[:2]
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
    
    if len(faces) == 0:
        # Fallback to upper center crop
        cx = w_img / 2.0
        cy = h_img * 0.35
        crop_h = int(h_img * 0.8)
    else:
        faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
        fx, fy, fw, fh = faces[0]
        cx = fx + fw / 2.0
        cy = fy + fh / 2.0
        crop_h = min(h_img, int(fh * zoom_factor))
        
    crop_w = int(crop_h * target_aspect)
    if crop_w > w_img:
        crop_w = w_img
        crop_h = int(crop_w / target_aspect)
        
    top = int(cy - crop_h * 0.38)
    left = int(cx - crop_w / 2.0)
    top = max(0, min(h_img - crop_h, top))
    left = max(0, min(w_img - crop_w, left))
    
    return pil_img.crop((left, top, left + crop_w, top + crop_h))

def format_canonical_advisor_small(pil_img):
    """
    Format a portrait image into the official HOI4 Political Advisor standard:
    - Exactly 65x67 pixels RGBA
    - Tilted photo card (-3.5 deg) with dark border
    - Soft Gaussian drop shadow
    - Official HOI4 memo paper note in lower-right
    """
    card_w = 34
    card_h = 49
    
    # Crop head and shoulders
    cropped = smart_face_crop(pil_img, target_aspect=card_w/card_h, zoom_factor=1.85)
    photo = cropped.resize((card_w, card_h), Image.Resampling.LANCZOS)
    
    # 1px border around photo
    framed_photo = Image.new("RGBA", (card_w + 2, card_h + 2), (18, 18, 18, 255))
    framed_photo.paste(photo, (1, 1))

    # Rotate 3.5 degrees (canonical HOI4 card tilt)
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
    
    note_img = load_note_asset()
    canvas.paste(note_img, (0, 0), note_img)
    return canvas

def chroma_key_despill(img_np):
    """影视级色差键控与溢色抑制算法 (Delta Keying & Despill)."""
    r = img_np[:, :, 0].astype(float)
    g = img_np[:, :, 1].astype(float)
    b = img_np[:, :, 2].astype(float)
    
    max_rb = np.maximum(r, b)
    green_diff = g - max_rb
    
    threshold_low = 15.0
    threshold_high = 70.0
    alpha = np.clip(1.0 - (green_diff - threshold_low) / (threshold_high - threshold_low), 0.0, 1.0)
    
    sat_factor = (g - np.minimum(r, b)) / (g + 1e-5)
    is_vibrant_green = (g > 80) & (g > r * 1.25) & (g > b * 1.25) & (sat_factor > 0.3)
    alpha[is_vibrant_green] = np.minimum(alpha[is_vibrant_green], 0.0)
    
    # Despill
    g_clamped = np.minimum(g, max_rb * 1.05)
    
    rgba = np.zeros((img_np.shape[0], img_np.shape[1], 4), dtype=np.uint8)
    rgba[:, :, 0] = r.astype(np.uint8)
    rgba[:, :, 1] = g_clamped.astype(np.uint8)
    rgba[:, :, 2] = b.astype(np.uint8)
    rgba[:, :, 3] = (alpha * 255.0).astype(np.uint8)
    return rgba

def process_portrait_assets(source_pil, output_dir, prefix, raw_save_path=None):
    """Generate both 156x210 Leader Large and 65x67 Canonical Advisor Small assets."""
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 156x210 Leader Large
    large_cropped = smart_face_crop(source_pil, target_aspect=156.0/210.0, zoom_factor=1.95)
    large_img = large_cropped.resize((156, 210), Image.Resampling.LANCZOS)
    large_path = os.path.join(output_dir, f"{prefix}_156x210.png")
    large_img.save(large_path, format="PNG")
    
    # 2. 65x67 Canonical Advisor Small
    advisor_img = format_canonical_advisor_small(source_pil)
    small_path = os.path.join(output_dir, f"{prefix}_small_65x67.png")
    advisor_img.save(small_path, format="PNG")
    
    # Backwards compatibility aliases
    small_std_path = os.path.join(output_dir, f"{prefix}_small.png")
    advisor_img.save(small_std_path, format="PNG")
    legacy_small_path = os.path.join(output_dir, f"{prefix}_small_78x105.png")
    advisor_img.save(legacy_small_path, format="PNG")
    
    orig_w, orig_h = source_pil.size
    print(f"\n==========================================")
    print(f"[OK] Canvas Resolution:            {orig_w} x {orig_h}")
    print(f"[OK] HOI4 Large Leader (156x210):  {large_path}")
    print(f"[OK] HOI4 Small Advisor (65x67):   {small_path}")
    if raw_save_path:
        print(f"[OK] Raw Green Screen Master:      {raw_save_path}")
    print(f"==========================================")
    
    rel_large = os.path.relpath(large_path, os.getcwd()).replace("\\", "/")
    rel_small = os.path.relpath(small_path, os.getcwd()).replace("\\", "/")
    print("\n--- Clausewitz interface/*.gfx Snippet ---")
    print(f"""spriteTypes = {{
    spriteType = {{
        name = "GFX_{prefix}"
        texturefile = "{rel_large}"
    }}
    spriteType = {{
        name = "GFX_{prefix}_small"
        texturefile = "{rel_small}"
    }}
}}""")
    print("------------------------------------------\n")
    return large_path

def build_prompt_payload(user_prompt, aspect_ratio="1:1 (Square)", megapixels=1.0, seed=None):
    if seed is None:
        seed = int(time.time() * 1000) % 4294967295

    ratio_choice = resolve_aspect_ratio(aspect_ratio)

    return {
        "28": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "moss_image_sft_nvfp4.safetensors",
                "weight_dtype": "default"
            }
        },
        "41": {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "model": ["28", 0],
                "lora_name": "KOOK-MOSS-SFT-观澜.safetensors",
                "strength_model": 1.0
            }
        },
        "38": {
            "class_type": "SkipLayerGuidanceDiTSimple",
            "inputs": {
                "model": ["41", 0],
                "double_layers": "",
                "single_layers": "22",
                "start_percent": 0.0,
                "end_percent": 0.5
            }
        },
        "30": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": "qwen3.5_9b_int8_convrot.safetensors",
                "type": "moss_image",
                "device": "default"
            }
        },
        "32": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "flux2-vae.safetensors"
            }
        },
        "71": {
            "class_type": "PrimitiveStringMultiline",
            "inputs": {
                "value": user_prompt
            }
        },
        "80": {
            "class_type": "QwenMossExpander",
            "inputs": {
                "user_prompt": ["71", 0],
                "preset": "MOSS核心版 (快速/推荐 8k上下文)",
                "model_name": "Qwen3.8-9B-Distill-uncensored-heretic.i1-Q6_K.gguf",
                "max_tokens": 1024,
                "temperature": 0.65,
                "top_p": 0.9,
                "seed": seed,
                "auto_unload_vram": True,
                "enable_thinking": False
            }
        },
        "79": {
            "class_type": "PreviewTextNode",
            "inputs": {
                "text": ["80", 0]
            }
        },
        "29": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["30", 0],
                "text": ["79", 0]
            }
        },
        "36": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["30", 0],
                "text": "worst quality, bad anatomy, watermark, jpeg artifact, blurry, shadows on green screen, non-green background elements"
            }
        },
        "19": {
            "class_type": "ResolutionSelector",
            "inputs": {
                "aspect_ratio": ratio_choice,
                "megapixels": float(megapixels),
                "multiple": 8
            }
        },
        "35": {
            "class_type": "EmptyFlux2LatentImage",
            "inputs": {
                "width": ["19", 0],
                "height": ["19", 1],
                "batch_size": 1
            }
        },
        "33": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["38", 0],
                "positive": ["29", 0],
                "negative": ["36", 0],
                "latent_image": ["35", 0],
                "seed": seed,
                "steps": 25,
                "cfg": 3.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0
            }
        },
        "34": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["33", 0],
                "vae": ["32", 0]
            }
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "HOI4_Portrait_Raw",
                "images": ["34", 0]
            }
        }
    }

def generate_portrait(prompt, output_dir, prefix, ratio="1:1", megapixels=1.0, seed=None, keep_alive=False):
    """ComfyUI Text-to-Image pipeline with auto VRAM cleanup."""
    try:
        ensure_comfyui_running()
        resolved_ratio = resolve_aspect_ratio(ratio)
        print(f"[*] Chosen Aspect Ratio: {resolved_ratio} (Target MP: {megapixels})")
        
        payload = build_prompt_payload(prompt, aspect_ratio=resolved_ratio, megapixels=megapixels, seed=seed)
        post_data = json.dumps({"prompt": payload}).encode('utf-8')
        req = urllib.request.Request(f"{COMFY_API_URL}/prompt", data=post_data, headers={'Content-Type': 'application/json'})
        
        print(f"[*] Posting prompt to ComfyUI ({COMFY_API_URL})...")
        resp = urllib.request.urlopen(req)
        prompt_id = json.loads(resp.read().decode('utf-8'))['prompt_id']
        print(f"[*] Generation active! Task ID: {prompt_id}")
        
        start_t = time.time()
        result_path = None
        while True:
            time.sleep(2)
            elapsed = int(time.time() - start_t)
            try:
                h_req = urllib.request.urlopen(f"{COMFY_API_URL}/history/{prompt_id}")
                h_data = json.loads(h_req.read().decode('utf-8'))
                if prompt_id in h_data:
                    item = h_data[prompt_id]
                    images = item.get('outputs', {}).get('9', {}).get('images', [])
                    if not images:
                        raise RuntimeError("No image output recorded.")
                    filename = images[0]['filename']
                    subfolder = images[0].get('subfolder', '')
                    raw_path = os.path.join(COMFY_OUTPUT_DIR, subfolder, filename)
                    print(f"[OK] Render completed in {elapsed}s: {raw_path}")
                    
                    # Chroma-key green screen and process
                    raw_img = Image.open(raw_path).convert("RGB")
                    rgba_arr = chroma_key_despill(np.array(raw_img))
                    cutout = Image.fromarray(rgba_arr)
                    
                    raw_save = os.path.join(output_dir, f"{prefix}_raw_{raw_img.width}x{raw_img.height}.png")
                    raw_img.save(raw_save)
                    cutout_path = os.path.join(output_dir, f"{prefix}_transparent_{cutout.width}x{cutout.height}.png")
                    cutout.save(cutout_path)
                    
                    result_path = process_portrait_assets(cutout, output_dir, prefix, raw_save_path=raw_save)
                    break
                else:
                    print(f"[*] Rendering in progress... ({elapsed}s)")
            except Exception as e:
                if "No image output" in str(e):
                    raise e
                print(f"[!] Polling: {e}")
                
            if elapsed > 300:
                raise TimeoutError("Render timed out after 300s.")
                
        return result_path
    finally:
        if not keep_alive:
            kill_comfyui()
        else:
            print("[*] --keep-alive specified: Keeping ComfyUI process running.")

if __name__ == "__main__":
    supported_ratios_str = ", ".join(sorted(set(ASPECT_RATIO_PRESETS.keys())))
    parser = argparse.ArgumentParser(description="HOI4 Portrait Pipeline with Dual Text-to-Image / Img2Img Post-Processing & Auto VRAM Cleanup")
    parser.add_argument("--prompt", type=str, default="", help="Description of character (for text-to-image)")
    parser.add_argument("--from-image", type=str, default="", help="Process an existing photo/portrait into HOI4 156x210 & 65x67 assets")
    parser.add_argument("--name", type=str, default="portrait_custom_leader", help="Asset prefix name")
    parser.add_argument("--outdir", type=str, default=r"gfx\leaders\custom", help="Target output directory")
    parser.add_argument("--ratio", "-r", type=str, default="1:1", 
                        help=f"Aspect ratio preset for ComfyUI. Options: {supported_ratios_str} (Default: 1:1)")
    parser.add_argument("--megapixels", "-m", type=float, default=1.0, 
                        help="Target megapixels (default: 1.0, e.g. 1.0 = ~1024x1024)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--keep-alive", action="store_true", 
                        help="Keep ComfyUI running in background. If omitted, ComfyUI is killed immediately after generation.")
    parser.add_argument("--kill", action="store_true", 
                        help="Kill any running ComfyUI process immediately and exit without generating.")
    args = parser.parse_args()

    # 1. Kill command
    if args.kill:
        kill_comfyui()
        sys.exit(0)

    # 2. From-image mode (Real-world reference or existing portrait)
    if args.from_image:
        if not os.path.exists(args.from_image):
            print(f"[!] Error: Source image file not found: {args.from_image}")
            sys.exit(1)
        src_pil = Image.open(args.from_image).convert("RGBA")
        process_portrait_assets(src_pil, args.outdir, args.name)
        sys.exit(0)

    # 3. ComfyUI Text-to-Image mode
    if not args.prompt:
        parser.error("--prompt (or --from-image / --kill) is required.")

    full_prompt = args.prompt
    if "绿幕" not in full_prompt and "green screen" not in full_prompt.lower():
        full_prompt = f"纯净平整单色绿幕背景（chroma key #00FF00 green screen background），{full_prompt}，正面特写，干净边缘，棚拍均匀平光照明，背景绝对纯绿色便于抠图"
        
    generate_portrait(full_prompt, args.outdir, args.name, ratio=args.ratio, megapixels=args.megapixels, seed=args.seed, keep_alive=args.keep_alive)
