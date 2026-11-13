import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from skimage import exposure
src=Image.open('orig/o.png').convert('RGB')
tgt=Image.open('/tmp/claude-0/-home-user-content-management/4429a793-2fa7-5e8d-8b75-1d73799d6b30/images/5.webp').convert('RGBA')
import sys
(sx1,sy1,sx2,sy2,tx1,ty1,tx2,ty2,rx,ry,dy)=map(float,sys.argv[1:12])
s=np.hypot(tx2-tx1,ty2-ty1)/np.hypot(sx2-sx1,sy2-sy1)
ang=np.degrees(np.arctan2(ty2-ty1,tx2-tx1)-np.arctan2(sy2-sy1,sx2-sx1))
big=src.resize((round(src.width*s),round(src.height*s)),Image.LANCZOS)
smx,smy=(sx1+sx2)/2*s,(sy1+sy2)/2*s; tmx,tmy=(tx1+tx2)/2,(ty1+ty2)/2
big=big.rotate(-ang,center=(smx,smy),resample=Image.BICUBIC)
canvas=Image.new('RGB',tgt.size); canvas.paste(big,(round(tmx-smx),round(tmy-smy)))
m=Image.new('L',tgt.size,0); d=ImageDraw.Draw(m); cx,cy=tmx,tmy+dy; d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=255); m=m.filter(ImageFilter.GaussianBlur(14))
T=np.array(tgt.convert('RGB')).astype(float); Cv=np.array(canvas).astype(float); M=np.array(m).astype(float)[...,None]/255
core=M[...,0]>0.6
for c in range(3):  # match colour stats inside the face
    a=Cv[...,c][core]; b=T[...,c][core]; Cv[...,c]=(Cv[...,c]-a.mean())/(a.std()+1e-6)*b.std()+b.mean()
out=T*(1-M)+Cv*M
al=np.array(tgt)[...,3]
res=np.dstack([np.clip(out,0,255),al]).astype('uint8'); Image.fromarray(res,'RGBA').save('new6_color.png')
a=res.astype(float)/255; rgb=a[...,:3]
g=(0.299*rgb[...,0]+0.587*rgb[...,1]+0.114*rgb[...,2])**1.2
c=exposure.equalize_adapthist(g,clip_limit=0.01); g=g*0.6+c*0.4
hi=g>0.62; g[hi]=0.62+(g[hi]-0.62)*0.42
Image.fromarray((np.clip(np.dstack([g,g,g,a[...,3]]),0,1)*255).astype('uint8'),'RGBA').save('new6_bw.png')
Image.open('new6_bw.png').crop((700,0,1000,300)).resize((400,400)).save('/tmp/claude-0/-home-user-content-management/4429a793-2fa7-5e8d-8b75-1d73799d6b30/scratchpad/f6.png')
print('scale',s,'angle',ang)
