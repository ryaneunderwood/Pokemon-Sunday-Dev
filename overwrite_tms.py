"""
Replace all TM entries in the new v21.1 items.txt with TMs from the old v17 items.txt.

- Removes all [TMxx] sections from the new PBS
- Converts old CSV TM entries (pocket=4) to v21.1 format
- Looks up each move's base power from the new moves.txt to set Fling_X flag
- HMs (field_use=4 in old) get FieldUse = HM instead of TR
"""

import csv
import io
import re

OLD_PBS   = r'C:/Users/rucra/Documents/GitHub/Pokemon-Sunday-Dev/PBS/items.txt'
NEW_PBS   = r'C:/Users/rucra/Documents/GitHub/Pokemon-Sunday-3/PBS/items.txt'
MOVES_PBS = r'C:/Users/rucra/Documents/GitHub/Pokemon-Sunday-3/PBS/moves.txt'


def parse_move_powers(path):
    """Return dict {MOVENAME: base_power} from v21.1 moves.txt."""
    powers = {}
    current = None
    with open(path, encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            m = re.match(r'^\[(\w+)\]', line)
            if m:
                current = m.group(1)
            elif current and line.startswith('Power ='):
                try:
                    powers[current] = int(line.split('=', 1)[1].strip())
                except ValueError:
                    pass
    return powers


def parse_old_tms(path):
    """Return list of row dicts for all pocket-4 items from old v17 CSV."""
    tms = []
    with open(path, encoding='utf-8-sig') as f:
        for raw in f:
            raw = raw.strip()
            if not raw or raw.startswith('#'):
                continue
            row = next(csv.reader(io.StringIO(raw)))
            if len(row) < 8:
                continue
            try:
                int(row[0])
            except ValueError:
                continue
            if row[4].strip() == '4':  # pocket 4 = TMs/HMs
                tms.append(row)
    return tms


def remove_tm_sections(text):
    """Remove all [TMxx] sections from the PBS text."""
    # Split into sections, drop any whose header matches [TM<digits>]
    parts = re.split(r'(?=^#-+\s*\n^\[TM\d+\])', text, flags=re.MULTILINE)
    # Also handle sections without a separator line before them
    cleaned = []
    section_re = re.compile(r'^\[TM\d+\]', re.MULTILINE)
    # Rebuild: split on any [TMxx] header block
    result = re.split(r'(?:^#-+\n)?^\[TM\d+\][^\[]*', text, flags=re.MULTILINE | re.DOTALL)
    return ''.join(result)


def format_tm(row, move_powers):
    def g(i): return row[i].strip() if i < len(row) else ''

    name      = g(1)
    display   = g(2)
    plural    = g(3)
    price     = g(5)
    desc      = g(6)
    field_use = g(7)  # 3=TR, 4=HM
    move_name = g(10)

    fu = 'HM' if field_use == '4' else 'TR'

    # Fling = move base power (capped at 150)
    power = move_powers.get(move_name.upper(), 0)
    fling = f'Fling_{min(power, 150)}' if power > 0 else None

    lines = ['#-------------------------------', f'[{name}]']
    lines.append(f'Name = {display}')
    if plural and plural != display:
        lines.append(f'NamePlural = {plural}')
    lines.append('Pocket = 4')
    if price and int(price) > 0:
        lines.append(f'Price = {int(price)}')
    lines.append(f'FieldUse = {fu}')
    if fling:
        lines.append(f'Flags = {fling}')
    if move_name:
        lines.append(f'Move = {move_name}')
    if desc:
        lines.append(f'Description = {desc}')

    return '\n'.join(lines)


def main():
    print('Parsing move powers from new moves.txt...')
    move_powers = parse_move_powers(MOVES_PBS)
    print(f'  {len(move_powers)} moves with power data')

    print('Parsing old TMs...')
    old_tms = parse_old_tms(OLD_PBS)
    print(f'  {len(old_tms)} TM/HM entries found')

    print('Reading new PBS...')
    with open(NEW_PBS, encoding='utf-8-sig') as f:
        content = f.read()

    # Count existing TMs before removal
    existing_count = len(re.findall(r'^\[TM\d+\]', content, re.MULTILINE))
    print(f'  {existing_count} existing [TMxx] sections to remove')

    # Remove all existing TM sections
    cleaned = remove_tm_sections(content)
    removed_count = len(re.findall(r'^\[TM\d+\]', cleaned, re.MULTILINE))
    print(f'  {removed_count} remaining after removal (should be 0)')

    # Format all old TMs as v21.1 entries
    new_sections = [format_tm(row, move_powers) for row in old_tms]

    # Append to cleaned PBS
    final = cleaned.rstrip('\n') + '\n\n' + '\n'.join(new_sections) + '\n'

    with open(NEW_PBS, 'w', encoding='utf-8') as f:
        f.write(final)

    print(f'\nDone. Replaced {existing_count} old TMs with {len(new_sections)} from old project.')

    print('\nTM list:')
    for row in old_tms:
        fu = 'HM' if row[7].strip() == '4' else 'TM'
        print(f'  [{row[1].strip()}] {fu} -> {row[10].strip() if len(row) > 10 else "?"}')


if __name__ == '__main__':
    main()
