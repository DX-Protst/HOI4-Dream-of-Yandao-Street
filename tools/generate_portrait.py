"""
HOI4 Leader Portrait Pipeline: ComfyUI (钢铁雄心.json) + Chroma Key + Despill
Used by the hoi4-portrait-generator Skill for AI agents.
支持预设画面比例调节 (1:1, 2:3, 3:2, 3:4, 4:3, 9:16, 16:9, 21:9)
内置显存自动释放机制：生图完成后自动彻底 Kill 掉 ComfyUI 进程，避免占用宝贵的 GPU 显存！
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
import psutil

COMFY_ROOT = r"C:\Program Files\Comfyui-WF-2026.8.8\Comfyui-WF-2026.8.8"
COMFY_PYTHON = os.path.join(COMFY_ROOT, "python", "python.exe")
COMFY_MAIN = os.path.join(COMFY_ROOT, "ComfyUI", "main.py")
COMFY_OUTPUT_DIR = os.path.join(COMFY_ROOT, "ComfyUI", "output")
COMFY_API_URL = "http://127.0.0.1:8188"

# 预设比例映射字典（支持简写与标准 ComfyUI ResolutionSelector 选项）
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

def resolve_aspect_ratio(ratio_input):
    """Normalize user ratio string to ComfyUI ResolutionSelector option."""
    key = str(ratio_input).strip()
    if key in ASPECT_RATIO_PRESETS:
        return ASPECT_RATIO_PRESETS[key]
    for k, v in ASPECT_RATIO_PRESETS.items():
        if key.lower() == k.lower():
            return v
    print(f"[!] Warning: Unknown ratio '{ratio_input}'. Supported: {list(ASPECT_RATIO_PRESETS.keys())}. Fallback to 1:1.")
    return "1:1 (Square)"

def kill_comfyui():
    """
    Kill all ComfyUI processes listening on 8188 or running main.py.
    Completely and immediately frees GPU VRAM and system memory.
    """
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
                    except Exception as e:
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
        print(f"[✓] Successfully terminated {killed_count} ComfyUI process(es). GPU VRAM 100% freed!")
    else:
        print("[✓] ComfyUI process is not running. VRAM is already clean.")

def ensure_comfyui_running():
    """Ensure ComfyUI server is running and accessible on port 8188."""
    try:
        req = urllib.request.urlopen(f"{COMFY_API_URL}/system_stats", timeout=2)
        if req.getcode() == 200:
            print("[✓] ComfyUI server is already running and responsive.")
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
                print("[✓] ComfyUI server started successfully.")
                return
        except Exception:
            continue
    raise TimeoutError("Failed to start ComfyUI server within 120 seconds.")

def build_prompt_payload(user_prompt, aspect_ratio="1:1 (Square)", megapixels=1.0, seed=None, steps=25, cfg=3.0):
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
        "31": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["38", 0],
                "positive": ["29", 0],
                "negative": ["36", 0],
                "latent_image": ["35", 0],
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "er_sde",
                "scheduler": "simple",
                "denoise": 1.0
            }
        },
        "37": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["31", 0],
                "vae": ["32", 0]
            }
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["37", 0],
                "filename_prefix": "hoi4_leader_raw"
            }
        }
    }

def remove_greenscreen_and_save(raw_img_path, output_dir, prefix):
    """
    Applies Chroma Keying (green delta) + Despill + Soft Feathering.
    Exports full raw, full transparent, and standard HOI4 portrait crops if bounding box is found.
    """
    os.makedirs(output_dir, exist_ok=True)
    img = Image.open(raw_img_path).convert('RGB')
    orig_w, orig_h = img.size
    rgb = np.array(img, dtype=np.float32)
    
    r = rgb[:, :, 0]
    g = rgb[:, :, 1]
    b = rgb[:, :, 2]
    
    # 1. Delta Keying
    max_rb = np.maximum(r, b)
    green_diff = g - max_rb
    
    lower_th = 15.0
    upper_th = 60.0
    alpha = np.clip(1.0 - (green_diff - lower_th) / (upper_th - lower_th), 0.0, 1.0)
    
    is_bright_green = (g > 100) & (g > r * 1.2) & (g > b * 1.2)
    alpha = np.where(is_bright_green, alpha, 1.0)
    
    # 2. Despill: Neutralize edge green spill
    despill_mask = g > max_rb
    g_despilled = np.where(despill_mask, (r + b) * 0.5, g)
    
    rgba = np.zeros((rgb.shape[0], rgb.shape[1], 4), dtype=np.uint8)
    rgba[:, :, 0] = np.clip(r, 0, 255).astype(np.uint8)
    rgba[:, :, 1] = np.clip(g_despilled, 0, 255).astype(np.uint8)
    rgba[:, :, 2] = np.clip(b, 0, 255).astype(np.uint8)
    rgba[:, :, 3] = np.clip(alpha * 255.0, 0, 255).astype(np.uint8)
    
    cutout = Image.fromarray(rgba, mode='RGBA')
    alpha_blurred = cutout.split()[3].filter(ImageFilter.GaussianBlur(radius=0.7))
    cutout.putalpha(alpha_blurred)
    
    # Raw backup
    raw_save = os.path.join(output_dir, f"{prefix}_raw_{orig_w}x{orig_h}.png")
    img.save(raw_save)
    
    # Transparent full resolution
    cutout_path = os.path.join(output_dir, f"{prefix}_transparent_{orig_w}x{orig_h}.png")
    cutout.save(cutout_path)
    
    # Auto framing for HOI4 156x210
    bbox = cutout.getbbox()
    if bbox:
        bx0, by0, bx1, by1 = bbox
        center_x = (bx0 + bx1) / 2
        bh = by1 - by0
        target_aspect = 156.0 / 210.0
        
        crop_h = min(bh * 1.05, rgb.shape[0])
        crop_w = crop_h * target_aspect
        if crop_w > rgb.shape[1]:
            crop_w = rgb.shape[1]
            crop_h = crop_w / target_aspect
            
        crop_x0 = max(0, int(center_x - crop_w / 2))
        crop_y0 = max(0, int(by0 - 20))
        crop_x1 = min(rgb.shape[1], int(crop_x0 + crop_w))
        crop_y1 = min(rgb.shape[0], int(crop_y0 + crop_h))
        
        cropped = cutout.crop((crop_x0, crop_y0, crop_x1, crop_y1))
        large_portrait = cropped.resize((156, 210), Image.Resampling.LANCZOS)
        large_path = os.path.join(output_dir, f"{prefix}_156x210.png")
        large_portrait.save(large_path)
        
        small_portrait = large_portrait.resize((78, 105), Image.Resampling.LANCZOS)
        small_path = os.path.join(output_dir, f"{prefix}_small_78x105.png")
        small_portrait.save(small_path)
        
        print(f"\n==========================================")
        print(f"[✓] Canvas Resolution:           {orig_w} x {orig_h}")
        print(f"[✓] HOI4 Large Leader (156x210): {large_path}")
        print(f"[✓] HOI4 Small Advisor (78x105): {small_path}")
        print(f"[✓] Transparent Cutout:          {cutout_path}")
        print(f"[✓] Raw Green Screen Master:     {raw_save}")
        print(f"==========================================")
        
        # Output Clausewitz .gfx registration snippet
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
    return cutout_path

def generate_portrait(prompt, output_dir, prefix, ratio="1:1", megapixels=1.0, seed=None, keep_alive=False):
    """
    Main portrait generation workflow.
    Automatically shuts down ComfyUI upon completion if keep_alive is False.
    """
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
                    print(f"[✓] Render completed in {elapsed}s: {raw_path}")
                    result_path = remove_greenscreen_and_save(raw_path, output_dir, prefix)
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
        # 强制清理：生图完成后杀死进程，释放所有显存
        if not keep_alive:
            kill_comfyui()
        else:
            print("[*] --keep-alive specified: Keeping ComfyUI process running.")

if __name__ == "__main__":
    supported_ratios_str = ", ".join(sorted(set(ASPECT_RATIO_PRESETS.keys())))
    parser = argparse.ArgumentParser(description="HOI4 Portrait Pipeline for AI Agents with Aspect Ratio Selection & Auto VRAM Cleanup")
    parser.add_argument("--prompt", type=str, default="", help="Description of character")
    parser.add_argument("--name", type=str, default="portrait_custom_leader", help="Asset prefix name")
    parser.add_argument("--outdir", type=str, default=r"gfx\leaders\custom", help="Target output directory")
    parser.add_argument("--ratio", "-r", type=str, default="1:1", 
                        help=f"Aspect ratio preset. Options: {supported_ratios_str} (Default: 1:1)")
    parser.add_argument("--megapixels", "-m", type=float, default=1.0, 
                        help="Target megapixels (default: 1.0, e.g. 1.0 = ~1024x1024)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--keep-alive", action="store_true", 
                        help="Keep ComfyUI running in background. If omitted, ComfyUI is killed immediately after generation to free VRAM.")
    parser.add_argument("--kill", action="store_true", 
                        help="Kill any running ComfyUI process immediately and exit without generating.")
    args = parser.parse_args()

    # If --kill is requested, terminate and exit
    if args.kill:
        kill_comfyui()
        sys.exit(0)

    if not args.prompt:
        parser.error("--prompt is required unless --kill is specified.")

    full_prompt = args.prompt
    if "绿幕" not in full_prompt and "green screen" not in full_prompt.lower():
        full_prompt = f"纯净平整单色绿幕背景（chroma key #00FF00 green screen background），{full_prompt}，正面特写，干净边缘，棚拍均匀平光照明，背景绝对纯绿色便于抠图"
        
    generate_portrait(full_prompt, args.outdir, args.name, ratio=args.ratio, megapixels=args.megapixels, seed=args.seed, keep_alive=args.keep_alive)
