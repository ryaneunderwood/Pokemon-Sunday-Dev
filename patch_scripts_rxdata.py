"""
Patches Scripts.rxdata to fix the typo :CINERITE -> :CINDERITE in the flingarray.

The scripts file is Ruby Marshal format: an array of [id, name, zlib_data] triples.
We find the relevant zlib stream, decompress, patch, recompress, and update the
Marshal string length prefix in the binary.
"""

import zlib
import shutil
import os

SCRIPTS_PATH = r'C:/Users/rucra/Documents/GitHub/Pokemon-Sunday-Dev/Data/Scripts.rxdata'
BACKUP_PATH  = SCRIPTS_PATH + '.bak'

OLD_TEXT = b':CINERITE'
NEW_TEXT = b':CINDERITE'


def marshal_encode_int(n):
    """Encode a non-negative integer as Ruby Marshal compact integer bytes."""
    if n == 0:
        return bytes([0])
    elif 1 <= n <= 122:
        return bytes([n + 5])
    elif n <= 255:
        return bytes([0x01, n & 0xff])
    elif n <= 65535:
        return bytes([0x02, n & 0xff, (n >> 8) & 0xff])
    elif n <= 16777215:
        return bytes([0x03, n & 0xff, (n >> 8) & 0xff, (n >> 16) & 0xff])
    else:
        return bytes([0x04, n & 0xff, (n >> 8) & 0xff, (n >> 16) & 0xff, (n >> 24) & 0xff])


def marshal_decode_int_at(data, pos):
    """Decode Ruby Marshal compact integer at pos. Returns (value, bytes_consumed)."""
    b = data[pos]
    if b == 0:
        return 0, 1
    elif b <= 4:
        # b bytes follow, little-endian
        n = 0
        for i in range(b):
            n |= data[pos + 1 + i] << (8 * i)
        return n, 1 + b
    elif b >= 0xfc:  # negative, b bytes of negative
        count = 256 - b
        n = -1
        for i in range(count):
            n &= ~(0xff << (8 * i))
            n |= data[pos + 1 + i] << (8 * i)
        return n, 1 + count
    elif b >= 0x80:
        return b - 256 - 5, 1  # small negative
    else:
        return b - 5, 1  # small positive (b >= 6)


def find_and_patch(data):
    pos = 0
    while pos < len(data):
        if pos + 2 < len(data) and data[pos] == 0x78 and data[pos+1] in (0x01, 0x9C, 0xDA):
            try:
                d = zlib.decompressobj()
                decompressed = d.decompress(data[pos:])
                unused = d.unused_data
                compressed_size = len(data[pos:]) - len(unused)

                if OLD_TEXT in decompressed:
                    print(f"Found target script at byte offset {pos}")
                    print(f"  Compressed size:   {compressed_size}")
                    print(f"  Decompressed size: {len(decompressed)}")

                    # Verify the length prefix is right before us
                    # Format: 0x22 ('"') + marshal_int(compressed_size) + compressed_data
                    # Find the 0x22 byte before pos
                    quote_pos = None
                    for lookback in range(1, 10):
                        if data[pos - lookback] == 0x22:
                            # Check if the marshal int after it encodes compressed_size
                            val, consumed = marshal_decode_int_at(data, pos - lookback + 1)
                            if val == compressed_size and (pos - lookback + 1 + consumed) == pos:
                                quote_pos = pos - lookback
                                len_start = pos - lookback + 1
                                len_bytes = consumed
                                break

                    if quote_pos is None:
                        print("ERROR: Could not locate Marshal length prefix. Aborting.")
                        return None

                    print(f"  Marshal string starts at: {quote_pos}")
                    print(f"  Length prefix at {len_start}, {len_bytes} byte(s)")

                    # Patch the decompressed script
                    count = decompressed.count(OLD_TEXT)
                    patched = decompressed.replace(OLD_TEXT, NEW_TEXT)
                    print(f"  Replaced {count} occurrence(s) of {OLD_TEXT} -> {NEW_TEXT}")

                    # Recompress at same level RPGMaker uses (default = 6)
                    new_compressed = zlib.compress(patched, 6)
                    new_compressed_size = len(new_compressed)
                    print(f"  New compressed size: {new_compressed_size}")

                    # Build new length prefix
                    new_len_bytes = marshal_encode_int(new_compressed_size)
                    print(f"  Old length encoding: {data[len_start:len_start+len_bytes].hex()}")
                    print(f"  New length encoding: {new_len_bytes.hex()}")

                    # Assemble patched file
                    # Everything before the quote byte + quote + new_len + new_compressed + everything after
                    end_of_old = pos + compressed_size
                    new_data = (
                        data[:quote_pos]          # everything before the string
                        + b'\x22'                 # string type byte
                        + new_len_bytes           # new length
                        + new_compressed          # new compressed data
                        + data[end_of_old:]       # rest of file
                    )

                    size_delta = len(new_data) - len(data)
                    print(f"  File size delta: {size_delta:+d} bytes")
                    return new_data

                pos += 1
            except Exception as e:
                pos += 1
        else:
            pos += 1

    print("ERROR: Target script not found.")
    return None


def main():
    print(f"Reading {SCRIPTS_PATH}")
    with open(SCRIPTS_PATH, 'rb') as f:
        data = f.read()
    print(f"File size: {len(data)} bytes")

    if OLD_TEXT not in data:
        print(f"'{OLD_TEXT}' not found in raw file (may already be compressed). Scanning...")

    # Backup first
    if not os.path.exists(BACKUP_PATH):
        shutil.copy2(SCRIPTS_PATH, BACKUP_PATH)
        print(f"Backup created: {BACKUP_PATH}")
    else:
        print(f"Backup already exists: {BACKUP_PATH}")

    patched = find_and_patch(data)
    if patched is None:
        print("Patch failed. Original file untouched.")
        return

    with open(SCRIPTS_PATH, 'wb') as f:
        f.write(patched)
    print(f"\nPatched file written: {SCRIPTS_PATH}")
    print("Done.")


if __name__ == '__main__':
    main()
