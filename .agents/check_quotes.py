from pathlib import Path
import re

file_path = Path('localisation/simp_chinese/YDS_focus_l_simp_chinese.yml')
with open(file_path, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()

found = 0
for idx, line in enumerate(lines, 1):
    raw = line.rstrip('\r\n')
    if idx == 1 or not raw or raw.strip().startswith('#'):
        continue
    if ':' not in raw:
        print(f"No colon at line {idx}: {raw}")
        continue
    k, v = raw.split(':', 1)
    v_str = v.strip()
    if v_str.startswith('0 ') or v_str.startswith('1 '):
        v_str = v_str[2:].strip()
    if v_str.startswith('"') and v_str.endswith('"'):
        inner = v_str[1:-1]
        unescaped = [m.start() for m in re.finditer(r'(?<!\\)"', inner)]
        if unescaped:
            print(f"Line {idx} has unescaped quotes: {raw}")
            found += 1
    else:
        print(f"Malformed quote structure at line {idx}: {raw}")
        found += 1

print(f"Done, found {found} issues.")
