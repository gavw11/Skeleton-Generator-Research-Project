import cv2 as cv
import os

def createVid(skel_dir, vidName, frameCount, fps, width, height):

    print("-----------CREATING VIDEO------------")

    image_files = [os.path.join(skel_dir, f) for f in os.listdir(skel_dir)]
                   
    image_files.sort()

    video_writer = cv.VideoWriter(f"Output Videos\\{vidName}.avi", cv.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

    id = 1

    for files in image_files:

        Vpath = os.path.join(skel_dir, str(id) + "-skeleton.png")
    
        im0 = cv.imread(Vpath)

        video_writer.write(im0)

        print(f"VIDEO FRAME: {id}/{frameCount}")

        id+=1


    video_writer.release()
    cv.destroyAllWindows()
    
