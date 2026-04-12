"""
Migrate trainer sprites from v17 (Pokemon-Sunday-Dev) to v21.1 (Pokemon-Sunday-3).

v17: Graphics/Characters/trainer###.png  (### = numeric ID from PBS/trainertypes.txt)
v21: Graphics/Trainers/INTERNALNAME.png  (internal name = bracket key in PBS/trainer_types.txt)

This script reads the OLD trainertypes.txt to build id->name mapping, then copies
each sprite to the new location with the correct name.
"""

import os
import shutil
import re

OLD_ROOT = os.path.join(os.path.dirname(__file__))
NEW_ROOT = os.path.join(os.path.dirname(__file__), "..", "Pokemon-Sunday-3")

OLD_SPRITES = os.path.join(OLD_ROOT, "Graphics", "Characters")
NEW_SPRITES = os.path.join(NEW_ROOT, "Graphics", "Trainers")
OLD_PBS     = os.path.join(OLD_ROOT, "PBS", "trainertypes.txt")

def parse_old_trainertypes(path):
    """Parse v17 trainertypes.txt (CSV: id,internal_name,...) -> dict {id: internal_name}"""
    mapping = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) < 2:
                continue
            try:
                trainer_id = int(parts[0])
                internal_name = parts[1].strip()
                mapping[trainer_id] = internal_name
            except ValueError:
                continue
    return mapping

def main():
    id_to_name = parse_old_trainertypes(OLD_PBS)
    print(f"Parsed {len(id_to_name)} trainer type entries from old PBS.")

    # Get all trainer sprite files from the old project
    old_files = [f for f in os.listdir(OLD_SPRITES) if re.match(r'^trainer\d+', f, re.IGNORECASE) and f.endswith(".png")]
    old_files.sort()

    copied = []
    skipped_exists = []
    unmapped = []

    for fname in old_files:
        src = os.path.join(OLD_SPRITES, fname)

        # Extract numeric ID from filename (e.g. trainer060.png -> 60)
        m = re.match(r'^trainer(\d+)\.png$', fname, re.IGNORECASE)
        if not m:
            # Handle "trainer909 (2).png" style
            m2 = re.match(r'^trainer(\d+)\s*\((\d+)\)\.png$', fname, re.IGNORECASE)
            if m2:
                trainer_id = int(m2.group(1))
                variant = m2.group(2)
                internal_name = id_to_name.get(trainer_id)
                if internal_name:
                    dest_name = f"{internal_name}_{variant}.png"
                else:
                    dest_name = fname  # keep original name if no mapping
                    unmapped.append(fname)
                dest = os.path.join(NEW_SPRITES, dest_name)
                shutil.copy2(src, dest)
                copied.append(f"{fname} -> {dest_name}")
            else:
                unmapped.append(fname)
            continue

        trainer_id = int(m.group(1))
        internal_name = id_to_name.get(trainer_id)

        if internal_name:
            dest_name = f"{internal_name}.png"
        else:
            # No PBS entry — keep numbered name so it's still in the folder
            dest_name = fname
            unmapped.append(fname)

        dest = os.path.join(NEW_SPRITES, dest_name)
        shutil.copy2(src, dest)
        copied.append(f"{fname} -> {dest_name}")

    print(f"\n=== Results ===")
    print(f"Copied/renamed: {len(copied)}")
    for entry in copied:
        print(f"  {entry}")

    if unmapped:
        print(f"\nUnmapped (no PBS entry, kept numbered name): {len(unmapped)}")
        for u in unmapped:
            print(f"  {u}")

    print("\nDone.")

if __name__ == "__main__":
    main()
