import numpy as np,json
from PIL import Image
from scipy.ndimage import map_coordinates
im=np.asarray(Image.open('/home/user/work/photos/picks/stage-1.jpg').convert('RGB')).astype(float); H,W,_=im.shape
k=json.load(open('kp.json'))
mid=lambda a,b:((a[0]+b[0])/2,(a[1]+b[1])/2)
C=[(mid(k['lsh'],k['lel']),26,0.20),(mid(k['rsh'],k['rel']),26,0.20),(mid(k['lel'],k['lwr']),22,0.14),(mid(k['rel'],k['rwr']),22,0.14)]
yy,xx=np.mgrid[0:H,0:W].astype(float); sx,sy=xx.copy(),yy.copy()
for (cx,cy),r,s in C:
    dx,dy=xx-cx,yy-cy; d=np.sqrt(dx*dx+dy*dy); t=np.clip(d/r,0,1); f=1-s*(1-t*t)**2
    m=d<r; sx[m]=cx+dx[m]*f[m]; sy[m]=cy+dy[m]*f[m]
out=np.stack([map_coordinates(im[:,:,c],[sy,sx],order=3,mode='nearest') for c in range(3)],-1)
Image.fromarray(np.clip(out,0,255).astype(np.uint8)).save('stage1_bulge.jpg',quality=97)
