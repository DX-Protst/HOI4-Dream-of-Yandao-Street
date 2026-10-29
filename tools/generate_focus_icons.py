"""
HOI4 Focus Icon Generator via ComfyUI & Chroma-Key Despill
Generates focus icons (100x100 max dimension, RGBA transparent PNG) on green screen #00FF00
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
import numpy as np
from PIL import Image, ImageFilter

COMFY_API_URL = "http://127.0.0.1:8188"

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
                "megapixels": 1.0,
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
                "filename_prefix": "hoi4_goal_raw"
            }
        }
    }

def process_goal_icon(raw_img_path, output_dir, icon_name):
    os.makedirs(output_dir, exist_ok=True)
    img = Image.open(raw_img_path).convert('RGB')
    rgb = np.array(img, dtype=np.float32)
    
    r = rgb[:, :, 0]
    g = rgb[:, :, 1]
    b = rgb[:, :, 2]
    
    # Delta Keying
    max_rb = np.maximum(r, b)
    green_diff = g - max_rb
    
    lower_th = 15.0
    upper_th = 60.0
    alpha = np.clip(1.0 - (green_diff - lower_th) / (upper_th - lower_th), 0.0, 1.0)
    
    # Protect dark colors & non-bright greens
    is_bright_green = (g > 100) & (g > r * 1.15) & (g > b * 1.15)
    alpha = np.where(is_bright_green, alpha, 1.0)
    
    # Despill: neutralize green spill
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
    
    # Crop to bounding box of non-transparent pixels
    bbox = cutout.getbbox()
    if bbox:
        cropped = cutout.crop(bbox)
        bw = cropped.width
        bh = cropped.height
        
        # Scale proportionally to fit within 100x100 (standard HOI4 goal icon dimension)
        scale = min(100.0 / bw, 100.0 / bh)
        new_w = max(1, int(round(bw * scale)))
        new_h = max(1, int(round(bh * scale)))
        
        goal_icon = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
    else:
        goal_icon = cutout.resize((100, 100), Image.Resampling.LANCZOS)
        
    out_file = os.path.join(output_dir, f"{icon_name}.png")
    goal_icon.save(out_file)
    print(f"[Done] HOI4 Goal Icon saved: {out_file} (size: {goal_icon.size})")
    return out_file

def generate_one(prompt_text, output_dir, icon_name, seed=None):
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
            # transient network errors
            pass
            
        if elapsed > 300:
            raise TimeoutError(f"Generation timed out for {icon_name} (300s)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, required=True)
    parser.add_argument("--name", type=str, required=True)
    parser.add_argument("--outdir", type=str, default="gfx/interface/goals")
    args = parser.parse_args()
    
    generate_one(args.prompt, args.outdir, args.name)
