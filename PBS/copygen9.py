import os, shutil, glob

base_in = os.path.expanduser("~/Downloads/Gen9/Graphics/Pokemon")
base_out = os.path.expanduser("~/Documents/GitHub/Pokemon-Sunday-Dev/Graphics/Battlers")

with open("output.txt", encoding="utf-8") as f:
    entries = [line.strip().strip("[]") for line in f if line.strip()]

for line in entries:
    num, name = line.split(",", 1)
    for view in ["Front", "Back","FrontShiny","BackShiny"]:
        src_dir = os.path.join(base_in, view)
        dst_dir = os.path.join(base_out, view)
        os.makedirs(dst_dir, exist_ok=True)

        # match all possible variants: NAME.png, NAME_1.png, NAME_2.png, etc.
        pattern = os.path.join(src_dir, f"{name}*.png")
        for src in glob.glob(pattern):
            suffix = src[len(src_dir) + 1 + len(name):-4]  # captures '', '_1', '_2', etc.
            dst = os.path.join(dst_dir, f"{num}{suffix}.png")
            shutil.copy2(src, dst)
            print(f"Copied {src} → {dst}")