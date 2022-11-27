import numpy
f=open("PBS/encounters.txt","r")
f2=open("encountersparsed.txt","w")
content=f.readlines()
content=[x.strip() for x in content]
content[0]="#--"
Enctypes=[
     "Land",
     "Cave",
     "Water",
     "RockSmash",
     "OldRod",
     "GoodRod",
     "SuperRod",
     "HeadbuttLow",
     "HeadbuttHigh",
     "LandMorning",
     "LandDay",
     "LandNight",
     "BugContest",
     "Rt1"]
EnctypeChances=[
     [10,10,10,10,10,10,10,10,5,5,4,4,1,1],
     [20,20,10,10,10,10,5,5,4,4,1,1],
     [30,30,20,18,2],
     [40,30,15,13,2],
     [90,10],
     [40,40,20],
     [40,30,15,13,2],
     [30,25,20,10,5,5,4,1],
     [30,25,20,10,5,5,4,1],
     [10,10,10,10,10,10,10,10,5,5,4,4,1,1],
     [10,10,10,10,10,10,10,10,5,5,4,4,1,1],
     [10,10,10,10,10,10,10,10,5,5,4,4,1,1],
     [20,20,10,10,10,10,5,5,4,4,1,1],
     [20,20,10,10,10,10,5,5,4,4,1,1]]
"""
with open ("PBS/encounters.txt", "r") as myfile:
    data = myfile.read().replace('\n', '')
    n = data.count('#--')
    
for i in numpy.arange(0,n):
    PB1=content.index("["+str(i+1)+"]")
    
    if i<n-1:
        
        PB2=content.index("["+str(i+2)+"]")
    else:
        PB2=len(content)
    enc=(content[PB1:PB2])
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


"""
for i in range(len(content)):
        if content[i][0:2]=='#-':
                print('yo',i,content[i][0:2])
                location=content[i+1].split("# ",1)[1]
                f2.write(location+'\n')
                j=i+4
                while content[j][0] !='#':
                        enctype=content[j-1]
                        f2.write('{| class="article-table"\n')
                        f2.write('|+ '+enctype+'\n')
                        f2.write('! Species !! Level !! Rate \n')
                        n=j
                        k=j
                        while (n<k+len(EnctypeChances[Enctypes.index(enctype)])) and j<len(content):
                                f2.write('|- \n')
                                print(content[n].split(','))
                                if len(content[n].split(','))==2:
                                        f2.write('|'+content[n].split(',')[0]+' || L'+content[n].split(',')[1]+' || '+str(EnctypeChances[Enctypes.index(enctype)][n-k])+'% \n')
                                elif len(content[n].split(','))==3:
                                        f2.write('|'+content[n].split(',')[0]+' || L'+content[n].split(',')[1]+'-'+content[n].split(',')[2]+' || '+str(EnctypeChances[Enctypes.index(enctype)][n-k])+'% \n')
                                n+=1
                                j+=1
                                
                        f2.write('|}\n')
                        if j<len(content) and content[j][0:2]!='#-':
                                j+=1
                        else:
                                break
       
f2.close()
f.close()

