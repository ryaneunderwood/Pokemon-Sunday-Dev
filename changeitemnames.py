import os
import re

# Dictionary mapping item names to their new numbers
item_numbers = {
    "AUSPICIOUSARMOR": "1438",
    "MALICIOUSARMOR": "1439",
    "SCROLLOFDARKNESS": "1440",
    "SCROLLOFWATERS": "1441",
    "LEADERSCREST": "1442",
    "BOOSTERENERGY": "1443",
    "ABILITYSHIELD": "1444",
    "CLEARAMULET": "1445",
    "MIRRORHERB": "1446",
    "PUNCHINGGLOVE": "1447",
    "COVERTCLOAK": "1448",
    "LOADEDDICE": "1449",
    "GIMMIGHOULCOIN": "1450",
    "TINYBAMBOOSHOOT": "1451",
    "BIGBAMBOOSHOOT": "1452",
    "FAIRYFEATHER": "1453",
    "SYRUPYAPPLE": "1454",
    "UNREMARKABLETEACUP": "1455",
    "MASTERPIECETEACUP": "1456",
    "WELLSPRINGMASK": "1457",
    "HEARTHFLAMEMASK": "1458",
    "CORNERSTONEMASK": "1459",
    "TEALMASK": "1460",
    "METALALLOY": "1461"
}

# Folder containing the PNG files
folder_path = r"C:\Users\rucra\Downloads\Generation 9 Pack v3.2.1\Graphics\Items"

# Function to extract the item name from the filename
def extract_item_name(filename):
    # This regex pattern looks for the item name without requiring "item" prefix
    match = re.search(r'(\w+)\.png', filename, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None

print(f"Searching for PNG files in: {folder_path}")

# Iterate through all files in the folder
for filename in os.listdir(folder_path):
    print(f"Examining file: {filename}")
    if filename.lower().endswith(".png"):
        item_name = extract_item_name(filename)
        print(f"  Extracted item name: {item_name}")
        if item_name:
            if item_name in item_numbers:
                new_number = item_numbers[item_name]
                new_filename = f"item{new_number}.png"
                old_path = os.path.join(folder_path, filename)
                new_path = os.path.join(folder_path, new_filename)
                
                # Rename the file
                os.rename(old_path, new_path)
                print(f"  Renamed {filename} to {new_filename}")
            else:
                print(f"  Skipped {filename} - item name not in the dictionary")
        else:
            print(f"  Skipped {filename} - could not extract item name")
    else:
        print(f"  Skipped {filename} - not a PNG file")

print("Renaming complete!")