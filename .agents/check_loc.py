import os
from pathlib import Path

file_path = Path("localisation/simp_chinese/YDS_focus_l_simp_chinese.yml")
with open(file_path, "r", encoding="utf-8-sig") as f:
    lines = f.readlines()

print("Total lines:", len(lines))
print("Header line:", repr(lines[0]))

issues = []
for idx, line in enumerate(lines, 1):
    raw = line.rstrip("\r\n")
    if idx == 1:
        if raw != "l_simp_chinese:":
            issues.append(f"Line 1 should be 'l_simp_chinese:', found: {repr(raw)}")
        continue
    if not raw or raw.strip().startswith("#"):
        continue
    if not line.startswith(" "):
        issues.append(f"Line {idx} does not start with space: {repr(raw)}")
    if ":" not in raw:
        issues.append(f"Line {idx} has no colon: {repr(raw)}")
    else:
        k, v = raw.split(":", 1)
        v_str = v.strip()
        if not v_str.endswith('"'):
            issues.append(f"Line {idx} does not end with quote: {repr(raw)}")
        if not (v_str.startswith('"') or (v_str.startswith('0 "') and v_str.endswith('"')) or (v_str.startswith('1 "') and v_str.endswith('"'))):
            issues.append(f"Line {idx} unexpected value start: {repr(raw)}")

print("Issues found:", len(issues))
for iss in issues[:20]:
    print(" ", iss)
