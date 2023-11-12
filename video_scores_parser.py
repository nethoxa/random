import os
import numpy as np
import cv2
        
# Just cut the black edges
def cut(img):
    midcol = int(np.size(img, 1) / 2)
    midfil = int(np.size(img, 0) / 2)

    for i in range(midcol):
        if(img[10][i][0] != 0 and img[10][i][1] != 0 and img[10][i][2] != 0):
            crop = img[0:np.size(img, 0), i:np.size(img, 1) - i]
            break

    try:
        for i in range(midfil):
        
            if(crop[i][10][0] != 0 and crop[i][10][1] != 0 and crop[i][10][2] != 0):
                crop = crop[i:np.size(crop, 0) - i, 0:np.size(crop, 1)]
                return crop
    except:
        for i in range(midfil):
        
            if(img[i][10][0] != 0 and img[i][10][1] != 0 and img[i][10][2] != 0):
                crop = img[i:np.size(img, 0) - i, 0:np.size(img, 1)]
                return crop
            
    raise ZeroDivisionError()
        

# stupid minimum squared error between two images
def mse(img1: cv2.Mat, img2: cv2.Mat):
    h, w, k = img1.shape
    diff = cv2.subtract(img1, img2)
    err = np.sum(diff**2)
    mse = err/(float(h*w))
    return mse



def main():
    # videos = os.listdir(".\\videos") @todo after pytube download, just run this
    #os.mkdir(videos[_].split(".")[0])
    
    cam = cv2.VideoCapture(".\\kk.mp4") 
    os.chdir(".\\Takashi Yoshimatsu - Piano Concerto Memo Flora Op67 (wsheet)")  

        
    index = 81
    tiempos = []
    
    while(True):

        ret1,frame1 = cam.read()
    
        if ret1:
            
            _,frame2 = cam.read()
            
            try:
                while(mse(frame1, frame2) < 12 or mse(frame1, frame2) > 100):
                    _,frame2 = cam.read() 
                    
                err = mse(frame1, frame2)
                print(err)
                tiempos.append(err)
                cv2.imwrite(str(index) + '.jpg', cut(frame1))
                index += 1
                continue
            
            except ZeroDivisionError:
                continue
            
            except:
                cv2.imwrite(str(index) + '.jpg', cut(frame1))
                index += 1
                cam.release()
                cv2.destroyAllWindows()
                break

            
    os.chdir("..")


if __name__ == "__main__":
    main()