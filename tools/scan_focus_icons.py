import glob
import re
import os

with open('interface/YDS_goals.gfx', 'r', encoding='utf-8', errors='ignore') as f:
    gfx_content = f.read()

defined_sprites = set(re.findall(r'name\s*=\s*"?([a-zA-Z0-9_]+)"?', gfx_content))
existing_files = set([os.path.splitext(f)[0] for f in os.listdir('gfx/interface/goals')])

print(f'Defined sprites in YDS_goals.gfx: {len(defined_sprites)}')
print(f'PNG files in gfx/interface/goals: {len(existing_files)}')

focus_files = glob.glob('common/national_focus/*.txt')
vanilla_or_missing = []

# also parse focus blocks accurately with bracket counting
def parse_focus_blocks(text):
    focuses = []
    idx = 0
    while True:
        pos = text.find('focus = {', idx)
        if pos == -1:
            pos = text.find('focus={', idx)
            if pos == -1:
                break
        open_b = text.find('{', pos)
        depth = 1
        curr = open_b + 1
        while curr < len(text) and depth > 0:
            if text[curr] == '{':
                depth += 1
            elif text[curr] == '}':
                depth -= 1
            curr += 1
        block = text[open_b+1:curr-1]
        id_m = re.search(r'\bid\s*=\s*([a-zA-Z0-9_]+)', block)
        icon_m = re.search(r'\bicon\s*=\s*([a-zA-Z0-9_]+)', block)
        if id_m:
            focuses.append((id_m.group(1), icon_m.group(1) if icon_m else None))
        idx = curr
    return focuses

for ff in focus_files:
    with open(ff, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    f_list = parse_focus_blocks(content)
    for fid, icon in f_list:
        is_custom_gfx = icon in defined_sprites
        is_custom_file = icon in existing_files
        is_generic = icon.startswith('GFX_goal_generic_') or icon.startswith('GFX_focus_generic_') or icon.startswith('goal_generic_')
        if is_generic or not is_custom_gfx or not is_custom_file:
            vanilla_or_missing.append((os.path.basename(ff), fid, icon, is_custom_gfx, is_custom_file))

print(f'Found {len(vanilla_or_missing)} focuses using vanilla or missing icons:')
for item in vanilla_or_missing:
    print(item)

print("\n--- FOCUS DETAILS ---")
focus_ids = [item[1] for item in vanilla_or_missing]
with open('localisation/simp_chinese/YDS_focus_l_simp_chinese.yml', 'r', encoding='utf-8-sig', errors='ignore') as f:
    loc_lines = f.readlines()

for fid in focus_ids:
    title = ''
    desc = ''
    for line in loc_lines:
        sline = line.strip()
        if sline.startswith(f'{fid}:'):
            title = sline.split(':', 1)[1].strip().strip('"0123456789 ')
        elif sline.startswith(f'{fid}_desc:'):
            desc = sline.split(':', 1)[1].strip().strip('"0123456789 ')
    print(f'{fid}: Title="{title}" | Desc="{desc}"')
