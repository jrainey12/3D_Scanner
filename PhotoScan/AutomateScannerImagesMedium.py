import os
from PhotoScan import *

doc = PhotoScan.app.document

chunk = doc.addChunk()
chunk.label = "Camera Still Chunk"

main_path = app.getExistingDirectory("Specify Folder containing images.")


project_path = app.getSaveFileName("Specify project filename for saving:")
if not project_path:
    print("Script aborted")
    
if project_path[-4:].lower() != ".psz":
    project_path += ".psz"
    
#Add Images      
effectiveimage_list = []
image_list = os.listdir(main_path)

for image in image_list:
		#if image.rsplit(".", 1)[1].upper() != "JPEG":
		#	image_list.remove(image)
		effectiveimage_list.append(main_path + "/" + image)
		
		
chunk.addPhotos(effectiveimage_list)
		

#Match and Align Photos
chunk.matchPhotos(accuracy = MediumAccuracy, preselection = NoPreselection, filter_mask=False, keypoint_limit=50000, tiepoint_limit=4000) 
chunk.alignCameras()             

#build dense cloud
chunk.buildDenseCloud(quality=MediumQuality, filter=AggressiveFiltering)

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
	

