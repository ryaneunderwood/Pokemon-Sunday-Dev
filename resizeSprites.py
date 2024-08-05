from PIL import Image,ImageFile
import os
directory='Graphics/Battlers/'
folder=['./']#['Back/','BackShiny/','Front/','FrontShiny/','Back/Female/','BackShiny/Female/','Front/Female/','FrontShiny/Female/']
for f in folder:
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    for filename in os.listdir(directory+f):
        if filename.endswith(".png") or filename.endswith(".PNG"):
            try:
                image=Image.open(directory+f+filename)
                #print(directory+filename,' 2')
                if image.size[0]==288:
                    print(f+filename)
                    new_image=image.resize((1/3*image.size[0],1/3*image.size[1]), Image.NEAREST)
                    new_image=new_image.resize((2*new_image.size[0],2*new_image.size[1]), Image.NEAREST)
                    new_image.save(directory+f+filename)
            except:
                print(f+filename, "failed to load image")
                image=Image.open(directory+f+filename)
                image.show()
            
