import numpy
f=open("PBS/pokemon.txt","r")
f3=open("PBS/pokemonforms.txt","r")
f2=open("pokesparsed.txt","w")
content=f.readlines()
content=[x.strip() for x in content]
content[0]="[1]"
content3=f3.readlines()
content3=[x.strip() for x in content3]
content3[0]="#--"
with open ("PBS/pokemon.txt", "r") as myfile:
    data = myfile.read().replace('\n', '')
    n = data.count('#')

with open ("PBS/pokemonforms.txt", "r") as myfile:
    data = myfile.read().replace('\n', '')
    n2 = data.count('#')
    
for i in numpy.arange(0,n):
    PB1=content.index("["+str(i+1)+"]")
    
    if i<n-1:
        
        PB2=content.index("["+str(i+2)+"]")
    else:
        PB2=len(content)
    poke=(content[PB1:PB2])
    for j in poke:
        if j[0:5]=="Name=":
            f2.write("#"+str(i+1)+"\n"+j[5:]+"\n")
        if j[0:5]=="Type1":
            f2.write("Type 1: "+j[6:] +"\n")
        if j[0:5]=="Type2":
            f2.write("Type 2: "+j[6:] +"\n")
        if j[0:5]=="BaseS":
            k=j.split(',')
            k0=k[0]
            k0=k0[10:]
            k[0]=k0
            f2.write("\nStats:\n"+"HP: "+k[0]+"\n"+"Attack: "+k[1]+"\n"+"Defense: "+k[2]+"\n"+"Sp. Attack: "+k[4]+"\n"+"Sp. Def: "+k[5]+"\n"+"Speed: "+k[3]+"\n")

        if j[0:5]=="Moves":
            k=j.split(',')
            k0=k[0]
            k0=k0[6:]
            k[0]=k0
            f2.write("\nMoves:\n")
            for ii in numpy.arange(0,len(k)/2):
                f2.write("L"+k[2*int(ii)]+" "+k[2*int(ii)+1]+"\n")
        if j[0:5]=="Compa":
            f2.write("\nEgg Groups: "+j[14:]+"\n\n")
        if j[0:5]=="EggMo":
            k=j.split(',')
            k0=k[0]
            k0=k0[9:]
            k[0]=k0
            f2.write("\nEgg Moves:\n")
            for ii in numpy.arange(0,len(k)):
                f2.write(k[int(ii)]+"\n")
            
            
        if j[0:5]=="Abili":
            f2.write("\nAbilities: "+j[10:]+"\n")
        if j[0:5]=="Hidde":
            f2.write("Hidden Ability: "+j[14:]+"\n")
        if (j[0:5]=="Evolu") & (len(j)>12):
            f2.write("Evolutions: "+j[11:]+"\n")
            f2.write("\n\n")

with open("PBS/pokemonforms.txt", "r") as a_file:

  for line in a_file:

    j = line.strip()

    if j[0]=="[":
        f2.write("\n\n-----------------\n")
        f2.write(j[1:-3]+"\n")
    if j[0:5]=="FormN":
        f2.write("Form Name: "+j[9:] +"\n")    
    if j[0:5]=="Type1":
        f2.write("Type 1: "+j[6:] +"\n")
    if j[0:5]=="Type2":
        f2.write("Type 2: "+j[6:] +"\n")
    if j[0:5]=="BaseS":
        k=j.split(',')
        k0=k[0]
        k0=k0[10:]
        k[0]=k0
        f2.write("\nStats:\n"+"HP: "+k[0]+"\n"+"Attack: "+k[1]+"\n"+"Defense: "+k[2]+"\n"+"Sp. Attack: "+k[4]+"\n"+"Sp. Def: "+k[5]+"\n"+"Speed: "+k[3]+"\n")

    if j[0:5]=="Moves":
        k=j.split(',')
        k0=k[0]
        k0=k0[6:]
        k[0]=k0
        f2.write("\nMoves:\n")
        for ii in numpy.arange(0,len(k)/2):
            f2.write("L"+k[2*int(ii)]+" "+k[2*int(ii)+1]+"\n")
        f2.write("\n")

    if j[0:5]=="EggMo":
        k=j.split(',')
        k0=k[0]
        k0=k0[9:]
        k[0]=k0
        f2.write("Egg Moves:\n")
        for ii in numpy.arange(0,len(k)):
            f2.write(k[int(ii)]+"\n")
        f2.write("\n")

    if j[0:5]=="Abili":
        f2.write("\nAbilities: "+j[10:]+"\n")
    if j[0:5]=="Hidde":
        f2.write("Hidden Ability: "+j[14:]+"\n")
    if (j[0:5]=="Evolu") & (len(j)>12):
        f2.write("Evolutions: "+j[11:]+"\n")
        
        
    
       
f2.close()
f.close()
f3.close()    
