out = []
with open("pokemon.txt", encoding="utf-8") as f:
    lines = f.readlines()

num, name = None, None
for line in lines:
    line = line.strip()
    if line.startswith('[') and line.endswith(']'):
        num = int(line[1:-1])
    elif line.startswith("InternalName="):
        name = line.split("=",1)[1]
        if 921 <= num <= 1040:
            out.append(f"[{num},{name}]")

with open("output.txt","w",encoding="utf-8") as f:
    f.write("\n".join(out))