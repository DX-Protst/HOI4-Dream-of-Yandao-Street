import os
import re

def main():
    icons = [f for f in os.listdir('gfx/interface/goals/EBS') if f.endswith('.png')]
    print(f"Total icon PNG files in gfx/interface/goals/EBS: {len(icons)}")

    with open('common/national_focus/EBS_focus.txt', 'r', encoding='utf-8') as f:
        text = f.read()

    fids = re.findall(r'id\s*=\s*(EBS_[a-zA-Z0-9_]+)', text)
    focus_ids = [fid for fid in fids if fid != 'EBS_focus_tree']
    print(f"Total focus IDs found in EBS_focus.txt: {len(focus_ids)}")

    missing_files = []
    for fid in focus_ids:
        expected_file = f"GFX_focus_{fid}.png"
        p = os.path.join('gfx/interface/goals/EBS', expected_file)
        if not os.path.exists(p):
            missing_files.append(expected_file)

    if missing_files:
        print(f"[FAIL] Missing files ({len(missing_files)}): {missing_files}")
    else:
        print(f"[OK] All {len(focus_ids)} focuses have their dedicated PNG icon on disk!")

    with open('interface/EBS_goals.gfx', 'r', encoding='utf-8') as f:
        gfx_text = f.read()

    sprites = re.findall(r'name\s*=\s*"([^"]+)"', gfx_text)
    base_sprites = [s for s in sprites if not s.endswith('_shine')]
    shine_sprites = [s for s in sprites if s.endswith('_shine')]
    print(f"Base sprites in EBS_goals.gfx: {len(base_sprites)}")
    print(f"Shine sprites in EBS_goals.gfx: {len(shine_sprites)}")

    # Verify that each focus in EBS_focus.txt has matching icon = GFX_focus_<id>
    mismatched = []
    for fid in focus_ids:
        expected_icon = f"GFX_focus_{fid}"
        # Search for block of this focus
        pat = rf'id\s*=\s*{fid}\b(?:(?!focus\s*=\s*\{{)[\s\S])*?icon\s*=\s*([a-zA-Z0-9_]+)'
        m = re.search(pat, text)
        if not m:
            mismatched.append((fid, "icon not found"))
        elif m.group(1) != expected_icon:
            mismatched.append((fid, m.group(1)))

    if mismatched:
        print(f"[FAIL] Mismatched icons in EBS_focus.txt: {mismatched[:5]}")
    else:
        print(f"[OK] All {len(focus_ids)} focus definitions in EBS_focus.txt match GFX_focus_<id> exactly!")

if __name__ == '__main__':
    main()
