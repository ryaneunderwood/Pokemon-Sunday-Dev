"""
Migrate item icons from v17 (Pokemon-Sunday-Dev) to v21.1 (Pokemon-Sunday-3).

v17: Graphics/Icons/item###.png  (### = numeric ID from PBS/items.txt)
v21: Graphics/Items/INTERNALNAME.png

Does NOT overwrite files that already exist in the new project.
"""

import os
import shutil
import re

OLD_ROOT = os.path.dirname(__file__)
NEW_ROOT = os.path.join(OLD_ROOT, "..", "Pokemon-Sunday-3")

OLD_SPRITES = os.path.join(OLD_ROOT, "Graphics", "Icons")
NEW_SPRITES = os.path.join(NEW_ROOT, "Graphics", "Items")
OLD_PBS     = os.path.join(OLD_ROOT, "PBS", "items.txt")


def parse_old_items(path):
    """Parse v17 items.txt (CSV: id,internal_name,...) -> dict {id: internal_name}"""
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
                item_id = int(parts[0])
                internal_name = parts[1].strip()
                mapping[item_id] = internal_name
            except ValueError:
                continue
    return mapping


def main():
    id_to_name = parse_old_items(OLD_PBS)
    print(f"Parsed {len(id_to_name)} item entries from old PBS.")

    existing_new = {f.lower() for f in os.listdir(NEW_SPRITES)}

    old_files = [f for f in os.listdir(OLD_SPRITES)
                 if re.match(r'^item\d+\.png$', f, re.IGNORECASE)]
    old_files.sort(key=lambda f: int(re.search(r'\d+', f).group()))

    copied = []
    skipped_exists = []
    unmapped = []

    for fname in old_files:
        m = re.match(r'^item(\d+)\.png$', fname, re.IGNORECASE)
        item_id = int(m.group(1))
        internal_name = id_to_name.get(item_id)

        if not internal_name:
            unmapped.append(fname)
            continue

        dest_name = f"{internal_name}.png"
        if dest_name.lower() in existing_new:
            skipped_exists.append(f"{fname} -> {dest_name} (already exists)")
            continue

        src = os.path.join(OLD_SPRITES, fname)
        dest = os.path.join(NEW_SPRITES, dest_name)
        shutil.copy2(src, dest)
        copied.append(f"{fname} -> {dest_name}")

    print(f"\nCopied:          {len(copied)}")
    print(f"Skipped/exists:  {len(skipped_exists)}")
    print(f"Unmapped:        {len(unmapped)}")

    if copied:
        print("\nCopied:")
        for e in copied:
            print(f"  {e}")

    if skipped_exists:
        print("\nSkipped (already exist in new project):")
        for e in skipped_exists:
            print(f"  {e}")

    if unmapped:
        print("\nUnmapped (no PBS entry):")
        for e in unmapped:
            print(f"  {e}")

    print("\nDone.")


if __name__ == "__main__":
    main()
