"""
Migrate custom items from v17 PBS/items.txt to v21.1 PBS/items.txt.

Skips any item whose internal name already exists in the new PBS.
Converts v17 CSV format to v21.1 key-value section format.
"""

import csv
import io
import re
import zlib
import os

OLD_PBS = r'C:/Users/rucra/Documents/GitHub/Pokemon-Sunday-Dev/PBS/items.txt'
NEW_PBS = r'C:/Users/rucra/Documents/GitHub/Pokemon-Sunday-3/PBS/items.txt'
SCRIPTS = r'C:/Users/rucra/Documents/GitHub/Pokemon-Sunday-Dev/Data/Scripts.rxdata'

# IDs to explicitly skip (duplicates/superseded)
SKIP_IDS = {719}  # GIMMIGHOULCOIN old entry — gen9 pack version used instead

# ── Pocket mapping ────────────────────────────────────────────────────────────
POCKET_MAP = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 1, 7: 7, 8: 8}

# ── FieldUse mapping ──────────────────────────────────────────────────────────
FIELD_USE = {'1': 'OnPokemon', '2': 'Direct', '3': 'TR', '4': 'HM', '5': 'OnPokemon'}

# ── Category → Flags ─────────────────────────────────────────────────────────
CATEGORY_FLAGS = {
    '2':  ['Mail'],
    '4':  ['PokeBall'],
    '7':  ['EvolutionStone'],
    '8':  ['Fossil'],
    '10': ['TypeGem'],
    '11': ['Mulch'],
    '12': ['MegaStone'],
}

# ── Extract flingarray from v17 scripts ───────────────────────────────────────
def build_fling_map(scripts_path):
    fling = {}
    with open(scripts_path, 'rb') as f:
        data = f.read()
    pos = 0
    while pos < len(data):
        if pos + 2 < len(data) and data[pos] == 0x78 and data[pos+1] in (0x01, 0x9C, 0xDA):
            try:
                d = zlib.decompressobj()
                text = d.decompress(data[pos:]).decode('utf-8', errors='replace')
                if 'flingarray' in text:
                    start = text.find('{', text.find('flingarray'))
                    depth, end = 0, start
                    for i, c in enumerate(text[start:], start):
                        if c == '{': depth += 1
                        elif c == '}':
                            depth -= 1
                            if depth == 0:
                                end = i + 1
                                break
                    block = text[start:end]
                    for m in re.finditer(r'(\d+)\s*=>\s*\[([^\]]+)\]', block):
                        power = int(m.group(1))
                        names = re.findall(r':(\w+)', m.group(2))
                        for name in names:
                            fling[name.upper()] = power
                    break
                pos += 1
            except:
                pos += 1
        else:
            pos += 1
    return fling

# ── Parse old v17 CSV items ───────────────────────────────────────────────────
def parse_old_items(path):
    items = []
    with open(path, encoding='utf-8-sig') as f:
        for raw in f:
            raw = raw.strip()
            if not raw or raw.startswith('#'):
                continue
            # Use csv reader to handle quoted description field
            row = next(csv.reader(io.StringIO(raw)))
            if len(row) < 8:
                continue
            try:
                int(row[0])
            except ValueError:
                continue
            items.append(row)
    return items

# ── Get existing names in new PBS ─────────────────────────────────────────────
def get_existing_names(path):
    names = set()
    with open(path, encoding='utf-8-sig') as f:
        for line in f:
            m = re.match(r'^\[(\w+)\]', line.strip())
            if m:
                names.add(m.group(1))
    return names

# ── Format one item entry ─────────────────────────────────────────────────────
def format_item(row, fling_map, seen_names):
    def g(i): return row[i].strip() if i < len(row) else ''

    item_id    = int(g(0))
    name       = g(1)
    display    = g(2)
    plural     = g(3)
    old_pocket = g(4)
    price      = g(5)
    desc       = g(6)
    field_use  = g(7)
    battle_use = g(8)
    category   = g(9)
    move_name  = g(10)  # for TMs/HMs

    if not name or name in seen_names:
        return None

    pocket = POCKET_MAP.get(int(old_pocket), int(old_pocket)) if old_pocket.isdigit() else 1

    # Build flags list
    flags = []
    cat_flags = CATEGORY_FLAGS.get(category, [])
    flags.extend(cat_flags)

    # KeyItem flag for pocket 8
    if old_pocket == '8':
        flags.append('KeyItem')

    # Repel flag
    if 'REPEL' in name.upper() and field_use == '2':
        flags.append('Repel')

    # Fling
    fling_power = fling_map.get(name.upper())
    if fling_power:
        flags.append(f'Fling_{fling_power}')

    lines = ['#-------------------------------', f'[{name}]']
    lines.append(f'Name = {display}')
    if plural and plural != display:
        lines.append(f'NamePlural = {plural}')

    lines.append(f'Pocket = {pocket}')

    if price and int(price) > 0:
        lines.append(f'Price = {int(price)}')

    fu = FIELD_USE.get(field_use)
    if fu:
        lines.append(f'FieldUse = {fu}')

    # BattleUse
    if battle_use == '1':
        lines.append('BattleUse = OnPokemon')
    elif battle_use == '2':
        # Balls → OnFoe; pocket-7 stat items → OnBattler; escape items → OnFoe
        if old_pocket == '7':
            lines.append('BattleUse = OnBattler')
        else:
            lines.append('BattleUse = OnFoe')
    elif battle_use == '3':
        lines.append('BattleUse = OnPokemon')

    if move_name and move_name.strip():
        lines.append(f'Move = {move_name.strip()}')

    if flags:
        lines.append(f'Flags = {",".join(flags)}')

    if desc:
        lines.append(f'Description = {desc}')

    return '\n'.join(lines)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print('Building fling map from v17 scripts...')
    fling_map = build_fling_map(SCRIPTS)
    print(f'  {len(fling_map)} items with fling data')

    print('Parsing old items PBS...')
    old_items = parse_old_items(OLD_PBS)
    print(f'  {len(old_items)} entries')

    print('Reading existing new PBS names...')
    existing = get_existing_names(NEW_PBS)
    print(f'  {len(existing)} items already in new PBS')

    sections = []
    skipped_existing = []
    skipped_ids = []

    for row in old_items:
        item_id = int(row[0].strip())
        name = row[1].strip() if len(row) > 1 else ''

        if item_id in SKIP_IDS:
            skipped_ids.append(f'  ID {item_id} ({name}) — in SKIP_IDS')
            continue

        if name in existing:
            skipped_existing.append(name)
            continue

        entry = format_item(row, fling_map, existing)
        if entry:
            sections.append(entry)
            existing.add(name)  # prevent dupes within old PBS

    # Append to new PBS
    with open(NEW_PBS, 'a', encoding='utf-8') as f:
        f.write('\n')
        f.write('\n'.join(sections))
        f.write('\n')

    print(f'\nAdded:            {len(sections)}')
    print(f'Skipped/existing: {len(skipped_existing)}')
    print(f'Skipped/IDs:      {len(skipped_ids)}')
    for s in skipped_ids:
        print(s)

    print('\nAdded items:')
    for s in sections:
        name_line = [l for l in s.split('\n') if l.startswith('[')][0]
        print(f'  {name_line}')

if __name__ == '__main__':
    main()
