import torch,torchvision,numpy as np,sys
from PIL import Image,ImageFilter
from torchvision.models.segmentation import deeplabv3_mobilenet_v3_large, DeepLabV3_MobileNet_V3_Large_Weights
w=DeepLabV3_MobileNet_V3_Large_Weights.DEFAULT; m=deeplabv3_mobilenet_v3_large(weights=w).eval()
for src,out in [(a.split('=')[0],a.split('=')[1]) for a in sys.argv[1:]]:
    im=Image.open(src).convert('RGB'); W,H=im.size
    x=w.transforms()(im).unsqueeze(0)
    with torch.no_grad(): o=m(x)['out'][0]
    p=torch.softmax(o,0)[15].numpy()  # person
    mask=Image.fromarray((p*255).astype(np.uint8)).resize((W,H),Image.BILINEAR).point(lambda v:255 if v>140 else (0 if v<90 else v))
    mask=mask.filter(ImageFilter.GaussianBlur(1.2))
    g=im.convert('L').convert('RGB'); rgba=g.convert('RGBA'); rgba.putalpha(mask); rgba.save(out)
    print(out,W,H)
