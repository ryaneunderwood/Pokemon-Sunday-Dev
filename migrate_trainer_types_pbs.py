"""
Migrate trainer type entries from old v17 PBS/trainertypes.txt into new v21.1 PBS/trainer_types.txt.

Old format (CSV): id,internal_name,display_name,base_money,battle_bgm,victory_bgm,,gender,skill_level,
New format (sections):
  [INTERNAL_NAME]
  Name = Display Name
  Gender = Male/Female/Unknown
  BaseMoney = 60
  BattleBGM = TrackName
  SkillLevel = 32

Notes:
- "Mixed" gender maps to "Unknown" in v21.1
- CHANELLER (old typo) is skipped — new PBS already has correct spelling CHANNELER
- ID 60 (LEADER_Pasiphae in old) is skipped — treated as LEADER_Misty (already in new PBS)
- BGM file names are stripped of .mp3 extension
"""

import os
import re

OLD_ROOT = os.path.dirname(__file__)
NEW_ROOT = os.path.join(OLD_ROOT, "..", "Pokemon-Sunday-3")

OLD_PBS = os.path.join(OLD_ROOT, "PBS", "trainertypes.txt")
NEW_PBS = os.path.join(NEW_ROOT, "PBS", "trainer_types.txt")

GENDER_MAP = {
    "Male": "Male",
    "Female": "Female",
    "Mixed": "Unknown",
}

# These IDs are intentionally skipped
SKIP_IDS = {
    60,  # Was LEADER_Pasiphae but is now LEADER_Misty — already in new PBS
}

# These internal names are intentionally skipped (typo duplicates of existing entries)
SKIP_NAMES = {
    "CHANELLER",  # Typo; new PBS already has CHANNELER
}


def parse_old_trainertypes(path):
    entries = []
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
            except ValueError:
                continue

            def get(i):
                return parts[i].strip() if i < len(parts) else ""

            entry = {
                "id":          trainer_id,
                "name":        get(1),
                "display":     get(2),
                "money":       get(3),
                "battle_bgm":  get(4),
                "victory_bgm": get(5),
                "gender":      get(7),
                "skill_level": get(8),
            }
            entries.append(entry)
    return entries


def parse_existing_names(path):
    names = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            m = re.match(r'^\[(\w+)\]', line.strip())
            if m:
                names.add(m.group(1))
    return names


def format_entry(entry):
    lines = []
    lines.append("#-------------------------------")
    lines.append(f"[{entry['name']}]")
    lines.append(f"Name = {entry['display']}")

    gender = GENDER_MAP.get(entry["gender"], entry["gender"])
    if gender:
        lines.append(f"Gender = {gender}")

    if entry["money"] and int(entry["money"]) > 0:
        lines.append(f"BaseMoney = {entry['money']}")

    bgm = entry["battle_bgm"].replace(".mp3", "").strip()
    if bgm:
        lines.append(f"BattleBGM = {bgm}")

    skill = entry["skill_level"]
    if skill and int(skill) > 0:
        lines.append(f"SkillLevel = {skill}")

    return "\n".join(lines)


def main():
    old_entries = parse_old_trainertypes(OLD_PBS)
    existing_names = parse_existing_names(NEW_PBS)

    new_sections = []
    skipped = []

    for entry in old_entries:
        if entry["id"] in SKIP_IDS:
            skipped.append(f"  ID {entry['id']} ({entry['name']}) — in SKIP_IDS")
            continue
        if entry["name"] in SKIP_NAMES:
            skipped.append(f"  {entry['name']} — in SKIP_NAMES (typo/duplicate)")
            continue
        if entry["name"] in existing_names:
            skipped.append(f"  {entry['name']} — already in new PBS")
            continue

        new_sections.append(format_entry(entry))
        existing_names.add(entry["name"])  # prevent duplicates within old PBS too

    if new_sections:
        with open(NEW_PBS, "a", encoding="utf-8") as f:
            f.write("\n")
            f.write("\n".join(new_sections))
            f.write("\n")

    print(f"Added {len(new_sections)} new trainer type entries to new PBS.")
    print(f"\nSkipped {len(skipped)}:")
    for s in skipped:
        print(s)

    if new_sections:
        print("\nAdded entries:")
        for sec in new_sections:
            name_line = [l for l in sec.split("\n") if l.startswith("[")][0]
            print(f"  {name_line}")


if __name__ == "__main__":
    main()
