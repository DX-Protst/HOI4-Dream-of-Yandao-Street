"""
HOI4 Focus Icon Generator via ComfyUI & Chroma-Key Despill
Generates focus icons (100x100 max dimension, RGBA transparent PNG) on green screen #00FF00
Supports --focus-id for loading standardized locked prompts from tools/ebs_focus_prompts_unified.json
Includes automatic VRAM cleanup.
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

# Ensure UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMFY_ROOT = r"C:\Program Files\Comfyui-WF-2026.8.8\Comfyui-WF-2026.8.8"
COMFY_PYTHON = os.path.join(COMFY_ROOT, "python", "python.exe")
COMFY_MAIN = os.path.join(COMFY_ROOT, "ComfyUI", "main.py")
COMFY_API_URL = "http://127.0.0.1:8188"
PROMPT_BOOK_PATH = os.path.join(PROJECT_ROOT, "tools", "ebs_focus_prompts_unified.json")

def kill_comfyui():
    """Kill all ComfyUI processes to immediately free GPU VRAM."""
    print("[*] Releasing GPU VRAM: Terminating ComfyUI process(es)...")
    killed_count = 0
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == psutil.CONN_LISTEN and conn.laddr.port == 8188:
                if conn.pid and conn.pid != os.getpid():
                    try:
                        p = psutil.Process(conn.pid)
                        p.kill()
                        killed_count += 1
                    except Exception:
                        pass
    except Exception:
        pass

    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmd = p.info.get('cmdline') or []
            cmd_str = " ".join(cmd).lower()
            if 'comfyui' in cmd_str and 'main.py' in cmd_str and p.info['pid'] != os.getpid():
                p.kill()
                killed_count += 1
        except Exception:
            pass

    if os.name == 'nt':
        try:
            subprocess.run([
                "powershell", "-NoProfile", "-Command",
                "Get-NetTCPConnection -LocalPort 8188 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
            ], capture_output=True, timeout=5)
        except Exception:
            pass

    if killed_count > 0:
        print(f"[OK] Terminated {killed_count} ComfyUI process(es). GPU VRAM 100% freed!")
    else:
        print("[OK] ComfyUI process is not running. VRAM clean.")

def ensure_comfyui_running():
    try:
        req = urllib.request.urlopen(f"{COMFY_API_URL}/system_stats", timeout=2)
        if req.getcode() == 200:
            return
    except Exception:
        pass

    print("[!] ComfyUI server is not responding. Starting background service...")
    cmd = [COMFY_PYTHON, COMFY_MAIN, "--listen", "127.0.0.1", "--port", "8188", "--disable-auto-launch"]
    flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS if os.name == 'nt' else 0
    subprocess.Popen(cmd, cwd=os.path.dirname(COMFY_MAIN), creationflags=flags)
    
    for _ in range(60):
        time.sleep(2)
        try:
            req = urllib.request.urlopen(f"{COMFY_API_URL}/system_stats", timeout=2)
            if req.getcode() == 200:
                print("[OK] ComfyUI server started successfully.")
                return
        except Exception:
            continue
    raise TimeoutError("Failed to start ComfyUI server within 120s.")

def build_workflow_payload(prompt_text, seed=None, steps=25, cfg=3.0):
    if seed is None:
        seed = int(time.time() * 1000) % 4294967295

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
                "value": prompt_text
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
                "text": "worst quality, bad anatomy, watermark, text, signature, jpeg artifact, blurry, realistic photo background, complex environment behind object, shadows on green screen, non-green background elements"
            }
        },
        "19": {
            "class_type": "ResolutionSelector",
            "inputs": {
                "aspect_ratio": "1:1 (Square)",
                "megapixels": 0.5,
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
                "steps": steps,
                "cfg": cfg,
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
                "filename_prefix": "HOI4_Focus_Raw",
                "images": ["34", 0]
            }
        }
    }

def chroma_key_despill(img_np):
    r = img_np[:, :, 0].astype(float)
    g = img_np[:, :, 1].astype(float)
    b = img_np[:, :, 2].astype(float)
    
    max_rb = np.maximum(r, b)
    green_diff = g - max_rb
    
    threshold_low = 18.0
    threshold_high = 65.0
    alpha = np.clip(1.0 - (green_diff - threshold_low) / (threshold_high - threshold_low), 0.0, 1.0)
    
    sat_factor = (g - np.minimum(r, b)) / (g + 1e-5)
    is_vibrant_green = (g > 80) & (g > r * 1.25) & (g > b * 1.25) & (sat_factor > 0.3)
    alpha[is_vibrant_green] = np.minimum(alpha[is_vibrant_green], 0.0)
    
    g_clamped = np.minimum(g, max_rb * 1.05)
    
    rgba = np.zeros((img_np.shape[0], img_np.shape[1], 4), dtype=np.uint8)
    rgba[:, :, 0] = r.astype(np.uint8)
    rgba[:, :, 1] = g_clamped.astype(np.uint8)
    rgba[:, :, 2] = b.astype(np.uint8)
    rgba[:, :, 3] = (alpha * 255.0).astype(np.uint8)
    return rgba

def process_goal_icon(raw_path, output_dir, icon_name):
    os.makedirs(output_dir, exist_ok=True)
    raw_img = Image.open(raw_path).convert("RGB")
    rgba_arr = chroma_key_despill(np.array(raw_img))
    cutout = Image.fromarray(rgba_arr)
    
    bbox = cutout.getbbox()
    if bbox:
        cutout = cutout.crop(bbox)
        
    w, h = cutout.size
    max_side = max(w, h)
    scale = 92.0 / max_side
    new_w, new_h = int(w * scale), int(h * scale)
    scaled_obj = cutout.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    goal_icon = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    paste_x = (100 - new_w) // 2
    paste_y = (100 - new_h) // 2
    goal_icon.paste(scaled_obj, (paste_x, paste_y), scaled_obj)
    
    out_file = os.path.join(output_dir, f"{icon_name}.png")
    goal_icon.save(out_file)
    print(f"[Done] HOI4 Goal Icon saved: {out_file} (size: {goal_icon.size})")
    return out_file

def generate_one(prompt_text, output_dir, icon_name, seed=None, keep_alive=False):
    try:
        ensure_comfyui_running()
        payload = build_workflow_payload(prompt_text, seed=seed)
        post_data = json.dumps({"prompt": payload}).encode('utf-8')
        req = urllib.request.Request(f"{COMFY_API_URL}/prompt", data=post_data, headers={'Content-Type': 'application/json'})
        
        print(f"[*] Submitting prompt for {icon_name}...")
        resp = urllib.request.urlopen(req)
        prompt_id = json.loads(resp.read().decode('utf-8'))['prompt_id']
        print(f"[*] Generation started with Prompt ID: {prompt_id}")
        
        start_t = time.time()
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
                        raise RuntimeError("No output image returned from node 9")
                    filename = images[0]['filename']
                    subfolder = images[0].get('subfolder', '')
                    
                    comfy_out_dir = r"C:\Program Files\Comfyui-WF-2026.8.8\Comfyui-WF-2026.8.8\ComfyUI\output"
                    raw_path = os.path.join(comfy_out_dir, subfolder, filename)
                    print(f"[*] ComfyUI rendered in {elapsed}s: {raw_path}")
                    return process_goal_icon(raw_path, output_dir, icon_name)
                else:
                    if elapsed % 10 == 0:
                        print(f"[*] Waiting for ComfyUI... ({elapsed}s)")
            except Exception as e:
                if "No output image" in str(e):
                    raise e
                pass
                
            if elapsed > 300:
                raise TimeoutError(f"Generation timed out for {icon_name} (300s)")
    finally:
        if not keep_alive:
            kill_comfyui()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HOI4 Focus Icon Generator with Unified EBS Style Lock support")
    parser.add_argument("--focus-id", type=str, default="", help="Focus ID to auto-load standardized locked prompt")
    parser.add_argument("--prompt", type=str, default="", help="Custom prompt (overrides auto prompt)")
    parser.add_argument("--name", type=str, default="", help="Output icon sprite name (e.g. GFX_focus_EBS_xyz)")
    parser.add_argument("--outdir", type=str, default="gfx/interface/goals/EBS")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--keep-alive", action="store_true")
    parser.add_argument("--kill", action="store_true", help="Immediately kill ComfyUI to free VRAM")
    args = parser.parse_args()
    
    if args.kill:
        kill_comfyui()
        sys.exit(0)

    prompt = args.prompt
    icon_name = args.name

    if args.focus_id:
        if os.path.exists(PROMPT_BOOK_PATH):
            with open(PROMPT_BOOK_PATH, "r", encoding="utf-8") as f:
                prompts_data = json.load(f)
            found = next((item for item in prompts_data if item["id"] == args.focus_id), None)
            if found:
                if not prompt:
                    prompt = found["locked_prompt"]
                if not icon_name:
                    icon_name = f"GFX_focus_{args.focus_id}"
                print(f"[OK] Loaded standardized locked prompt for {args.focus_id} ({found['name']})")
            else:
                print(f"[!] Warning: focus-id '{args.focus_id}' not found in unified prompt book.")
        else:
            print(f"[!] Warning: {PROMPT_BOOK_PATH} not found.")

    if not prompt or not icon_name:
        parser.error("Either --focus-id (found in prompt book) or both --prompt and --name must be provided.")

    generate_one(prompt, args.outdir, icon_name, seed=args.seed, keep_alive=args.keep_alive)
