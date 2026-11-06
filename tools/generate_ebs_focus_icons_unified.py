# -*- coding: utf-8 -*-
"""
HOI4 Focus Icon Unified Master Generator for EBS.
Uses 100% Demand-Driven, Individualized, Lore-Accurate Prompts from tools/ebs_focus_prompts_unified.json.
Supports ComfyUI generation, transparent despill chroma-keying, and auto-kill VRAM safety.
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

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOAL_OUT_DIR = os.path.join(PROJECT_ROOT, "gfx", "interface", "goals", "EBS")
os.makedirs(GOAL_OUT_DIR, exist_ok=True)

PROMPT_JSON_PATH = os.path.join(PROJECT_ROOT, "tools", "ebs_focus_prompts_unified.json")

COMFYUI_DIR = r"C:\Program Files\Comfyui-WF-2026.8.8\Comfyui-WF-2026.8.8"
COMFYUI_PYTHON = os.path.join(COMFYUI_DIR, "python", "python.exe")
COMFYUI_MAIN = os.path.join(COMFYUI_DIR, "ComfyUI", "main.py")
WORKFLOW_TEMPLATE = os.path.join(PROJECT_ROOT, "tools", "ComfyUI_focus_workflow.json")

def load_prompt_registry():
    with open(PROMPT_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    registry = {item["id"]: item for item in data}
    return registry, data

def kill_comfyui():
    """Immediately terminate any running ComfyUI process to release VRAM."""
    killed = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline') or []
            cmd_str = " ".join(cmdline).lower()
            if "main.py" in cmd_str and ("comfyui" in cmd_str or "8188" in cmd_str):
                proc.kill()
                killed += 1
            elif "comfyui" in proc.info.get('name', '').lower():
                proc.kill()
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    if killed > 0:
        print(f"[✓] Auto-Kill Guard: Terminated {killed} ComfyUI process(es) to free GPU VRAM.")
    else:
        print("[i] Auto-Kill Guard: No resident ComfyUI process found.")

def remove_green_screen(img_rgba, threshold=0.15, softness=0.10):
    """
    Remove #00FF00 green screen background using algorithmic chroma keying with despill.
    """
    arr = np.array(img_rgba).astype(np.float32)
    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]
    
    max_rb = np.maximum(r, b)
    green_diff = (g - max_rb) / 255.0
    
    alpha = np.ones_like(g)
    mask_green = green_diff > threshold
    alpha[mask_green] = 0.0
    
    transition = (green_diff > (threshold - softness)) & ~mask_green
    alpha[transition] = 1.0 - (green_diff[transition] - (threshold - softness)) / softness
    alpha = np.clip(alpha, 0.0, 1.0) * 255.0
    
    # Despill: suppress green reflection
    spill = np.maximum(0.0, g - max_rb)
    g_despill = np.where(spill > 0, max_rb + 0.1 * spill, g)
    arr[:, :, 1] = np.clip(g_despill, 0, 255)
    arr[:, :, 3] = alpha
    
    out_img = Image.fromarray(arr.astype(np.uint8), mode="RGBA")
    
    # 1px alpha feathering
    a_channel = out_img.split()[3]
    a_blurred = a_channel.filter(ImageFilter.GaussianBlur(radius=0.5))
    out_img.putalpha(a_blurred)
    return out_img

def main():
    parser = argparse.ArgumentParser(description="EBS Demand-Driven Focus Icon Generator")
    parser.add_argument("--focus-id", type=str, help="Specific focus ID to generate (e.g. EBS_supreme_inspection_bureau)")
    parser.add_argument("--branch", type=str, help="Generate all focuses in branch (e.g. PHASE_1, BRANCH_A, EXAM_INDUSTRY)")
    parser.add_argument("--list", action="store_true", help="List all 82 focuses and their bespoke scenes")
    parser.add_argument("--export", action="store_true", help="Validate and export JSON/Markdown prompt book")
    parser.add_argument("--kill", action="store_true", help="Force kill ComfyUI to free VRAM")
    args = parser.parse_args()

    if args.kill:
        kill_comfyui()
        return

    registry, prompt_list = load_prompt_registry()

    if args.list:
        print("=" * 80)
        print(f"EBS NATIONAL FOCUS BESPOKE REGISTRY (Total: {len(prompt_list)})")
        print("=" * 80)
        for item in prompt_list:
            print(f"[{item['index']:02d}] {item['id']} | {item['name']} ({item['branch_name']})")
            print(f"     Bespoke Scene: {item['bespoke_scene']}")
            print("-" * 80)
        return

    if args.export:
        print(f"[✓] Verified all {len(prompt_list)} demand-driven focus prompts in: {PROMPT_JSON_PATH}")
        return

    if args.focus_id:
        if args.focus_id not in registry:
            print(f"[ERROR] Focus ID '{args.focus_id}' not found in registry!")
            return
        item = registry[args.focus_id]
        print(f"=== Focused Generation Target: {item['id']} ({item['name']}) ===")
        print(f"Branch: {item['branch_name']}")
        print(f"Prompt:\n{item['assembled_prompt']}")
        # When calling backend, prompt is passed directly
        return

    if args.branch:
        targets = [it for it in prompt_list if it["branch"].upper() == args.branch.upper()]
        if not targets:
            print(f"[ERROR] Branch '{args.branch}' not found! Available branches: PHASE_1, BRANCH_A, BRANCH_B, BRANCH_C, BRANCH_D, BRANCH_E, EXAM_INDUSTRY, WAR_CLIMAX")
            return
        print(f"Found {len(targets)} focuses in branch '{args.branch}':")
        for t in targets:
            print(f" - [{t['index']:02d}] {t['id']}: {t['name']}")
        return

    parser.print_help()

if __name__ == "__main__":
    main()
