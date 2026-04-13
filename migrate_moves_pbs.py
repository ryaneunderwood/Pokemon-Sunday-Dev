"""
Migrate custom moves from v17 PBS/moves.txt to v21.1 PBS/moves.txt.

Skips moves already in the new PBS.
Converts v17 CSV format to v21.1 key-value section format.

v17 CSV fields (0-indexed):
  0: id
  1: INTERNAL_NAME
  2: Display Name
  3: function_code  (hex string)
  4: base_power
  5: type
  6: category       (Physical / Special / Status)
  7: accuracy       (0 = never misses)
  8: pp
  9: effect_chance
 10: target_hex
 11: priority
 12: flags          (letter codes: see FLAG_MAP)
 13: description    (quoted)
"""

import csv
import io
import re

OLD_PBS = r'C:/Users/rucra/Documents/GitHub/Pokemon-Sunday-Dev/PBS/moves.txt'
NEW_PBS = r'C:/Users/rucra/Documents/GitHub/Pokemon-Sunday-3/PBS/moves.txt'

# ── Letter flag → v21.1 flag name ────────────────────────────────────────────
# 'c' (CanMagicCoat) and 'f' have no direct v21.1 equivalents — skipped.
FLAG_MAP = {
    'a': 'Contact',
    'b': 'CanProtect',
    'd': 'Dance',
    'e': 'CanMirrorMove',
    'g': 'Bomb',
    'h': 'HighCriticalHitRate',
    'i': 'Biting',
    'j': 'Punching',
    'k': 'Sound',
    'l': 'Powder',
    'm': 'Pulse',
    'n': 'Bomb',   # same as 'g' in v21.1
    'o': 'Slicing',
}

# ── Target hex → v21.1 target name ───────────────────────────────────────────
TARGET_MAP = {
    '00': 'NearOther',
    '01': 'NearAlly',
    '02': 'RandomNearFoe',
    '04': 'AllNearFoes',
    '08': 'AllBattlers',
    '10': 'User',
    '20': 'AllAllies',
    '40': 'UserOrNearAlly',
}

# ── Hex function code → v21.1 FunctionCode string ────────────────────────────
# Custom D-codes (D00-D06) that have no built-in v21.1 equivalent are mapped
# to their closest standard code but flagged as NEEDS_CUSTOM_SCRIPT below.
FUNC_MAP = {
    '000': 'None',
    '002': 'RecoilHalfOfDamageDealt',       # Struggle (will be skipped anyway)
    '007': 'ParalyzeTarget',
    '00A': 'BurnTarget',
    '00F': 'FlinchTarget',
    '010': 'FlinchTarget',
    '013': 'ConfuseTarget',
    '01F': 'RaiseUserSpeed1',
    '020': 'RaiseUserSpAtk1',
    '021': 'RaiseUserSpDef1',
    '029': 'RaiseUserAtkAcc1',
    '02A': 'RaiseUserDefSpDef1',
    '02B': 'RaiseUserSpAtkSpDefSpd1',
    '02D': 'RaiseUserMainStats1',
    '030': 'RaiseUserSpeed2',
    '032': 'RaiseUserSpAtk2',
    '039': 'RaiseUserSpAtk3',
    '03C': 'LowerUserDefSpDef1',
    '03E': 'LowerUserSpeed1',
    '03F': 'LowerUserSpAtk2',
    '040': 'ConfuseTarget',
    '042': 'LowerTargetAttack1',
    '043': 'LowerTargetDefense1',
    '044': 'LowerTargetSpeed1',
    '045': 'LowerTargetSpAtk1',
    '046': 'LowerTargetSpDef1',
    '047': 'LowerTargetAccuracy1',
    '04B': 'LowerTargetAttack2',
    '04D': 'LowerTargetSpeed2',
    '04F': 'LowerTargetSpDef2',
    '06C': 'FixedDamageHalfTargetHP',
    '070': 'OHKO',
    '092': 'PowerHigherWithConsecutiveUseOnUserSide',
    '0A5': 'None',         # never-miss is already expressed by Accuracy = 0
    '0BD': 'HitTwoTimes',
    '0BE': 'HitTwoTimesPoisonTarget',
    '0C0': 'HitTwoToFiveTimes',
    '0DD': 'HealUserByHalfOfDamageDone',
    '0E0': 'UserFaintsExplosive',
    '0E2': 'UserFaintsLowerTargetAtkSpAtk2',
    '0E7': 'AttackerFaintsIfUserFaints',
    '0FA': 'RecoilQuarterOfDamageDealt',
    '0FB': 'RecoilThirdOfDamageDealt',
    '0FD': 'RecoilThirdOfDamageDealt',
    '117': 'RedirectAllMovesToUser',
    '122': 'UseTargetDefenseInsteadOfTargetSpDef',
    '14E': 'TwoTurnAttackRaiseUserSpAtkSpDefSpd2',
    # Custom game-specific codes — nearest approximation used; Ruby implementation needed
    'D00': 'LowerTargetAccuracy1',          # PRISMSHOT: lowers acc + may confuse
    'D01': 'FailsIfNotUserFirstTurn',        # SUNRISE: priority, fails if not first turn
    'D02': 'AttackerFaintsIfUserFaints',     # SUNSET: countdown faint (custom)
    'D03': 'CureTargetStatusCondition',      # XRAYEYES: heals target's status
    'D05': 'StartLeechSeedTarget',           # SAPPYSEED: damage + leech seed
    'D06': 'TrapTargetInBattle',             # TERRAFIRMA: traps + ensures next hit
    'FFF': 'None',                           # Placeholder — needs custom Ruby
}

# Codes that need a custom Ruby script implementation
NEEDS_CUSTOM_SCRIPT = {'D00', 'D01', 'D02', 'D03', 'D05', 'D06', 'FFF'}

# Moves to skip entirely
SKIP_NAMES = {
    'STRUGGLE',  # Engine built-in; not defined in v21.1 PBS
}

# Moves that are likely placeholders / need manual review
REVIEW_NAMES = {
    'TERABLAST',  # Placeholder for gen9 Tera Blast — wrong type/power/desc in old PBS
    'ICEWALL',    # Custom move; FFF placeholder function code
}


def parse_old_moves(path):
    moves = []
    with open(path, encoding='utf-8-sig') as f:
        for raw in f:
            raw = raw.strip()
            if not raw or raw.startswith('#'):
                continue
            row = next(csv.reader(io.StringIO(raw)))
            if len(row) < 9:
                continue
            try:
                int(row[0])
            except ValueError:
                continue
            moves.append(row)
    return moves


def get_existing_names(path):
    names = set()
    with open(path, encoding='utf-8-sig') as f:
        for line in f:
            m = re.match(r'^\[(\w+)\]', line.strip())
            if m:
                names.add(m.group(1))
    return names


def convert_flags(flag_str):
    seen = set()
    result = []
    for ch in flag_str.strip():
        f = FLAG_MAP.get(ch)
        if f and f not in seen:
            seen.add(f)
            result.append(f)
    return result


def convert_target(target_hex):
    return TARGET_MAP.get(target_hex.strip().upper().zfill(2), 'NearOther')


def format_move(row):
    def g(i):
        return row[i].strip() if i < len(row) else ''

    name       = g(1)
    display    = g(2)
    func_code  = g(3).upper()
    power      = g(4)
    move_type  = g(5)
    category   = g(6)
    accuracy   = g(7)
    pp         = g(8)
    effect_pct = g(9)
    target_hex = g(10)
    priority   = g(11)
    flag_str   = g(12)
    desc       = g(13)

    func_name = FUNC_MAP.get(func_code, f'None  # TODO: unknown code {func_code}')
    target    = convert_target(target_hex)
    flags     = convert_flags(flag_str)

    lines = ['#-------------------------------', f'[{name}]']
    lines.append(f'Name = {display}')
    lines.append(f'Type = {move_type}')
    lines.append(f'Category = {category}')

    if power and int(power) > 0:
        lines.append(f'Power = {power}')

    if accuracy and int(accuracy) > 0:
        lines.append(f'Accuracy = {accuracy}')

    lines.append(f'TotalPP = {pp}')
    lines.append(f'Target = {target}')

    if priority and int(priority) != 0:
        lines.append(f'Priority = {priority}')

    lines.append(f'FunctionCode = {func_name}')

    if flags:
        lines.append(f'Flags = {",".join(flags)}')

    if effect_pct and int(effect_pct) > 0:
        lines.append(f'EffectChance = {effect_pct}')

    if desc:
        lines.append(f'Description = {desc}')

    return '\n'.join(lines)


def main():
    print('Parsing old moves...')
    old_moves = parse_old_moves(OLD_PBS)
    print(f'  {len(old_moves)} entries')

    print('Reading existing new PBS names...')
    existing = get_existing_names(NEW_PBS)
    print(f'  {len(existing)} moves already in new PBS')

    sections = []
    skipped_existing = []
    skipped_engine = []
    needs_review = []
    needs_custom_script = []

    for row in old_moves:
        name = row[1].strip()
        func_code = row[3].strip().upper()

        if name in SKIP_NAMES:
            skipped_engine.append(name)
            continue

        if name in existing:
            skipped_existing.append(name)
            continue

        entry = format_move(row)
        sections.append(entry)
        existing.add(name)

        if name in REVIEW_NAMES:
            needs_review.append(name)
        if func_code in NEEDS_CUSTOM_SCRIPT:
            needs_custom_script.append(f'{name} (code {func_code})')

    with open(NEW_PBS, 'a', encoding='utf-8') as f:
        f.write('\n')
        f.write('\n'.join(sections))
        f.write('\n')

    print(f'\nAdded:            {len(sections)}')
    print(f'Skipped/existing: {len(skipped_existing)}')
    print(f'Skipped/engine:   {len(skipped_engine)} ({", ".join(skipped_engine)})')

    print('\nAdded moves:')
    for s in sections:
        name_line = next(l for l in s.split('\n') if l.startswith('['))
        func_line = next((l for l in s.split('\n') if l.startswith('FunctionCode')), '')
        print(f'  {name_line}  {func_line}')

    if needs_review:
        print('\nNeeds manual review (placeholder function code or wrong data):')
        for n in needs_review:
            print(f'  {n}')

    if needs_custom_script:
        print('\nNeeds custom Ruby FunctionCode implementation:')
        for n in needs_custom_script:
            print(f'  {n}')
        print('  These use game-specific D-codes that do not exist in v21.1 Essentials.')
        print('  A closest standard FunctionCode was substituted — see list above.')


if __name__ == '__main__':
    main()
