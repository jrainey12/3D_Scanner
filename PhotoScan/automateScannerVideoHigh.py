import os
from PhotoScan import *

doc = PhotoScan.app.document

chunk = doc.addChunk()
chunk.label = "MultiFrame Chunk"

main_path = app.getExistingDirectory("Specify Folder containing images subfolders.")
main_path+= "/"

project_path = app.getSaveFileName("Specify project filename for saving:")
if not project_path:
    print("Script aborted")
    
if project_path[-4:].lower() != ".psz":
    project_path += ".psz"
    
#Add Images      
paths = os.listdir(main_path)

for x in range(1, 19):
	chunk.addFrame()

image_paths = list()

for p in paths:
	if os.path.isdir(main_path + p):
		#paths.remove(p)
		image_paths.append(p)

image_paths.sort()
		
for p in image_paths:
	print(p)
	#os.chdir(main_path + p)	
	image_list = os.listdir(main_path + p)
	effectiveimage_list = []
	
		
	for image in image_list:
		if image.rsplit(".", 1)[1].upper() != "PNG":
			image_list.remove(image)
		effectiveimage_list.append(main_path + p + "/" + image)
		
	effectiveimage_list.sort()
		
	chunk.addPhotos([effectiveimage_list[0]])
	
	
	num = image_paths.index(p)	
	
		
	for x in range(1, len(effectiveimage_list)):
		
		chunk.cameras[num].frames[x].open(effectiveimage_list[x])
	
	#for y in effectiveimage_list:
	#	if y .endswith(".png"):
	#		f.open(y)
		

#Match and Align Photos
chunk.matchPhotos(accuracy = HighestAccuracy, preselection = NoPreselection, filter_mask=False, keypoint_limit=50000, tiepoint_limit=4000) 
chunk.alignCameras()             

#build dense cloud
chunk.buildDenseCloud(quality=HighQuality, filter=AggressiveFiltering)

#build mesh
chunk.buildModel(surface=Arbitrary, interpolation=EnabledInterpolation)

#build texture
chunk.buildUV(mapping=GenericMapping)
chunk.buildTexture(blending=MosaicBlending, size=4096)

#save
if not doc.save(project_path):
    app.messageBox("Can't save project!")

app.update()
print("Script finished")	
	
