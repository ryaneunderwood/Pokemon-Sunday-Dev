from PIL import Image,ImageFile
import os
directory='Graphics/Battlers/'
directory2=
folder=['Back/','BackShiny/','Back/Female/','BackShiny/Female/']
for f in folder:
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    for filename in os.listdir(directory+f):
        if filename.endswith(".png") or filename.endswith(".PNG"):
            try:
                image=Image.open(directory+f+filename)
                #print(directory+filename,' 2')
                if image.size[0]==192:
                    print(f+filename)
                    new_image=image.resize((2*image.size[0],1.5*image.size[1]), Image.NEAREST)
                    new_image.save(directory2+f+filename)
            except:
                print(f+filename, "failed to load image")
    
            
