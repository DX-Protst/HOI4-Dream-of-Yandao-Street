# -*- coding: utf-8 -*-
"""
EBS Complete Localization Builder
Combines all localization modules into localisation/simp_chinese/EBS_l_simp_chinese.yml.
Ensures single UTF-8 BOM, strict YAML format, single-line strings with \\n escapes,
and complete integrity of all keys.
"""

import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import data modules
from ebs_loc_data_base import DATA_BASE
from ebs_loc_data_focuses import DATA_FOCUSES
from ebs_loc_data_events_classic import DATA_CLASSIC_EVENTS
from ebs_loc_data_crises import DATA_CRISES
from ebs_loc_data_fe_part1 import DATA_FE_PART1
from ebs_loc_data_fe_part2 import DATA_FE_PART2

def format_val(val: str) -> str:
    # Ensure no raw linebreaks inside the string, replace with \n
    val = val.strip().replace('\r\n', '\n').replace('\r', '\n')
    # If there are empty lines, preserve as double newline in game \n\n
    paragraphs = val.split('\n\n')
    cleaned_paras = []
    for p in paragraphs:
        lines = [l.strip() for l in p.split('\n') if l.strip()]
        cleaned_paras.append(r'\n'.join(lines))
    escaped = r'\n\n'.join(cleaned_paras)
    # Replace internal straight double quotes with Chinese quotes to avoid YAML break
    escaped = escaped.replace('"', '“')
    return escaped

def main():
    target_path = Path("localisation/simp_chinese/EBS_l_simp_chinese.yml")
    
    sections = [
        ("EBS IDEOLOGY PARTIES", DATA_BASE),
        ("EBS NATIONAL FOCUSES & DECISIONS", DATA_FOCUSES),
        ("EBS CLASSIC NARRATIVE EVENTS", DATA_CLASSIC_EVENTS),
        ("EBS INTERWOVEN CRISES & ENDINGS", DATA_CRISES),
        ("EBS FOCUS COMPLETION NARRATIVE EVENTS (1-34)", DATA_FE_PART1),
        ("EBS FOCUS COMPLETION NARRATIVE EVENTS (35-60)", DATA_FE_PART2),
    ]

    lines = ["l_simp_chinese:"]
    total_keys = 0

    for sec_title, sec_dict in sections:
        lines.append(f"  # ========================================================")
        lines.append(f"  # {sec_title}")
        lines.append(f"  # ========================================================")
        for k, v in sec_dict.items():
            clean = format_val(v)
            lines.append(f'  {k}:0 "{clean}"')
            total_keys += 1

    content = "\n".join(lines) + "\n"

    # Write with explicit UTF-8 BOM
    with open(target_path, "wb") as f:
        f.write(b"\xef\xbb\xbf")
        f.write(content.encode("utf-8"))

    print(f"[SUCCESS] Generated {total_keys} keys in {target_path}")
    print(f"Total lines: {len(lines)}, total chars: {len(content)}")

if __name__ == "__main__":
    main()
