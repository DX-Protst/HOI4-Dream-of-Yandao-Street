"""
HOI4 Leader Portrait Generator via ComfyUI & Chroma-Key Despill
工作流: 钢铁雄心.json
支持: 1:1 绿幕生图 -> 自动化色键抠图与边缘去绿 (Despill) -> 输出标准 HOI4 领袖/顾问尺寸 (156x210 / 78x105)
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
DEFAULT_WORKFLOW_PATH = r"C:\Program Files\Comfyui-WF-2026.8.8\Comfyui-WF-2026.8.8\ComfyUI\user\default\workflows\钢铁雄心.json"

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
                "text": "worst quality, bad anatomy, watermark, jpeg artifact, blurry, shadows on green screen, non-green background elements"
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
                "filename_prefix": "hoi4_leader_raw"
            }
        }
    }

def remove_greenscreen_and_save(raw_img_path, output_dir, prefix):
    os.makedirs(output_dir, exist_ok=True)
    img = Image.open(raw_img_path).convert('RGB')
    rgb = np.array(img, dtype=np.float32)
    
    r = rgb[:, :, 0]
    g = rgb[:, :, 1]
    b = rgb[:, :, 2]
    
    # 色差键控：利用绿色与红色/蓝色最大值的差异
    max_rb = np.maximum(r, b)
    green_diff = g - max_rb
    
    lower_th = 15.0
    upper_th = 60.0
    alpha = np.clip(1.0 - (green_diff - lower_th) / (upper_th - lower_th), 0.0, 1.0)
    
    # 保护暗色衣物与非荧光绿
    is_bright_green = (g > 100) & (g > r * 1.2) & (g > b * 1.2)
    alpha = np.where(is_bright_green, alpha, 1.0)
    
    # Despill: 去除边缘绿光溢出 (反光抑制)
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
    
    # 1. 原始绿幕备份与 1024 完整抠图
    raw_save = os.path.join(output_dir, f"{prefix}_raw_1024.png")
    img.save(raw_save)
    
    cutout_1024 = os.path.join(output_dir, f"{prefix}_transparent_1024.png")
    cutout.save(cutout_1024)
    
    # 2. 居中裁切至 HOI4 领袖尺寸 (156 x 210)
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
        
        # 3. HOI4 顾问小图标 (78 x 105)
        small_portrait = large_portrait.resize((78, 105), Image.Resampling.LANCZOS)
        small_path = os.path.join(output_dir, f"{prefix}_small_78x105.png")
        small_portrait.save(small_path)
        
        print(f"[Done] HOI4 Large Portrait: {large_path}")
        print(f"[Done] HOI4 Small Advisor:  {small_path}")
        print(f"[Done] Raw 1024 Preview:    {raw_save}")
        print(f"[Done] Transparent 1024:    {cutout_1024}")
        return large_path
    return cutout_1024

def generate(prompt_text, output_dir, prefix="portrait_leader", seed=None):
    payload = build_workflow_payload(prompt_text, seed=seed)
    post_data = json.dumps({"prompt": payload}).encode('utf-8')
    req = urllib.request.Request(f"{COMFY_API_URL}/prompt", data=post_data, headers={'Content-Type': 'application/json'})
    
    print(f"[*] Submitting prompt to ComfyUI ({COMFY_API_URL})...")
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
                
                # ComfyUI output directory
                comfy_out_dir = r"C:\Program Files\Comfyui-WF-2026.8.8\Comfyui-WF-2026.8.8\ComfyUI\output"
                raw_path = os.path.join(comfy_out_dir, subfolder, filename)
                print(f"[*] ComfyUI rendered in {elapsed}s: {raw_path}")
                
                # Execute chroma-keying
                print("[*] Processing chroma key and despill removal...")
                return remove_greenscreen_and_save(raw_path, output_dir, prefix)
            else:
                print(f"[*] Waiting for ComfyUI... ({elapsed}s)")
        except Exception as e:
            if "No output image" in str(e):
                raise e
            print(f"[!] Polling: {e}")
            
        if elapsed > 300:
            raise TimeoutError("ComfyUI generation timed out (300s)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HOI4 Portrait Generator via ComfyUI & Chroma Key")
    parser.add_argument("--prompt", type=str, default="纯净平整单色绿幕背景（chroma key #00FF00 green screen background），一位严谨沉稳的钢铁雄心风格学院领袖半身肖像，身着整洁的深色民国中山装与教务风衣，胸前佩戴校徽，正面特写，面部轮廓分明，神色果断，干净边缘，棚拍均匀平光照明，背景绝对纯绿色，便于自动抠图", help="Prompt for ComfyUI")
    parser.add_argument("--name", type=str, default="portrait_custom_leader", help="Output file prefix")
    parser.add_argument("--outdir", type=str, default=r"c:\Users\10431\Desktop\HOI4\gfx\leaders\custom", help="Output directory")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    args = parser.parse_args()

    generate(args.prompt, args.outdir, args.name, args.seed)
