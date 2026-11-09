# sheet.py base.mp4 ovdir out.jpg cols scale : composite test overlay frames on base frames and tile
import sys,os,subprocess
from PIL import Image
base,ov,out=sys.argv[1:4];cols=int(sys.argv[4]);sc=float(sys.argv[5])
fs=sorted(f for f in os.listdir(ov) if f.endswith('.png'));ims=[]
for f in fs:
  i=int(f[:4]);t=i/30;tmp='/tmp/_bf.png'
  subprocess.run(['ffmpeg','-v','error','-y','-ss',str(min(t,float(sys.argv[6]) if len(sys.argv)>6 else t)),'-i',base,'-frames:v','1',tmp])
  b=Image.open(tmp).convert('RGBA');o=Image.open(os.path.join(ov,f)).convert('RGBA');b=b.resize(o.size);b.alpha_composite(o)
  b=b.convert('RGB').resize((int(o.size[0]*sc),int(o.size[1]*sc)));ims.append((b,f))
w,h=ims[0][0].size;rows=(len(ims)+cols-1)//cols;S=Image.new('RGB',(w*cols,h*rows))
from PIL import ImageDraw;d=ImageDraw.Draw(S)
for k,(im,f) in enumerate(ims):S.paste(im,((k%cols)*w,(k//cols)*h));d.text(((k%cols)*w+6,(k//cols)*h+4),f"{int(f[:4])/30:.1f}s",fill=(255,255,0))
S.save(out,quality=80)
