import glob
from pathlib import Path
import re

total_issues = 0
for fpath in glob.glob("localisation/**/*.yml", recursive=True):
    with open(fpath, "r", encoding="utf-8-sig", errors="replace") as f:
        lines = f.readlines()
    
    file_issues = []
    if not lines:
        continue
    header = lines[0].rstrip("\r\n")
    if not (header.startswith("l_simp_chinese:") or header.startswith("l_english:")):
        file_issues.append(f"Bad header: {header}")
    
    for idx, line in enumerate(lines[1:], 2):
        raw = line.rstrip("\r\n")
        if not raw or raw.strip().startswith("#"):
            continue
        if not raw.startswith(" "):
            file_issues.append(f"Line {idx} doesn't start with space: {raw[:30]}")
        if ":" not in raw:
            file_issues.append(f"Line {idx} no colon: {raw[:30]}")
            continue
        k, v = raw.split(":", 1)
        v_str = v.strip()
        if v_str.startswith("0 ") or v_str.startswith("1 "):
            v_str = v_str[2:].strip()
        if v_str.startswith('"') and v_str.endswith('"'):
            inner = v_str[1:-1]
            unescaped = [m.start() for m in re.finditer(r'(?<!\\)"', inner)]
            if unescaped:
                file_issues.append(f"Line {idx} unescaped quote: {raw[:40]}")
        else:
            file_issues.append(f"Line {idx} missing quotes: {raw[:40]}")
    
    if file_issues:
        print(f"File {fpath}: {len(file_issues)} issues")
        for iss in file_issues[:5]:
            print(f"  {iss}")
        total_issues += len(file_issues)

print(f"Total issues across all yml: {total_issues}")
