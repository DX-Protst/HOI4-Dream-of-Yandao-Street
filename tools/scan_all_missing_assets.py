import os
import glob
import re

def parse_pdx_blocks(text):
    """Parses top-level blocks or key-value structures from Clausewitz text."""
    # Strip comments first
    lines = []
    for line in text.splitlines():
        line = line.split('#')[0]
        lines.append(line)
    clean_text = '\n'.join(lines)
    return clean_text

def get_loc_dict():
    locs = {}
    for f in glob.glob('localisation/simp_chinese/*.yml'):
        with open(f, 'r', encoding='utf-8-sig', errors='ignore') as fp:
            for line in fp:
                line = line.strip()
                if ':' in line:
                    parts = line.split(':', 1)
                    k = parts[0].strip()
                    v = parts[1].strip().strip('"0123456789 ')
                    locs[k] = v
    return locs

def scan_ideas():
    locs = get_loc_dict()
    # Read all gfx files to get sprite definitions
    gfx_sprites = {}
    for gfx_file in glob.glob('interface/*.gfx'):
        with open(gfx_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        # SpriteType = { name = "..." texturefile = "..." }
        matches = re.findall(r'name\s*=\s*["\']?([^"\'\s]+)["\']?\s+texturefile\s*=\s*["\']?([^"\'\s]+)["\']?', content, re.IGNORECASE)
        for name, tex in matches:
            gfx_sprites[name] = tex.replace('\\', '/')

    idea_files = glob.glob('common/ideas/*.txt')
    ideas = []

    for fpath in idea_files:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            text = parse_pdx_blocks(f.read())

        # parse ideas inside country = { ... } or hidden_ideas = { ... }
        # find matching braces
        i = 0
        while i < len(text):
            m = re.search(r'\b(country|hidden_ideas)\s*=\s*\{', text[i:])
            if not m:
                break
            start = i + m.end()
            depth = 1
            curr = start
            while curr < len(text) and depth > 0:
                if text[curr] == '{':
                    depth += 1
                elif text[curr] == '}':
                    depth -= 1
                curr += 1
            block = text[start:curr-1]
            i = curr

            # now inside country = { ... }, each block is an idea
            b_idx = 0
            while b_idx < len(block):
                m_sub = re.search(r'\b([a-zA-Z0-9_]+)\s*=\s*\{', block[b_idx:])
                if not m_sub:
                    break
                idea_name = m_sub.group(1)
                sub_start = b_idx + m_sub.end()
                depth_sub = 1
                curr_sub = sub_start
                while curr_sub < len(block) and depth_sub > 0:
                    if block[curr_sub] == '{':
                        depth_sub += 1
                    elif block[curr_sub] == '}':
                        depth_sub -= 1
                    curr_sub += 1
                idea_body = block[sub_start:curr_sub-1]
                b_idx = curr_sub

                # extract picture if any
                pic_m = re.search(r'\bpicture\s*=\s*([a-zA-Z0-9_]+)', idea_body)
                picture = pic_m.group(1) if pic_m else None
                ideas.append({
                    'file': os.path.basename(fpath),
                    'id': idea_name,
                    'picture': picture,
                    'name': locs.get(idea_name, idea_name),
                    'desc': locs.get(f'{idea_name}_desc', '')
                })

    print(f"Total parsed ideas: {len(ideas)}")
    missing_or_placeholder_ideas = []
    for idea in ideas:
        iid = idea['id']
        pic = idea['picture']
        # Default sprite if picture not specified: GFX_idea_<id>
        sprite_name = f"GFX_idea_{pic}" if pic else f"GFX_idea_{iid}"
        
        # Check if sprite is in gfx_sprites
        tex = gfx_sprites.get(sprite_name)
        file_exists = False
        if tex:
            file_exists = os.path.exists(tex)
            if file_exists and os.path.getsize(tex) == 0:
                file_exists = False
        
        is_generic = False
        if pic and ('generic' in pic or 'idea_unknown' in pic):
            is_generic = True
        if not tex or not file_exists or is_generic:
            missing_or_placeholder_ideas.append({
                **idea,
                'sprite_name': sprite_name,
                'tex': tex,
                'file_exists': file_exists,
                'is_generic': is_generic
            })

    return ideas, missing_or_placeholder_ideas, gfx_sprites

def scan_focuses(gfx_sprites):
    locs = get_loc_dict()
    focus_files = glob.glob('common/national_focus/*.txt')
    focuses = []

    for fpath in focus_files:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            text = parse_pdx_blocks(f.read())

        # parse focus = { ... }
        i = 0
        while i < len(text):
            m = re.search(r'\bfocus\s*=\s*\{', text[i:])
            if not m:
                break
            start = i + m.end()
            depth = 1
            curr = start
            while curr < len(text) and depth > 0:
                if text[curr] == '{':
                    depth += 1
                elif text[curr] == '}':
                    depth -= 1
                curr += 1
            block = text[start:curr-1]
            i = curr

            id_m = re.search(r'\bid\s*=\s*([a-zA-Z0-9_]+)', block)
            icon_m = re.search(r'\bicon\s*=\s*([a-zA-Z0-9_]+)', block)
            if id_m:
                fid = id_m.group(1)
                icon = icon_m.group(1) if icon_m else ''
                focuses.append({
                    'file': os.path.basename(fpath),
                    'id': fid,
                    'icon': icon,
                    'name': locs.get(fid, fid),
                    'desc': locs.get(f'{fid}_desc', '')
                })

    print(f"Total parsed focuses: {len(focuses)}")
    missing_or_generic_focuses = []
    for f in focuses:
        fid = f['id']
        icon = f['icon']
        is_generic = (
            'generic' in icon or 
            icon == '' or 
            icon.startswith('GFX_goal_continuous_')
        )
        tex = gfx_sprites.get(icon)
        file_exists = False
        if tex:
            file_exists = os.path.exists(tex)
            if file_exists and os.path.getsize(tex) == 0:
                file_exists = False
        
        if is_generic or not tex or not file_exists:
            missing_or_generic_focuses.append({
                **f,
                'tex': tex,
                'file_exists': file_exists,
                'is_generic': is_generic
            })

    return focuses, missing_or_generic_focuses

if __name__ == '__main__':
    all_ideas, missing_ideas, gfx_sprites = scan_ideas()
    all_focuses, missing_focuses = scan_focuses(gfx_sprites)

    print(f"\n================ MISSING / PLACEHOLDER IDEAS ({len(missing_ideas)}) ================")
    for item in missing_ideas:
        print(f"[{item['file']}] {item['id']} ('{item['name']}'): sprite={item['sprite_name']}, tex={item['tex']}, exists={item['file_exists']}, is_generic={item['is_generic']}")

    print(f"\n================ MISSING / GENERIC FOCUSES ({len(missing_focuses)}) ================")
    for item in missing_focuses:
        print(f"[{item['file']}] {item['id']} ('{item['name']}'): icon={item['icon']}, tex={item['tex']}, exists={item['file_exists']}, is_generic={item['is_generic']}")
