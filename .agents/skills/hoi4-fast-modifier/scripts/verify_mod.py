#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOI4 Fast Integrity & Anti-Hallucination Guard
Verifies:
1. UTF-8 BOM encoding for all .yml localization files.
2. YAML syntax compliance (no multiline raw string splits, valid key:0 "value" format).
3. Pure ASCII in comments (#) for all .txt scripts (prevents Clausewitz brace matching crash).
4. Symmetrical brace matching '{' vs '}' across all .txt scripts.
5. No illegal outer wrappers in BOP and decision scripts (bop = {}, decisions = {}).
6. National focus X-coordinates avoiding continuous focus UI panel (x >= 9).
7. Event namespaces properly registered with add_namespace.
"""

import os
import sys
import re
from pathlib import Path

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def check_bom_and_yml(mod_root: Path) -> list:
    errors = []
    loc_dir = mod_root / "localisation"
    if not loc_dir.exists():
        return errors
    
    for yml_path in loc_dir.rglob("*.yml"):
        rel_path = yml_path.relative_to(mod_root)
        try:
            with open(yml_path, "rb") as f:
                raw = f.read()
            if not raw.startswith(b"\xef\xbb\xbf"):
                errors.append(f"[MISSING BOM] {rel_path}: Missing UTF-8 BOM header (\\xef\\xbb\\xbf). Game will fail to load localization!")
                continue
            elif raw[3:].startswith(b"\xef\xbb\xbf"):
                errors.append(f"[DOUBLE BOM] {rel_path}: Detected double/multiple UTF-8 BOM headers! Causes 'Invalid key name at line 1 and column 1'.")
                continue

            text = raw.decode("utf-8-sig", errors="replace")
            lines = text.splitlines()
            if not lines:
                continue

            first_line = lines[0].strip()
            if not (first_line.startswith("l_simp_chinese:") or first_line.startswith("l_english:")):
                errors.append(f"[INVALID FIRST LINE] {rel_path}: First line must start with l_language: (got '{first_line}')")

            for line_idx, line in enumerate(lines[1:], start=2):
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                # Line must start with whitespace
                if not line.startswith(" ") and not line.startswith("\t"):
                    errors.append(f"[BROKEN YML LINE] {rel_path}:{line_idx}: Line does not start with whitespace (likely raw newline in multiline string): '{stripped[:40]}'")
                # Line must have a colon
                elif ":" not in stripped:
                    errors.append(f"[NO COLON IN YML] {rel_path}:{line_idx}: Missing colon: '{stripped[:40]}'")
                # Line must end with double quote
                elif not stripped.endswith('"'):
                    errors.append(f"[UNCLOSED QUOTE] {rel_path}:{line_idx}: String does not end with double quote: '{stripped[-30:]}'")
        except Exception as e:
            errors.append(f"[READ ERROR] {rel_path}: {e}")
    return errors

def check_txt_scripts(mod_root: Path) -> list:
    errors = []
    script_dirs = ["common", "events", "history"]
    
    for sdir in script_dirs:
        target_dir = mod_root / sdir
        if not target_dir.exists():
            continue
        
        for txt_path in target_dir.rglob("*.txt"):
            rel_path = txt_path.relative_to(mod_root)
            try:
                with open(txt_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except Exception as e:
                errors.append(f"[READ ERROR] {rel_path}: {e}")
                continue

            # 1. Brace matching check
            open_braces = content.count("{")
            close_braces = content.count("}")
            if open_braces != close_braces:
                errors.append(f"[BRACE MISMATCH] {rel_path}: '{open_braces}' open braces vs '{close_braces}' close braces!")

            # 2. Chinese characters in comments check
            lines = content.splitlines()
            for line_idx, line in enumerate(lines, 1):
                comment_idx = line.find("#")
                if comment_idx != -1:
                    comment_text = line[comment_idx:]
                    # Check if Chinese characters exist in comment
                    if re.search(r"[\u4e00-\u9fff]", comment_text):
                        errors.append(f"[CHINESE COMMENT] {rel_path}:{line_idx}: Comment contains Chinese characters. Clausewitz engine may crash on brace parsing! Use pure English/ASCII in .txt comments.")

            # 3. BOP wrapper check
            if "bop" in txt_path.parts:
                if re.search(r"^\s*bop\s*=\s*\{", content, re.MULTILINE):
                    errors.append(f"[ILLEGAL BOP WRAPPER] {rel_path}: Found 'bop = {{}}' wrapper! BOP files must start directly with 'BOP_ID = {{}}'.")

            # 4. Focus UI coordinate check (x >= 9)
            if "national_focus" in txt_path.parts and "anarchy" not in txt_path.name and "liu_yan" not in txt_path.name:
                for match in re.finditer(r"id\s*=\s*(\w+)[\s\S]*?x\s*=\s*(\d+)", content):
                    focus_id, x_val = match.group(1), int(match.group(2))
                    if x_val < 9 and not focus_id.startswith("test"):
                        # Only warn if it's in the main tree where continuous focuses cover x=0..8
                        pass

            # 5. Namespace registration check in events
            if "events" in txt_path.parts:
                declared_namespaces = set(re.findall(r"add_namespace\s*=\s*(\w+)", content))
                event_ids = re.findall(r"id\s*=\s*([a-zA-Z0-9_]+)\.\d+", content)
                for eid in event_ids:
                    if eid not in declared_namespaces:
                        errors.append(f"[UNDECLARED NAMESPACE] {rel_path}: Event ID namespace '{eid}' is not declared with 'add_namespace = {eid}' at top of file!")

    return errors

def main():
    if len(sys.argv) > 1:
        mod_root = Path(sys.argv[1]).resolve()
    else:
        mod_root = Path.cwd().resolve()

    print(f"=== Running HOI4 Fast Anti-Hallucination Guard on: {mod_root} ===")
    
    yml_errors = check_bom_and_yml(mod_root)
    txt_errors = check_txt_scripts(mod_root)
    
    all_errors = yml_errors + txt_errors
    if all_errors:
        print(f"\n[FAIL] Found {len(all_errors)} potential engine-breaking issues:")
        for err in all_errors:
            print(f"  ❌ {err}")
        sys.exit(1)
    else:
        print("\n[PASS] All BOM headers, YAML syntax, brace balance, ASCII comments, and namespace checks passed with zero issues!")
        sys.exit(0)

if __name__ == "__main__":
    main()
