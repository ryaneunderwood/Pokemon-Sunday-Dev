from PIL import Image,ImageFile
import os
directory='Graphics/' #/Battlers/'
folder=['Icons/']#['Back/','BackShiny/','Front/','FrontShiny/']
for f in folder:
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    for filename in os.listdir(directory+f):
        if filename.startswith("roam"): #endswith(".png"):
            try:
                image=Image.open(directory+f+filename)
                #print(directory+filename,' 2')
                if image.size[0]==64:
                    print(f+filename)
                    new_image=image.resize((0.5*image.size[0],0.5*image.size[1]), Image.NEAREST)
                    new_image.save(directory+f+filename)
            except:
                print(f+filename, "failed to load image")
    
            
