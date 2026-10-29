"""
Updates interface/YDS_goals.gfx and common/national_focus/YDS_focus.txt
with the 14 newly generated focus icons.
"""

import re

REPLACEMENTS = [
    ("YDS_campus_asset_inventory", "GFX_goal_generic_construct_civ_factory", "GFX_focus_YDS_campus_asset_inventory"),
    ("YDS_school_canteen_monopoly", "GFX_goal_generic_consumer_goods", "GFX_focus_YDS_school_canteen_monopoly"),
    ("YDS_overhead_corridor_network", "GFX_goal_generic_construct_infrastructure", "GFX_focus_YDS_overhead_corridor_network"),
    ("YDS_sports_room_requisition", "GFX_goal_generic_allies_build_infantry", "GFX_focus_YDS_sports_room_requisition"),
    ("YDS_craft_class_armory", "GFX_goal_generic_construct_mil_factory", "GFX_focus_YDS_craft_class_armory"),
    ("YDS_print_shop_overdrive", "GFX_goal_generic_scientific_exchange", "GFX_focus_YDS_print_shop_overdrive"),
    ("YDS_chemistry_lab_reagents", "GFX_goal_generic_oil_refinery", "GFX_focus_YDS_chemistry_lab_reagents"),
    ("YDS_handicraft_standardization", "GFX_goal_generic_production", "GFX_focus_YDS_handicraft_standardization"),
    ("YDS_campus_logistics_gigafactory", "GFX_goal_generic_construct_civ_factory", "GFX_focus_YDS_campus_logistics_gigafactory"),
    ("YDS_gaokao_war_mobilization", "GFX_goal_generic_major_war", "GFX_focus_YDS_gaokao_war_mobilization"),
    ("YDS_exam_hall_tactics", "GFX_goal_generic_position_armies", "GFX_focus_YDS_exam_hall_tactics"),
    ("YDS_break_repeater_siege", "GFX_goal_generic_occupy_start_war", "GFX_focus_YDS_break_repeater_siege"),
    ("YDS_all_front_counterattack", "GFX_goal_generic_scientific_exchange", "GFX_focus_YDS_all_front_counterattack"),
    ("YDS_all_china_educational_hegemony", "GFX_goal_generic_forceful_treaty", "GFX_focus_YDS_all_china_educational_hegemony"),
]

def update_goals_gfx():
    with open('interface/YDS_goals.gfx', 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = []
    for fid, old_icon, new_icon in REPLACEMENTS:
        # Check if already defined
        if f'name = "{new_icon}"' in content:
            print(f"Sprite {new_icon} already in YDS_goals.gfx, skipping.")
            continue
        block = f"""\tSpriteType = {{
\t\tname = "{new_icon}"
\t\ttexturefile = "gfx/interface/goals/{new_icon}.png"
\t}}
\tSpriteType = {{
\t\tname = "{new_icon}_shine"
\t\ttexturefile = "gfx/interface/goals/{new_icon}.png"
\t\teffectFile = "gfx/FX/buttonstate.lua"
\t\tanimation = {{
\t\t\tanimationmaskfile = "gfx/interface/goals/{new_icon}.png"
\t\t\tanimationtexturefile = "gfx/interface/goals/shine_overlay.dds"
\t\t\tanimationrotation = -90.0
\t\t\tanimationlooping = no
\t\t\tanimationtime = 0.75
\t\t\tanimationdelay = 0
\t\t\tanimationblendmode = "add"
\t\t\tanimationtype = "scrolling"
\t\t\tanimationrotationoffset = {{ x = 0.0 y = 0.0 }}
\t\t\tanimationtexturescale = {{ x = 1.0 y = 1.0 }}
\t\t}}
\t\tlegacy_lazy_load = no
\t}}"""
        blocks.append(block)

    if blocks:
        all_new = '\n\n' + '\n\n'.join(blocks) + '\n}\n'
        last_brace = content.rfind('}')
        if last_brace != -1:
            updated = content[:last_brace] + all_new
            with open('interface/YDS_goals.gfx', 'w', encoding='utf-8') as f:
                f.write(updated)
            print(f"Added {len(blocks)} sprite pairs to interface/YDS_goals.gfx")
        else:
            print("Error: Could not find last brace in interface/YDS_goals.gfx")

def update_focus_tree():
    with open('common/national_focus/YDS_focus.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    modified = content
    for fid, old_icon, new_icon in REPLACEMENTS:
        # Match from id = fid until icon = old_icon without crossing another focus = {
        pattern = re.compile(rf'(id\s*=\s*{fid}\b(?:(?!focus\s*=\s*\{{)[\s\S])*?icon\s*=\s*){old_icon}\b')
        m = pattern.search(modified)
        if m:
            modified = pattern.sub(rf'\g<1>{new_icon}', modified, count=1)
            print(f"Updated focus {fid} -> {new_icon}")
        else:
            print(f"Warning: Could not match focus {fid} with icon {old_icon}")

    with open('common/national_focus/YDS_focus.txt', 'w', encoding='utf-8') as f:
        f.write(modified)
    print("Updated common/national_focus/YDS_focus.txt")

if __name__ == '__main__':
    update_goals_gfx()
    update_focus_tree()
